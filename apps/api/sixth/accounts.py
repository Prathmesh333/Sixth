"""Google-only personal accounts and revocable cookie sessions."""

import hashlib
import json
import re
import secrets
import time
from threading import RLock
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
from pydantic import BaseModel, ConfigDict, Field
from requests.exceptions import RequestException
from starlette.datastructures import MutableHeaders

from .models import now, uid

ACCOUNTS = "__accounts__"


class PrivateResponses:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def private_send(message):
            if message["type"] == "http.response.start" and scope.get("path", "").startswith("/v1/"):
                MutableHeaders(scope=message)["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, private_send)


class GoogleLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")
    credential: str = Field(min_length=1, max_length=16000, repr=False)
    consent: Literal[True]


class FriendInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")


class Accounts:
    def __init__(self, store, settings):
        self.store, self.settings = store, settings
        self.lock = RLock()

    def verify_google(self, credential):
        def fetch(*args, **kwargs):
            kwargs["timeout"] = 10
            return GoogleRequest()(*args, **kwargs)
        return id_token.verify_oauth2_token(credential, fetch, self.settings.google_client_id)

    def describe(self, owner, csrf):
        profile = self.store.get(owner, "profile", "self") or {}
        return {"account": owner, "name": profile.get("name", "Your Sixth" if owner.startswith("wa_") else owner.title()),
                "csrf_token": csrf, "demo": owner in {"alex", "jordan"}}

    def throttle(self, request, username, route):
        bucket = int(time.time() // 600)
        # No untrusted forwarded header is used as proof of client identity.
        client = request.client.host if request.client else "unknown"
        limits = [("global", 100), ("client:" + client, 20)]
        if username:
            limits.append(("user:" + username, 10))
        with self.store.transaction() as db:
            pending = []
            for subject, limit in limits:
                key = hashlib.sha256(f"{route}:{bucket}:{subject}".encode()).hexdigest()
                row = db.execute("SELECT data FROM records WHERE owner=? AND kind='auth_rate' AND id=?",
                                 (ACCOUNTS, key)).fetchone()
                rate = json.loads(row[0]) if row else {"id": key, "count": 0}
                if rate["count"] >= limit:
                    raise HTTPException(429, "Too many attempts. Try again in 10 minutes.")
                pending.append({**rate, "count": rate["count"] + 1})
            for rate in pending:
                self.store.put_tx(db, ACCOUNTS, "auth_rate", rate)

    def issue(self, owner, request, response):
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
        with self.store.transaction() as db:
            old = request.cookies.get("sixth_session", "")
            db.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(old.encode()).hexdigest(),))
            db.execute("INSERT INTO sessions VALUES (?,?,?,?)",
                       (hashlib.sha256(token.encode()).hexdigest(), owner, csrf, now()))
        response.set_cookie("sixth_session", token, httponly=True, samesite="strict",
                            secure=self.settings.cookie_secure, max_age=86400)
        response.headers["Cache-Control"] = "no-store"
        return self.describe(owner, csrf)

    def router(self, origin_check, session):
        router = APIRouter()

        @router.get("/v1/auth/config")
        def config():
            return {"google_client_id": self.settings.google_client_id or None}

        @router.post("/v1/auth/google/start")
        def start(request: Request, response: Response):
            origin_check(request)
            if not self.settings.google_client_id:
                raise HTTPException(503, "Google sign-in is being configured")
            with self.lock:
                self.throttle(request, "", "start")
                nonce = secrets.token_urlsafe(32)
                key = hashlib.sha256(nonce.encode()).hexdigest()
                self.store.put(ACCOUNTS, "google_challenge", {"id": key, "expires": time.time() + 600, "used": False})
            response.set_cookie("sixth_google_nonce", nonce, httponly=True, samesite="strict",
                                secure=self.settings.cookie_secure, max_age=600, path="/v1/auth/google")
            return {"nonce": nonce}

        @router.post("/v1/auth/google")
        def google_login(body: GoogleLogin, request: Request, response: Response):
            origin_check(request)
            if not self.settings.google_client_id:
                raise HTTPException(503, "Google sign-in is being configured")
            with self.lock:
                self.throttle(request, "", "login")
                nonce = request.cookies.get("sixth_google_nonce", "")
                key = hashlib.sha256(nonce.encode()).hexdigest()
                challenge = self.store.get(ACCOUNTS, "google_challenge", key) if nonce else None
                if not challenge or challenge["used"] or challenge["expires"] <= time.time():
                    raise HTTPException(401, "Restart Google sign-in to continue")
                try:
                    claims = self.verify_google(body.credential)
                except (ValueError, GoogleAuthError, RequestException):
                    raise HTTPException(401, "Google sign-in could not be verified. Please retry.") from None
                if not claims.get("sub") or claims.get("email_verified") is not True or not secrets.compare_digest(str(claims.get("nonce", "")), nonce):
                    raise HTTPException(401, "Google sign-in could not be verified. Please retry.")
                identity_key = hashlib.sha256(str(claims["sub"]).encode()).hexdigest()
                identity = self.store.get(ACCOUNTS, "google_identity", identity_key)
                with self.store.transaction() as db:
                    if not identity:
                        owner = "u_" + uid()
                        name = str(claims.get("given_name") or claims.get("name") or "Sixth user").strip()[:60] or "Sixth user"
                        base = re.sub(r"[^a-z0-9]", "", name.lower())[:18] or "sixth"
                        username = base + "_" + secrets.token_hex(4)
                        identity = {"id": identity_key, "owner": owner}
                        self.store.put_tx(db, ACCOUNTS, "google_identity", identity)
                        self.store.put_tx(db, ACCOUNTS, "account", {"id": username, "owner": owner, "created_at": now()})
                        self.store.put_tx(db, owner, "profile", {"id": "self", "name": name, "username": username,
                                                                "channel": "google", "consented_at": now()})
                    self.store.put_tx(db, ACCOUNTS, "google_challenge", {**challenge, "used": True})
                response.delete_cookie("sixth_google_nonce", path="/v1/auth/google", httponly=True,
                                       samesite="strict", secure=self.settings.cookie_secure)
                return self.issue(identity["owner"], request, response)

        @router.post("/v1/session/logout")
        def logout(response: Response, auth=Depends(session)):
            with self.store.transaction() as db:
                db.execute("DELETE FROM sessions WHERE token_hash=?", (auth["token_hash"],))
            response.delete_cookie("sixth_session", httponly=True, samesite="strict", secure=self.settings.cookie_secure)
            response.headers["Cache-Control"] = "no-store"
            return {"signed_out": True}

        def personal(auth):
            if not auth["owner"].startswith("u_"):
                raise HTTPException(403, "Create a personal Sixth account to add friends")
            return auth["owner"]

        def friendship(owner, identifier):
            item = self.store.get(ACCOUNTS, "friend", identifier)
            if not item or owner not in item["members"]:
                raise HTTPException(404, "Friend request not found")
            return item

        def present(owner, item):
            other = next(member for member in item["members"] if member != owner)
            profile = self.store.get(other, "profile", "self") or {}
            return {"id": item["id"], "name": profile.get("name", "Sixth user"),
                    "username": profile.get("username", ""), "status": item["status"],
                    "incoming": item["requested_by"] != owner,
                    "memory_shared": bool(item.get("sharing", {}).get(other, {}).get("memory_ids")),
                    "availability_shared": bool(item.get("sharing", {}).get(other, {}).get("availability"))}

        @router.get("/v1/friends")
        def friends(auth=Depends(session)):
            owner = personal(auth)
            profile = self.store.get(owner, "profile", "self")
            return {"username": profile["username"], "items": [present(owner, item)
                    for item in self.store.list(ACCOUNTS, "friend") if owner in item["members"]]}

        @router.post("/v1/friends", status_code=201)
        def invite(body: FriendInput, request: Request, auth=Depends(session)):
            owner = personal(auth)
            with self.lock:
                self.throttle(request, owner, "friends")
                target = self.store.get(ACCOUNTS, "account", body.username.lower())
                if not target:
                    raise HTTPException(404, "No Sixth account has this username")
                if target["owner"] == owner:
                    raise HTTPException(422, "Choose someone else's username")
                members = sorted([owner, target["owner"]])
                identifier = hashlib.sha256(":".join(members).encode()).hexdigest()
                existing = self.store.get(ACCOUNTS, "friend", identifier)
                item = existing or self.store.put(ACCOUNTS, "friend", {
                    "id": identifier, "members": members, "requested_by": owner,
                    "status": "pending", "created_at": now(),
                })
                return present(owner, item)

        @router.post("/v1/friends/{identifier}/accept")
        def accept(identifier: str, auth=Depends(session)):
            owner = personal(auth)
            with self.lock:
                item = friendship(owner, identifier)
                if item["requested_by"] == owner:
                    raise HTTPException(403, "Only the recipient can accept this request")
                if item["status"] != "pending":
                    raise HTTPException(409, "This request is no longer pending")
                item = self.store.put(ACCOUNTS, "friend", {**item, "status": "accepted", "accepted_at": now()})
                return present(owner, item)

        @router.delete("/v1/friends/{identifier}")
        def remove(identifier: str, auth=Depends(session)):
            owner = personal(auth)
            with self.lock:
                friendship(owner, identifier)
                with self.store.transaction() as db:
                    db.execute("DELETE FROM records WHERE owner=? AND kind='friend' AND id=?", (ACCOUNTS, identifier))
            return {"removed": True}

        return router
