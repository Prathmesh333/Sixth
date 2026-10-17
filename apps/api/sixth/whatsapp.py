"""Opt-in, signed WhatsApp channel. Live sending is separately gated.

One background worker per API process; deploy a single worker/instance.
Phone possession is proved by a signed inbound message, never a typed number.
"""

import hashlib
import hmac
import json
import logging
import re
import secrets
import time
from threading import Event, RLock, Thread
from typing import Literal
from urllib.parse import quote

import httpx
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from .models import now
from .tasks import submit_message

SYSTEM = "__whatsapp__"
logger = logging.getLogger(__name__)


class LinkInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phone: str = Field(pattern=r"^\+[1-9][0-9]{7,14}$")
    consent: Literal[True]


class WhatsApp:
    def __init__(self, store, runtime, settings):
        self.store, self.runtime, self.settings = store, runtime, settings
        self.lock, self.stop_event, self.thread = RLock(), Event(), None
        self.cipher = None
        if settings.whatsapp_enabled:
            required = [settings.whatsapp_app_secret, settings.whatsapp_verify_token,
                        settings.whatsapp_phone_number_id, settings.whatsapp_business_number,
                        settings.whatsapp_encryption_key, settings.whatsapp_identity_secret,
                        settings.whatsapp_allowed_numbers]
            if not all(required):
                raise ValueError("WhatsApp requires configured webhook, number and encryption settings")
            self.cipher = Fernet(settings.whatsapp_encryption_key.encode())
            if not re.fullmatch(r"[1-9][0-9]{7,14}", settings.whatsapp_business_number):
                raise ValueError("WhatsApp business number must contain international digits only")
            if settings.public_url.rstrip("/") not in settings.allowed_origins:
                raise ValueError("WhatsApp public URL must match an allowed web origin")
            if settings.whatsapp_send_enabled and (
                not settings.whatsapp_access_token or not re.fullmatch(r"v\d+\.\d+", settings.whatsapp_api_version)
            ):
                raise ValueError("Live WhatsApp sending requires an access token and explicit API version")

    def digest(self, value):
        return hmac.new(self.settings.whatsapp_identity_secret.encode(), value.encode(), hashlib.sha256).hexdigest()

    def seal(self, value):
        return self.cipher.encrypt(json.dumps(value).encode()).decode()

    def unseal(self, value):
        return json.loads(self.cipher.decrypt(value.encode()))

    def require_enabled(self):
        if not self.settings.whatsapp_enabled:
            raise HTTPException(503, "WhatsApp is not configured yet")

    def start(self):
        if not self.settings.whatsapp_enabled:
            return
        # Reconcile ambiguous sends instead of blindly sending a second copy.
        for item in self.store.list(SYSTEM, "wa_outbox"):
            if item["status"] == "sending":
                self.store.put(SYSTEM, "wa_outbox", {**item, "status": "uncertain"})
        self.thread = Thread(target=self.loop, name="sixth-whatsapp", daemon=True)
        self.thread.start()

    def close(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

    def loop(self):
        while not self.stop_event.is_set():
            try:
                self.drain()
            except Exception as error:
                logger.warning("WhatsApp worker error: %s", type(error).__name__)
            self.stop_event.wait(2)

    def queue_reply(self, identifier, phone, text, incoming_id, sent_at):
        if self.store.get(SYSTEM, "wa_outbox", identifier):
            return
        self.store.put(SYSTEM, "wa_outbox", {
            "id": identifier, "status": "pending", "created": sent_at, "attempts": 0,
            "sealed": self.seal({"phone": phone, "text": text[:4000], "incoming_id": incoming_id}),
        })

    def drain(self):
        with self.lock:
            for item in self.store.list(SYSTEM, "wa_inbox"):
                if item["status"] == "pending":
                    self.process(item)
                if item.get("task_id"):
                    task = self.store.get(item["owner"], "task", item["task_id"])
                    if task and task["status"] in {"awaiting_input", "completed", "failed", "cancelled"}:
                        incoming = self.unseal(item["sealed"])
                        reply = task.get("reply", "This request was cancelled.")
                        if task["status"] == "awaiting_input":
                            reply += "\nReview this exact action in Sixth: " + self.settings.public_url
                        key = item["id"] + "-" + task["status"]
                        self.queue_reply(key, incoming["phone"], reply, incoming["provider_id"], incoming["sent_at"])
            if self.settings.whatsapp_send_enabled:
                for item in self.store.list(SYSTEM, "wa_outbox"):
                    if item["status"] == "pending" and item.get("retry_at", 0) <= time.time():
                        self.send(item)

    def process(self, item):
        incoming = self.unseal(item["sealed"])
        phone, text = incoming["phone"], incoming["text"].strip()
        phone_key = self.digest("phone:" + phone)
        if text.startswith("LINK "):
            key = self.digest("link:" + text[5:].strip())
            with self.store.transaction() as db:
                row = db.execute(
                    "SELECT data FROM records WHERE owner=? AND kind='wa_link' AND id=?", (SYSTEM, key),
                ).fetchone()
                link = json.loads(row[0]) if row else None
                if link and link["expires"] > time.time() and link["phone_key"] == phone_key:
                    owner = "wa_" + phone_key[:32]
                    self.store.put_tx(db, SYSTEM, "wa_identity", {"id": phone_key, "owner": owner})
                    self.store.put_tx(db, SYSTEM, "wa_link", {**link, "status": "verified", "owner": owner})
                    self.store.put_tx(db, owner, "profile", {"id": "self", "name": "Your Sixth", "channel": "whatsapp"})
                    reply = "WhatsApp connected to Sixth. Messages are stored to answer you and remember preferences. Tell me a preference, or ask what I remember. Actions need review in the web app."
                else:
                    reply = "This connection code is invalid or expired. Start again on the Sixth website."
            self.queue_reply(item["id"] + "-link", phone, reply, incoming["provider_id"], incoming["sent_at"])
            item["status"] = "done"
        else:
            identity = self.store.get(SYSTEM, "wa_identity", phone_key)
            if not identity:
                self.queue_reply(item["id"] + "-signup", phone,
                                 "Connect your number first at " + self.settings.public_url,
                                 incoming["provider_id"], incoming["sent_at"])
                item["status"] = "done"
            else:
                owner, conv_id = identity["owner"], "whatsapp"
                if not self.store.get(owner, "conversation", conv_id):
                    self.store.put(owner, "conversation", {"id": conv_id, "title": "WhatsApp", "created_at": now()})
                task_id = "wa-" + item["id"]
                submit_message(self.store, owner, conv_id, text, task_id=task_id,
                               source_id=task_id + "-source", channel="whatsapp")
                item.update(status="done", owner=owner, task_id=task_id)
                self.store.put(SYSTEM, "wa_inbox", item)
                self.runtime.run(owner, task_id)
        self.store.put(SYSTEM, "wa_inbox", item)

    def send(self, item):
        if time.time() - item["created"] > 23 * 3600:
            self.store.put(SYSTEM, "wa_outbox", {**item, "status": "expired"})
            return
        data = self.unseal(item["sealed"])
        item.update(status="sending", attempts=item["attempts"] + 1)
        self.store.put(SYSTEM, "wa_outbox", item)
        try:
            with httpx.Client(timeout=20) as client:
                response = client.post(
                    f"https://graph.facebook.com/{self.settings.whatsapp_api_version}/{self.settings.whatsapp_phone_number_id}/messages",
                    headers={"Authorization": "Bearer " + self.settings.whatsapp_access_token},
                    json={"messaging_product": "whatsapp", "to": data["phone"], "type": "text",
                          "context": {"message_id": data["incoming_id"]}, "text": {"body": data["text"]}},
                )
            if response.status_code == 429 and item["attempts"] < 3:
                item.update(status="pending", retry_at=time.time() + 60 * item["attempts"])
            elif response.is_success:
                message_id = response.json().get("messages", [{}])[0].get("id")
                item.update(status="sent" if message_id else "uncertain", provider_id=message_id)
            else:
                item.update(status="uncertain" if response.status_code >= 500 else "failed",
                            http_status=response.status_code)
        except (httpx.HTTPError, ValueError, IndexError):
            item["status"] = "uncertain"
        self.store.put(SYSTEM, "wa_outbox", item)

    def router(self, origin_check):
        router = APIRouter()

        @router.get("/v1/whatsapp/config")
        def config():
            return {"enabled": self.settings.whatsapp_enabled,
                    "sending_enabled": self.settings.whatsapp_send_enabled}

        @router.post("/v1/whatsapp/link", status_code=201)
        def link(body: LinkInput, request: Request, response: Response):
            self.require_enabled()
            origin_check(request)
            if body.phone[1:] not in self.settings.whatsapp_allowed_numbers:
                raise HTTPException(403, "This number is not enabled for the WhatsApp test integration")
            with self.lock:
                # Limit repeated anonymous link attempts without storing the raw IP or phone.
                bucket = int(time.time() // 600)
                rate_id = self.digest(f"rate:{request.client.host if request.client else ''}:{bucket}")
                rate = self.store.get(SYSTEM, "wa_rate", rate_id) or {"id": rate_id, "count": 0}
                if rate["count"] >= 10:
                    raise HTTPException(429, "Too many connection attempts. Try again later.")
                rate["count"] += 1
                self.store.put(SYSTEM, "wa_rate", rate)
                nonce = secrets.token_urlsafe(24)
                browser_secret = secrets.token_urlsafe(32)
                key = self.digest("link:" + nonce)
                self.store.put(SYSTEM, "wa_link", {"id": key, "phone_key": self.digest("phone:" + body.phone[1:]),
                                                  "status": "pending", "expires": time.time() + 600,
                                                  "consented_at": now(), "notice_version": "2026-10-17"})
                self.store.put(SYSTEM, "wa_browser", {"id": self.digest("browser:" + browser_secret),
                                                      "link_id": key})
            response.set_cookie("sixth_wa_link", browser_secret, httponly=True, secure=self.settings.cookie_secure,
                                samesite="strict", max_age=600, path="/v1/whatsapp")
            response.headers["Cache-Control"] = "no-store"
            return {"url": "https://wa.me/" + self.settings.whatsapp_business_number + "?text=" + quote("LINK " + nonce),
                    "expires_in": 600}

        @router.get("/v1/whatsapp/link")
        def linked(request: Request, response: Response):
            self.require_enabled()
            browser_secret = request.cookies.get("sixth_wa_link", "")
            binding = self.store.get(SYSTEM, "wa_browser", self.digest("browser:" + browser_secret)) if browser_secret else None
            link = self.store.get(SYSTEM, "wa_link", binding["link_id"]) if binding else None
            if not link or link["expires"] <= time.time():
                raise HTTPException(410, "Connection expired. Start again.")
            response.headers["Cache-Control"] = "no-store"
            if link["status"] != "verified":
                return {"connected": False}
            token, csrf = self.digest("session:" + browser_secret), self.digest("csrf:" + browser_secret)
            with self.store.transaction() as db:
                db.execute("INSERT INTO sessions VALUES (?,?,?,?) ON CONFLICT(token_hash) DO NOTHING",
                           (hashlib.sha256(token.encode()).hexdigest(), link["owner"], csrf, now()))
            response.set_cookie("sixth_session", token, httponly=True, secure=self.settings.cookie_secure,
                                samesite="strict", max_age=86400)
            return {"connected": True}

        @router.get("/webhooks/whatsapp")
        def verify(request: Request):
            self.require_enabled()
            query = request.query_params
            if query.get("hub.mode") != "subscribe" or not secrets.compare_digest(
                query.get("hub.verify_token", ""), self.settings.whatsapp_verify_token,
            ):
                raise HTTPException(403, "Webhook verification failed")
            return Response(query.get("hub.challenge", ""), media_type="text/plain")

        @router.post("/webhooks/whatsapp")
        async def webhook(request: Request):
            self.require_enabled()
            raw = bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > 1_000_000:
                    raise HTTPException(413, "Webhook too large")
            expected = "sha256=" + hmac.new(self.settings.whatsapp_app_secret.encode(), raw, hashlib.sha256).hexdigest()
            if not secrets.compare_digest(request.headers.get("x-hub-signature-256", ""), expected):
                raise HTTPException(403, "Invalid webhook signature")
            try:
                payload = json.loads(raw)
                if payload.get("object") != "whatsapp_business_account":
                    raise ValueError()
                for entry in payload.get("entry", [])[:100]:
                    for change in entry.get("changes", [])[:100]:
                        value = change.get("value", {})
                        if value.get("metadata", {}).get("phone_number_id") != self.settings.whatsapp_phone_number_id:
                            continue
                        for message in value.get("messages", [])[:100]:
                            phone, provider_id = message.get("from", ""), message.get("id", "")
                            if not re.fullmatch(r"[1-9][0-9]{7,14}", phone) or not 1 <= len(provider_id) <= 300:
                                continue
                            if phone not in self.settings.whatsapp_allowed_numbers:
                                continue
                            text = message.get("text", {}).get("body", "")
                            if message.get("type") != "text" or not isinstance(text, str) or not 1 <= len(text) <= 16000:
                                continue
                            sent_at = int(message.get("timestamp", 0))
                            if sent_at <= 0 or sent_at > time.time() + 60:
                                continue
                            item_id = self.digest("message:" + provider_id)
                            item = {"id": item_id, "status": "pending", "received": time.time(),
                                    "sealed": self.seal({"phone": phone, "text": text, "provider_id": provider_id,
                                                         "sent_at": sent_at})}
                            with self.store.transaction() as db:
                                db.execute("INSERT INTO records (owner,kind,id,data) VALUES (?,?,?,?) "
                                           "ON CONFLICT(owner,kind,id) DO NOTHING",
                                           (SYSTEM, "wa_inbox", item_id, json.dumps(item)))
            except (ValueError, TypeError, AttributeError):
                raise HTTPException(400, "Invalid webhook payload") from None
            return {"received": True}

        return router
