import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sixth.config import Settings
from sixth.main import create_app


@pytest.fixture
def settings(tmp_path: Path):
    return Settings(data_dir=tmp_path, memory_backend="sqlite_fixture", model_api_key="", model_name="")


def login(client, account="alex"):
    response = client.post(
        "/v1/session/demo", json={"account": account}, headers={"Origin": "http://testserver"}
    )
    assert response.status_code == 200, response.text
    return {"Origin": "http://testserver", "X-CSRF-Token": response.json()["csrf_token"]}


@pytest.fixture
def workspace(settings):
    app = create_app(settings)
    with TestClient(app) as client:
        headers = login(client)
        yield client, headers, app


def send(client, headers, text, conversation_id=None, key=None):
    if not conversation_id:
        conversation_id = client.post("/v1/conversations", headers=headers).json()["id"]
    response = client.post(
        f"/v1/conversations/{conversation_id}/messages",
        json={"text": text},
        headers={**headers, "Idempotency-Key": key or __import__("uuid").uuid4().hex},
    )
    assert response.status_code == 202, response.text
    return wait(client, response.json()["task_id"]), conversation_id


def wait(client, task_id):
    for _ in range(150):
        task = client.get(f"/v1/tasks/{task_id}").json()
        if task["status"] in {"awaiting_input", "completed", "failed", "cancelled"}:
            assert task["status"] != "failed", task
            return task
        time.sleep(0.02)
    pytest.fail("Task did not finish")


def approve(client, headers, task, key="approve-cart-once"):
    action = task["action"]
    return client.post(
        f"/v1/tasks/{task['id']}/decisions",
        headers={**headers, "Idempotency-Key": key},
        json={
            "decision_id": action["decision_id"],
            "decision": "approve",
            "fingerprint": action["fingerprint"],
            "plan_revision": action["plan_revision"],
        },
    )


def test_memory_changes_action_and_cart_replay_is_safe(workspace):
    client, headers, app = workspace
    send(client, headers, "Maya is vegetarian")
    first, conversation = send(client, headers, "Plan Maya's birthday dinner for four")
    assert first["plan"]["guests"] == 4
    assert first["evidence"][0]["value"] == "vegetarian"
    assert first["plan"]["recipe"]["dairy_free"] is False
    revised, _ = send(
        client, headers, "Two more people are joining and Maya avoids dairy for this dinner", conversation
    )
    assert revised["plan"]["guests"] == 6
    assert revised["plan"]["recipe"]["dairy_free"] is True
    rice = next(item for item in revised["plan"]["items"] if item["id"] == "rice")
    assert rice["quantity"] == 250
    assert approve(client, headers, first, "stale-review-key").status_code == 409
    assert approve(client, headers, revised).status_code == 202
    assert wait(client, revised["id"])["result"]["status"] == "succeeded"
    assert approve(client, headers, revised).status_code == 202
    assert len(client.get("/v1/carts").json()) == 1
    with app.state.store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM action_ledger").fetchone()[0] == 1


def test_cross_account_isolation_and_csrf(workspace):
    client, headers, _ = workspace
    send(client, headers, "Maya is vegetarian")
    task, conversation = send(client, headers, "Plan dinner for four")
    assert client.post("/v1/conversations").status_code == 403
    login(client, "jordan")
    assert client.get("/v1/memory").json()["items"] == []
    assert client.get(f"/v1/tasks/{task['id']}").status_code == 404
    assert client.get(f"/v1/tasks/{task['id']}/events").status_code == 404
    assert client.get(f"/v1/conversations/{conversation}").status_code == 404
    assert (
        client.post(
            "/v1/session/demo", json={"account": "alex"}, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )


def test_correction_and_forgetting_remove_retrievable_context(workspace):
    client, headers, _ = workspace
    send(client, headers, "Maya is vegetarian")
    fact = client.get("/v1/memory").json()["items"][0]
    correction = client.patch(
        f"/v1/memory/{fact['id']}",
        json={"expected_version": 1, "value": "vegan", "reason": "Maya told me"},
        headers=headers,
    )
    assert correction.status_code == 200
    assert correction.json()["version"] == 2
    assert (
        client.patch(
            f"/v1/memory/{fact['id']}",
            json={"expected_version": 1, "value": "vegetarian", "reason": "stale"},
            headers=headers,
        ).status_code
        == 409
    )
    task, _ = send(client, headers, "Plan dinner for four")
    assert task["plan"]["recipe"]["dairy_free"] is True
    current = correction.json()
    assert client.delete(f"/v1/memory/{current['id']}", headers=headers).status_code == 202
    assert client.get("/v1/memory").json()["items"] == []
    assert approve(client, headers, task).status_code == 409


def test_other_account_cannot_retrieve_modify_or_delete_private_profile(workspace):
    client, headers, _ = workspace
    created = client.post(
        "/v1/memory",
        headers=headers,
        json={
            "subject": "Me",
            "predicate": "preference",
            "value": "private-profile-marker-8472",
            "source_text": "My private preference",
        },
    )
    assert created.status_code == 201
    fact = created.json()

    other_headers = login(client, "jordan")
    # A supplied owner or known subject ID must never select another account's graph.
    response = client.get("/v1/memory", params={"owner": "alex", "subject_id": fact["subject_id"]})
    assert response.status_code == 200
    assert response.json()["items"] == []
    exported = client.get("/v1/export")
    assert exported.status_code == 200
    assert exported.json()["assertions"] == []
    assert "private-profile-marker-8472" not in exported.text
    assert client.patch(
        f"/v1/memory/{fact['id']}",
        headers=other_headers,
        json={"expected_version": 1, "value": "changed", "reason": "cross-account attempt"},
    ).status_code == 404
    assert client.delete(f"/v1/memory/{fact['id']}", headers=other_headers).status_code == 404

    recall, _ = send(client, other_headers, "What do you know about Alex?")
    assert recall["evidence"] == []
    assert "private-profile-marker-8472" not in recall["reply"]

    login(client, "alex")
    remaining = client.get("/v1/memory").json()["items"]
    assert len(remaining) == 1
    assert remaining[0]["id"] == fact["id"]
    assert remaining[0]["value"] == "private-profile-marker-8472"


def test_http_retry_and_sse_reconnect(workspace):
    client, headers, _ = workspace
    first, conv = send(client, headers, "Maya is vegetarian", key="same-request-key")
    second, _ = send(client, headers, "Maya is vegetarian", conv, key="same-request-key")
    assert first["id"] == second["id"]
    response = client.get(f"/v1/tasks/{first['id']}/events")
    assert "task.completed" in response.text
    assert "text/event-stream" in response.headers["content-type"]
    assert client.get(f"/v1/tasks/{first['id']}/events", headers={"Last-Event-ID": "9999"}).text == ""
    conflicting = client.post(
        f"/v1/conversations/{conv}/messages",
        json={"text": "different"},
        headers={**headers, "Idempotency-Key": "same-request-key"},
    )
    assert conflicting.status_code == 409


def test_persistent_checkpoint_resumes_review_after_restart(settings):
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        send(client, headers, "Maya is vegetarian")
        pending, _ = send(client, headers, "Plan dinner for four")
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        assert len(client.get("/v1/memory").json()["items"]) == 1
        assert approve(client, headers, pending).status_code == 202
        assert wait(client, pending["id"])["result"]["status"] == "succeeded"
        assert len(client.get("/v1/carts").json()) == 1


def test_unsupported_dietary_constraint_blocks_cart(workspace):
    client, headers, _ = workspace
    response = client.post(
        "/v1/memory",
        headers=headers,
        json={
            "subject": "Maya",
            "predicate": "allergy",
            "value": "sesame",
            "source_text": "Maya has a sesame allergy",
        },
    )
    assert response.status_code == 201
    task, _ = send(client, headers, "Plan dinner for four")
    assert "action" not in task
    assert "cannot verify" in task["reply"]


def test_falkordb_configuration_does_not_silently_fall_back(settings):
    settings.memory_backend = "falkordb"
    settings.falkordb_port = 1
    with TestClient(create_app(settings)) as client:
        login(client)
        status = client.get("/v1/status").json()
        assert status["memory"]["backend"] == "falkordb"
        assert status["memory"]["connected"] is False
        assert client.get("/health/ready").status_code == 503


def test_explicit_timezone_and_invalid_timezone(workspace):
    client, headers, _ = workspace
    conversation_id = client.post("/v1/conversations", headers=headers).json()["id"]
    response = client.post(
        f"/v1/conversations/{conversation_id}/messages",
        json={"text": "Hello", "timezone": "Asia/Calcutta"},
        headers={**headers, "Idempotency-Key": "timezone-request"},
    )
    assert response.status_code == 202
    invalid = client.post(
        f"/v1/conversations/{conversation_id}/messages",
        json={"text": "Hello", "timezone": "Not/AZone"},
        headers={**headers, "Idempotency-Key": "invalid-timezone"},
    )
    assert invalid.status_code == 422
