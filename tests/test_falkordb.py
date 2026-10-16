"""Real graph smoke test, opt-in locally and enabled in the dedicated CI job."""

import os
from uuid import uuid4

import pytest
from sixth.config import Settings
from sixth.memory import Memory
from sixth.models import FactInput, now, uid
from sixth.planner import Planner
from sixth.runtime import Runtime
from sixth.storage import Store

pytestmark = pytest.mark.skipif(
    os.environ.get("SIXTH_GRAPH_TEST") != "1", reason="Requires a real FalkorDB server"
)


def test_real_graph_context_correction_and_isolation(tmp_path):
    settings = Settings(data_dir=tmp_path, memory_backend="falkordb")
    memory = Memory(Store(tmp_path / "operational.sqlite"), settings)
    owner, other = "integration-" + uuid4().hex, "integration-" + uuid4().hex
    assert memory.health()["connected"]
    fact = memory.add(
        owner,
        FactInput(subject="Maya", predicate="diet", value="vegetarian", source_text="Maya is vegetarian"),
    )
    memory.ensure_event(owner, "test-dinner", ["Maya"])
    assert memory.current(owner, "test-dinner")[0]["id"] == fact["id"]
    assert memory.current(other) == []
    paths = (
        memory.graph(owner)
        .query("""
        MATCH (e:Event)<-[:ATTENDS]-(p:Person)<-[:HAS_SUBJECT]-(a:Assertion)-[:SUPPORTED_BY]->(s:Source)
        RETURN count(s)
    """)
        .result_set
    )
    assert paths[0][0] == 1
    corrected = memory.correct(owner, fact["id"], 1, "vegan", "Maya changed her preference")
    assert [f["value"] for f in memory.current(owner, "test-dinner")] == ["vegan"]
    memory.forget(owner, corrected["id"])
    assert memory.current(owner, "test-dinner") == []
    assert memory.health()["connected"]


def test_graph_backed_plan_and_verified_outcome(tmp_path):
    settings = Settings(data_dir=tmp_path, memory_backend="falkordb", model_api_key="", model_name="")
    store = Store(tmp_path / "operational.sqlite")
    memory = Memory(store, settings)
    runtime = Runtime(store, memory, Planner(settings))
    owner = "integration-" + uuid4().hex
    memory.add(owner, FactInput(subject="Maya", predicate="diet", value="vegan", source_text="Maya is vegan"))
    task_id = uid()
    store.put(
        owner,
        "task",
        {
            "id": task_id,
            "conversation_id": uid(),
            "source_id": uid(),
            "text": "Plan Maya's birthday dinner for four",
            "status": "queued",
            "updated_at": now(),
        },
    )
    try:
        runtime.run(owner, task_id)
        task = store.get(owner, "task", task_id)
        assert task["status"] == "awaiting_input", task
        assert task["plan"]["recipe"]["dairy_free"]
        paths = (
            memory.graph(owner)
            .query("""
            MATCH (p:Plan)-[:BASED_ON]->(a:Assertion)-[:SUPPORTED_BY]->(s:Source)
            RETURN count(s)
        """)
            .result_set
        )
        assert paths[0][0] == 1
        task.update(decision="approve", status="running")
        store.put(owner, "task", task)
        runtime.run(owner, task_id, "approve")
        completed = store.get(owner, "task", task_id)
        assert completed["status"] == "completed", completed
        assert completed["result"]["status"] == "succeeded"
        outcomes = (
            memory.graph(owner).query("MATCH (:Action)-[:PRODUCED]->(o:Outcome) RETURN o.status").result_set
        )
        assert outcomes == [["verified"]]
        assert store.list(owner, "outbox")[0]["status"] == "applied"
    finally:
        runtime.close()
