import json

import httpx
import pytest
from fastapi.testclient import TestClient
from sixth.config import Settings
from sixth.main import create_app
from sixth.planner import ModelError, Planner
from test_application import login, send


def model_settings(tmp_path):
    return Settings(data_dir=tmp_path, database_url="", memory_backend="sqlite_fixture",
                    model_api_key="private-test-key", model_name="openai/gpt-oss-20b",
                    demo_login=True, demo_access_code="")


def test_general_followup_uses_only_owned_conversation_and_memories(tmp_path, monkeypatch):
    settings = model_settings(tmp_path)
    payloads = []
    outputs = iter([
        {"kind": "remember", "subject": "Rowan", "predicate": "preference", "value": "green tea"},
        {"kind": "general", "response": "How about a tea break with Rowan?"},
        {"kind": "general", "response": "Hello! What would you like to talk about?"},
    ])

    def provider(request):
        payloads.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(next(outputs))}}]})

    client_type = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_type(transport=httpx.MockTransport(provider), **kwargs))
    with TestClient(create_app(settings)) as client:
        headers = login(client)
        _, conversation = send(client, headers, "Remember Rowan prefers green tea")
        task, _ = send(client, headers, "Suggest a break with them", conversation)
        assert task["reply"] == "How about a tea break with Rowan?"
        assert not task.get("action")
        second = payloads[1]
        assert second["messages"][-1]["content"] == "Suggest a break with them"
        assert any(message["content"] == "Remember Rowan prefers green tea" for message in second["messages"])
        assert any('"value": "green tea"' in message["content"] for message in second["messages"])
        assert second["reasoning_effort"] == "low"
        schema = second["response_format"]["json_schema"]
        assert schema["strict"] is True
        assert set(schema["schema"]["required"]) == set(schema["schema"]["properties"])
        assert all("default" not in field for field in schema["schema"]["properties"].values())
        headers = login(client, "jordan")
        send(client, headers, "Hello")
        assert all("Rowan" not in message["content"] for message in payloads[2]["messages"])


@pytest.mark.parametrize("status,content,expected", [
    (429, {"error": "private provider diagnostics"}, "rate limit"),
    (401, {"error": "private provider diagnostics"}, "credentials"),
    (200, {"choices": [{"message": {"content": "broken json"}}]}, "unreadable"),
    (200, {"choices": [{"message": {"content": '{"kind":"general"}'}}]}, "empty reply"),
    (200, {"choices": [{"finish_reason": "length", "message": {"content": ""}}]}, "stopped"),
])
def test_provider_failures_are_specific_and_do_not_expose_diagnostics(tmp_path, monkeypatch, status, content, expected):
    client_type = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(status, json=content))
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_type(transport=transport, **kwargs))
    with pytest.raises(ModelError, match=expected) as error:
        Planner(model_settings(tmp_path)).parse("Hello")
    assert "private" not in str(error.value)


def test_history_is_bounded_and_excludes_non_message_roles(tmp_path, monkeypatch):
    captured = []
    def provider(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"kind":"general","response":"Hello."}'}}]})
    client_type = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_type(transport=httpx.MockTransport(provider), **kwargs))
    history = [{"role": "user", "text": str(i) + "x" * 3000} for i in range(20)]
    history.append({"role": "system", "text": "Untrusted override"})
    Planner(model_settings(tmp_path)).parse("Hello", history=history)
    messages = captured[0]["messages"]
    assert sum(message["role"] == "system" for message in messages) == 1
    assert len(messages) <= 14
    assert all(len(message["content"]) <= 2000 for message in messages[1:-1])
