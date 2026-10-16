"""Illustrative client query; requires a separately installed, tested falkordb client.

The documentation task syntax-checks this file but does not execute the query.
Never use a browser/model-provided value to choose a production tenant graph.
"""
import os
from datetime import datetime, timezone
from falkordb import FalkorDB


def attendee_context(event_id: str, as_of: int) -> list:
    graph_name = os.environ.get("SIXTH_EXAMPLE_GRAPH", "sixth_fixture_alex")
    if not graph_name.startswith("sixth_fixture_"):
        raise ValueError("This example is restricted to fixture graphs")
    db = FalkorDB(
        host=os.environ.get("FALKORDB_HOST", "127.0.0.1"),
        port=int(os.environ.get("FALKORDB_PORT", "6379")),
    )
    graph = db.select_graph(graph_name)
    result = graph.query(
        """
        MATCH (p:Person)-[:ATTENDS]->(e:Event {id:$event_id}),
              (a:Assertion)-[:HAS_SUBJECT]->(p),
              (a)-[:SUPPORTED_BY]->(s:Source)
        WHERE a.status = 'confirmed'
          AND a.valid_from <= $as_of
          AND (a.valid_to IS NULL OR a.valid_to > $as_of)
          AND (a.scope_type = 'person'
               OR (a.scope_type = 'event' AND a.scope_id = $event_id))
        RETURN p.id, a.id, a.predicate, a.value_json, s.id
        LIMIT 50
        """,
        params={"event_id": event_id, "as_of": as_of},
    )
    return result.result_set


if __name__ == "__main__":
    instant = datetime(2026, 10, 17, 13, 30, tzinfo=timezone.utc)
    print(attendee_context("dinner-01", int(instant.timestamp() * 1000)))
