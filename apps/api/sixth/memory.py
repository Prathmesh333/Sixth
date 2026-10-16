import hashlib
import json

from falkordb import FalkorDB

from .config import Settings
from .models import FactInput, now, uid
from .storage import Store


class Memory:
    def __init__(self, store: Store, settings: Settings):
        self.store, self.settings = store, settings
        self.client = None
        self.enabled = settings.memory_backend == "falkordb"

    def graph(self, owner: str):
        # Never accept a graph selector from the model or request body.
        if self.client is None:
            settings = self.settings
            self.client = FalkorDB(
                host=settings.falkordb_host,
                port=settings.falkordb_port,
                username=settings.falkordb_username,
                password=settings.falkordb_password,
                ssl=settings.falkordb_ssl,
                socket_connect_timeout=2,
                socket_timeout=3,
            )
        graph_name = "sixth_u_" + hashlib.sha256(owner.encode()).hexdigest()[:24]
        return self.client.select_graph(graph_name)

    def health(self):
        if not self.enabled:
            return {
                "backend": "sqlite_fixture",
                "connected": True,
                "simulation": True,
                "detail": "Local fixture memory. FalkorDB is not connected.",
            }
        try:
            self.graph("health").query("RETURN 1")
            return {
                "backend": "falkordb",
                "connected": True,
                "simulation": False,
                "detail": "FalkorDB personal graphs connected.",
            }
        except Exception:
            return {
                "backend": "falkordb",
                "connected": False,
                "simulation": False,
                "detail": "FalkorDB unavailable. Check the server and configured connection.",
            }

    def all(self, owner: str) -> list[dict]:
        if not self.enabled:
            return self.store.list(owner, "fact")
        rows = self.graph(owner).query("MATCH (a:Assertion) RETURN a.payload").result_set
        return [json.loads(row[0]) for row in rows]

    def current(self, owner: str, event_id: str | None = None) -> list[dict]:
        if not self.enabled:
            facts = self.all(owner)
        else:
            if event_id:
                rows = (
                    self.graph(owner)
                    .query(
                        """
                    MATCH (p:Person)-[:ATTENDS]->(e:Event {id:$event_id}),
                          (a:Assertion)-[:HAS_SUBJECT]->(p), (a)-[:SUPPORTED_BY]->(s:Source)
                    WHERE a.status='confirmed'
                      AND (a.scope_type='person' OR (a.scope_type='event' AND a.scope_id=$event_id))
                    RETURN DISTINCT a.payload
                """,
                        params={"event_id": event_id},
                    )
                    .result_set
                )
            else:
                rows = (
                    self.graph(owner)
                    .query("""
                MATCH (a:Assertion)-[:HAS_SUBJECT]->(p:Person), (a)-[:SUPPORTED_BY]->(s:Source)
                WHERE a.status='confirmed'
                RETURN a.payload
                """)
                    .result_set
                )
            facts = [json.loads(row[0]) for row in rows]
        return [
            fact
            for fact in facts
            if fact["status"] == "confirmed"
            and (fact["scope_type"] == "person" or fact["scope_id"] == event_id)
        ]

    def save(self, owner: str, fact: dict):
        if not self.enabled:
            return self.store.put(owner, "fact", fact)
        self.graph(owner).query(
            """
            MERGE (p:Person {id:$subject_id}) SET p.name=$subject
            MERGE (s:Source {id:$source_id}) SET s.excerpt=$excerpt, s.captured_at=$captured_at
            MERGE (a:Assertion {id:$id})
            SET a.payload=$payload, a.status=$status, a.predicate=$predicate,
                a.scope_type=$scope_type, a.scope_id=$scope_id, a.version=$version
            MERGE (a)-[:HAS_SUBJECT]->(p)
            MERGE (a)-[:SUPPORTED_BY]->(s)
        """,
            params={
                "subject_id": fact["subject"].casefold(),
                "subject": fact["subject"],
                "source_id": fact["sources"][0]["source_id"],
                "excerpt": fact["sources"][0]["excerpt"],
                "captured_at": fact["recorded_at"],
                "id": fact["id"],
                "payload": json.dumps(fact),
                "status": fact["status"],
                "predicate": fact["predicate"],
                "scope_type": fact["scope_type"],
                "scope_id": fact["scope_id"],
                "version": fact["version"],
            },
        )
        return fact

    def ensure_event(self, owner: str, event_id: str, people: list[str]):
        if not self.enabled:
            return
        for person in people:
            self.graph(owner).query(
                """
                MERGE (e:Event {id:$event_id})
                MERGE (p:Person {id:$person_id}) SET p.name=$person
                MERGE (p)-[:ATTENDS]->(e)
            """,
                params={"event_id": event_id, "person_id": person.casefold(), "person": person},
            )

    def record_plan(self, owner: str, plan: dict):
        if not self.enabled:
            return
        self.graph(owner).query(
            """
            MERGE (p:Plan {id:$id}) SET p.revision=$revision, p.status=$status, p.guests=$guests
            MERGE (e:Event {id:$id}) MERGE (p)-[:FOR_EVENT]->(e)
            MERGE (r:Recipe {id:$recipe_id}) SET r.name=$recipe_name
            MERGE (p)-[:USES_RECIPE]->(r)
        """,
            params={
                "id": plan["id"],
                "revision": plan["revision"],
                "status": plan["status"],
                "guests": plan["guests"],
                "recipe_id": plan["recipe"]["id"],
                "recipe_name": plan["recipe"]["name"],
            },
        )
        self.graph(owner).query(
            "MATCH (p:Plan {id:$id})-[r:BASED_ON]->() DELETE r", params={"id": plan["id"]}
        )
        for fact_id in plan["evidence_ids"]:
            self.graph(owner).query(
                """
                MATCH (p:Plan {id:$plan_id}), (a:Assertion {id:$fact_id}) MERGE (p)-[:BASED_ON]->(a)
            """,
                params={"plan_id": plan["id"], "fact_id": fact_id},
            )

    def add(self, owner: str, request: FactInput, source_id: str | None = None, fact_id: str | None = None):
        identifier = fact_id or uid()
        existing = next((f for f in self.all(owner) if f["id"] == identifier), None)
        if existing:
            return existing
        fact = {
            "id": identifier,
            "subject_id": request.subject.casefold(),
            "subject": request.subject,
            "predicate": request.predicate.casefold(),
            "value": request.value,
            "status": "confirmed",
            "scope_type": request.scope_type,
            "scope_id": request.scope_id or request.subject.casefold(),
            "valid_from": now(),
            "recorded_at": now(),
            "version": 1,
            "sources": [
                {"source_id": source_id or uid(), "excerpt": request.source_text, "captured_at": now()}
            ],
        }
        for old in self.current(owner, fact["scope_id"]):
            if (old["subject_id"], old["predicate"], old["scope_type"], old["scope_id"]) == (
                fact["subject_id"],
                fact["predicate"],
                fact["scope_type"],
                fact["scope_id"],
            ):
                old["status"], old["valid_to"] = "superseded", now()
                self.save(owner, old)
                fact["supersedes"] = old["id"]
                fact["version"] = old["version"] + 1
        return self.save(owner, fact)

    def correct(self, owner: str, identifier: str, expected: int, value: str, reason: str):
        old = next((f for f in self.all(owner) if f["id"] == identifier), None)
        if old is None:
            raise KeyError(identifier)
        if old["version"] != expected or old["status"] != "confirmed":
            raise ValueError("This memory has changed. Refresh before editing.")
        return self.add(
            owner,
            FactInput(
                subject=old["subject"],
                predicate=old["predicate"],
                value=value,
                scope_type=old["scope_type"],
                scope_id=old["scope_id"],
                source_text=reason,
            ),
        )

    def forget(self, owner: str, identifier: str):
        fact = next((f for f in self.all(owner) if f["id"] == identifier), None)
        if not fact:
            raise KeyError(identifier)
        if self.enabled:
            self.graph(owner).query("MATCH (a:Assertion {id:$id}) DETACH DELETE a", params={"id": identifier})
            for source in fact["sources"]:
                self.graph(owner).query(
                    """
                    MATCH (s:Source {id:$id}) OPTIONAL MATCH (a:Assertion)-[:SUPPORTED_BY]->(s)
                    WITH s, count(a) AS supports WHERE supports=0 DETACH DELETE s
                """,
                    params={"id": source["source_id"]},
                )
        else:
            self.store.delete(owner, "fact", identifier)
        return fact
