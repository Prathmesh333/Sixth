import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sixth.main import create_app
from sixth.whatsapp import SYSTEM
from test_application import settings as shared_settings


@pytest.fixture(name="settings")
def channel_settings(tmp_path):
    yield from shared_settings.__wrapped__(tmp_path)


@pytest.fixture
def channel(settings):
    settings.whatsapp_enabled = True
    settings.whatsapp_app_secret = "test-app-secret-not-for-production"
    settings.whatsapp_identity_secret = "test-identity-secret-separate-from-meta"
    settings.whatsapp_allowed_numbers = ["15555550101", "15555550202"]
    settings.whatsapp_verify_token = "test-verify-token"
    settings.whatsapp_phone_number_id = "123456789"
    settings.whatsapp_business_number = "15555550999"
    settings.whatsapp_encryption_key = Fernet.generate_key().decode()
    settings.whatsapp_api_version = "v25.0"
    settings.whatsapp_send_enabled = False
    app = create_app(settings)
    app.state.whatsapp.start = lambda: None
    with TestClient(app) as client:
        yield client, app.state.whatsapp, settings


def incoming(client, settings, text, identifier, phone="15555550101", timestamp=None):
    payload = {"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {
        "metadata": {"phone_number_id": settings.whatsapp_phone_number_id},
        "messages": [{"id": identifier, "from": phone, "type": "text",
                      "timestamp": str(timestamp or int(time.time())), "text": {"body": text}}],
    }}]}]}
    raw = json.dumps(payload).encode()
    signature = hmac.new(settings.whatsapp_app_secret.encode(), raw, hashlib.sha256).hexdigest()
    return client.post("/webhooks/whatsapp", content=raw,
                       headers={"X-Hub-Signature-256": "sha256=" + signature, "Content-Type": "application/json"})


def link(client, phone="+15555550101"):
    response = client.post("/v1/whatsapp/link", json={"phone": phone, "consent": True}, headers={"Origin": "http://testserver"})
    assert response.status_code == 201
    return parse_qs(urlparse(response.json()["url"]).query)["text"][0]


def test_webhook_signature_verification_and_phone_possession(channel):
    client, wa, settings = channel
    assert client.get("/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "wrong"}).status_code == 403
    verified = client.get("/webhooks/whatsapp", params={
        "hub.mode": "subscribe", "hub.verify_token": settings.whatsapp_verify_token, "hub.challenge": "challenge123",
    })
    assert verified.text == "challenge123"
    assert client.post("/webhooks/whatsapp", json={"object": "whatsapp_business_account"}).status_code == 403
    assert wa.store.list(SYSTEM, "wa_inbox") == []
    code = link(client)
    assert client.get("/v1/whatsapp/link").json() == {"connected": False}
    assert incoming(client, settings, code, "wrong-sender", phone="15555550202").status_code == 200
    wa.drain()
    assert client.get("/v1/whatsapp/link").json() == {"connected": False}
    assert client.get("/v1/session").status_code == 401
    assert incoming(client, settings, code, "correct-sender").status_code == 200
    wa.drain()
    outsider = TestClient(client.app)
    outsider.cookies.set("sixth_wa_link", code[5:])
    assert outsider.get("/v1/whatsapp/link").status_code == 410
    outsider.close()
    assert client.get("/v1/whatsapp/link").json() == {"connected": True}
    session = client.get("/v1/session").json()
    assert session["account"].startswith("wa_")
    assert session["demo"] is False
    assert "15555550101" not in session["account"]


def test_inbound_memory_is_durable_deduplicated_and_isolated(channel):
    client, wa, settings = channel
    code = link(client)
    incoming(client, settings, code, "link-first")
    wa.drain()
    client.get("/v1/whatsapp/link")
    session = client.get("/v1/session").json()
    assert incoming(client, settings, "I am vegetarian", "message-1").status_code == 200
    assert incoming(client, settings, "I am vegetarian", "message-1").status_code == 200
    # Webhook acknowledgement has not executed the model or created a task.
    assert wa.store.list(session["account"], "task") == []
    wa.drain()
    wa.drain()
    assert len(wa.store.list(session["account"], "task")) == 1
    facts = client.get("/v1/memory").json()["items"]
    assert len(facts) == 1 and facts[0]["value"] == "vegetarian"
    outbox = wa.store.list(SYSTEM, "wa_outbox")
    assert len(outbox) == 2
    assert all(item["status"] == "pending" for item in outbox)
    assert "15555550101" not in json.dumps(wa.store.list(SYSTEM, "wa_inbox"))
    assert "I am vegetarian" not in json.dumps(wa.store.list(SYSTEM, "wa_inbox"))
    from test_application import login
    login(client, "alex")
    assert client.get("/v1/memory").json()["items"] == []
    assert client.get(f"/v1/tasks/{wa.store.list(session['account'], 'task')[0]['id']}").status_code == 404


def test_link_expiry_origin_and_rate_limit(channel):
    client, wa, _ = channel
    assert client.post("/v1/whatsapp/link", json={"phone": "+15555550101", "consent": True}).status_code == 403
    code = link(client)
    key = wa.digest("link:" + code[5:])
    item = wa.store.get(SYSTEM, "wa_link", key)
    wa.store.put(SYSTEM, "wa_link", {**item, "expires": time.time() - 1})
    assert client.get("/v1/whatsapp/link").status_code == 410
    for _ in range(9):
        assert client.post("/v1/whatsapp/link", json={"phone": "+15555550101", "consent": True},
                           headers={"Origin": "http://testserver"}).status_code == 201
    assert client.post("/v1/whatsapp/link", json={"phone": "+15555550101", "consent": True},
                       headers={"Origin": "http://testserver"}).status_code == 429


def test_outbound_uncertainty_is_not_retried_and_old_messages_expire(channel, monkeypatch):
    _, wa, settings = channel
    settings.whatsapp_send_enabled = True
    settings.whatsapp_access_token = "test-access-token"
    calls = []
    client_type = httpx.Client

    def timeout(request):
        calls.append(request)
        raise httpx.ReadTimeout("simulated uncertain send", request=request)

    transport = httpx.MockTransport(timeout)
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_type(transport=transport, **kwargs))
    wa.queue_reply("reply-1", "15555550101", "Test reply", "provider-1", time.time())
    wa.queue_reply("reply-expired", "15555550101", "Old reply", "provider-2", time.time() - 86400)
    wa.drain()
    wa.drain()
    assert len(calls) == 1
    assert wa.store.get(SYSTEM, "wa_outbox", "reply-1")["status"] == "uncertain"
    assert wa.store.get(SYSTEM, "wa_outbox", "reply-expired")["status"] == "expired"


def test_whatsapp_action_requires_web_review(channel):
    client, wa, settings = channel
    incoming(client, settings, link(client), "link-action")
    wa.drain()
    client.get("/v1/whatsapp/link")
    owner = client.get("/v1/session").json()["account"]
    incoming(client, settings, "Plan dinner for four", "dinner-action")
    wa.drain()
    task = wa.store.list(owner, "task")[0]
    assert task["status"] == "awaiting_input"
    with wa.store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM action_ledger").fetchone()[0] == 0
    replies = [wa.unseal(item["sealed"])["text"] for item in wa.store.list(SYSTEM, "wa_outbox")]
    assert any("Review this exact action in Sixth" in text for text in replies)


def test_outbound_success_records_provider_acceptance(channel, monkeypatch):
    _, wa, settings = channel
    settings.whatsapp_send_enabled = True
    settings.whatsapp_access_token = "test-access-token"
    calls = []
    client_type = httpx.Client

    def accept(request):
        calls.append(request)
        assert request.headers["Authorization"] == "Bearer test-access-token"
        assert json.loads(request.content)["to"] == "15555550101"
        return httpx.Response(200, json={"messages": [{"id": "accepted-test-message"}]})

    transport = httpx.MockTransport(accept)
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_type(transport=transport, **kwargs))
    wa.queue_reply("accepted", "15555550101", "Test reply", "incoming-test", time.time())
    wa.drain()
    wa.drain()
    assert len(calls) == 1
    assert wa.store.get(SYSTEM, "wa_outbox", "accepted")["status"] == "sent"


def test_disabled_channel_is_explicit(settings):
    with TestClient(create_app(settings)) as client:
        assert client.get("/v1/whatsapp/config").json()["enabled"] is False
        assert client.post("/webhooks/whatsapp", json={}).status_code == 503
