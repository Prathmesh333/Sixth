import hashlib
import json
import time

import pytest
from fastapi.testclient import TestClient
from sixth.accounts import ACCOUNTS, Accounts
from sixth.main import create_app
from test_application import send
from test_application import settings as shared_settings


@pytest.fixture(name="settings")
def account_settings(tmp_path):
    yield from shared_settings.__wrapped__(tmp_path)


@pytest.fixture
def google(settings, monkeypatch):
    settings.google_client_id = "test-client.apps.googleusercontent.com"

    def verify(self, credential):
        if credential == "bad-signature":
            raise ValueError("invalid signature")
        return json.loads(credential)

    monkeypatch.setattr(Accounts, "verify_google", verify)
    return settings


ORIGIN = {"Origin": "http://testserver"}


def google_login(client, subject, **overrides):
    start = client.post("/v1/auth/google/start", headers=ORIGIN)
    assert start.status_code == 200
    claims = {"sub": subject, "given_name": subject.title(), "email_verified": True,
              "nonce": start.json()["nonce"], **overrides}
    return client.post("/v1/auth/google", json={"credential": json.dumps(claims), "consent": True}, headers=ORIGIN)


def login(client, subject):
    response = google_login(client, subject)
    assert response.status_code == 200, response.text
    return {**ORIGIN, "X-CSRF-Token": response.json()["csrf_token"]}


def test_google_login_logout_persistence_and_isolation(google):
    app = create_app(google)
    with TestClient(app) as client:
        headers = login(client, "avery")
        current = client.get("/v1/session")
        assert current.headers["cache-control"] == "no-store"
        assert current.json()["demo"] is False and current.json()["name"] == "Avery"
        owner = current.json()["account"]
        assert owner.startswith("u_")
        assert "credential" not in str(app.state.store.list(ACCOUNTS, "google_identity"))
        task, _ = send(client, headers, "I am vegetarian")
        old_cookie = client.cookies.get("sixth_session")
        assert client.post("/v1/session/logout", headers=ORIGIN).status_code == 403
        assert client.post("/v1/session/logout", headers=headers).status_code == 200
        client.cookies.set("sixth_session", old_cookie)
        assert client.get("/v1/session").status_code == 401
        client.cookies.clear()
        login(client, "jules")
        assert client.get("/v1/memory").json()["items"] == []
        assert client.get(f"/v1/tasks/{task['id']}").status_code == 404
    with TestClient(create_app(google)) as client:
        response = google_login(client, "avery", given_name="New display name")
        assert response.status_code == 200 and response.json()["account"] == owner
        assert client.get("/v1/memory").json()["items"][0]["value"] == "vegetarian"


def test_google_challenge_nonce_consent_and_replay(google):
    app = create_app(google)
    with TestClient(app) as client:
        assert client.post("/v1/auth/google/start").status_code == 403
        assert client.post("/v1/auth/google", json={"credential": "x", "consent": True}, headers=ORIGIN).status_code == 401
        assert google_login(client, "avery", nonce="different-browser").status_code == 401
        assert google_login(client, "avery", email_verified=False).status_code == 401
        start = client.post("/v1/auth/google/start", headers=ORIGIN)
        nonce = start.json()["nonce"]
        assert client.post("/v1/auth/google", json={"credential": "bad-signature", "consent": True}, headers=ORIGIN).status_code == 401
        body = {"credential": json.dumps({"sub": "avery", "nonce": nonce, "email_verified": True}), "consent": False}
        assert client.post("/v1/auth/google", json=body, headers=ORIGIN).status_code == 422
        body["consent"] = True
        assert client.post("/v1/auth/google", json=body, headers=ORIGIN).status_code == 200
        client.cookies.set("sixth_google_nonce", nonce)
        assert client.post("/v1/auth/google", json=body, headers=ORIGIN).status_code == 401
        client.cookies.clear()
        nonce = client.post("/v1/auth/google/start", headers=ORIGIN).json()["nonce"]
        key = hashlib.sha256(nonce.encode()).hexdigest()
        item = app.state.store.get(ACCOUNTS, "google_challenge", key)
        app.state.store.put(ACCOUNTS, "google_challenge", {**item, "expires": time.time() - 1})
        assert client.post("/v1/auth/google", json=body, headers=ORIGIN).status_code == 401


def test_google_disabled_and_no_password_routes(settings):
    settings.demo_login = False
    with TestClient(create_app(settings)) as client:
        assert client.get("/v1/auth/config").json() == {"google_client_id": None}
        assert client.post("/v1/auth/google/start", headers=ORIGIN).status_code == 503
        assert client.post("/v1/accounts", json={}, headers=ORIGIN).status_code in {404, 405}
        assert client.post("/v1/session/login", json={}, headers=ORIGIN).status_code in {404, 405}
        assert client.post("/v1/session/demo", json={"account": "alex"}, headers=ORIGIN).status_code == 403


def test_friends_require_recipient_acceptance_and_never_share_memory(google):
    with TestClient(create_app(google)) as a, TestClient(a.app) as b, TestClient(a.app) as outsider:
        ah, bh, ch = login(a, "avery"), login(b, "jules"), login(outsider, "outsider")
        username_a = a.get("/v1/friends").json()["username"]
        username_b = b.get("/v1/friends").json()["username"]
        send(a, ah, "I am vegetarian")
        assert a.post("/v1/friends", json={"username": username_a}, headers=ah).status_code == 422
        result = a.post("/v1/friends", json={"username": username_b}, headers=ah)
        assert result.status_code == 201
        identifier = result.json()["id"]
        assert a.post(f"/v1/friends/{identifier}/accept", headers=ah).status_code == 403
        assert outsider.post(f"/v1/friends/{identifier}/accept", headers=ch).status_code == 404
        assert outsider.delete(f"/v1/friends/{identifier}", headers=ch).status_code == 404
        assert b.get("/v1/friends").json()["items"][0]["incoming"] is True
        assert b.post(f"/v1/friends/{identifier}/accept", headers=bh).json()["status"] == "accepted"
        assert b.get("/v1/memory").json()["items"] == []
        assert a.get("/v1/friends").json()["items"][0]["memory_shared"] is False
        assert b.delete(f"/v1/friends/{identifier}", headers=bh).status_code == 200
        assert a.get("/v1/friends").json()["items"] == []
