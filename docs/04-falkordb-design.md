# FalkorDB design and integration

## Integration decision

Use the official Python client over the Redis-compatible protocol and write an explicit Sixth schema. Follow the [official client examples](https://docs.falkordb.com/) and verify supported syntax against the selected server release. Do not assume Neo4j procedures, constraint syntax, or transaction behavior.

Three supported design routes are distinct:

| Route | Role | Sixth decision |
|---|---|---|
| Direct client | Exact domain schema and parameterized traversals | Default for the hackathon |
| Graphiti + FalkorDB | Temporal episodic extraction and hybrid recall | Optional time-boxed integration spike |
| GraphRAG-SDK | Document ingestion and source-grounded retrieval | Later document feature; separate owned graph namespace |

Graphiti already supplies a [FalkorDB driver and example](research/repositories/getzep--graphiti.md). GraphRAG-SDK has its own schema and ingestion pipeline. Neither schema can be treated as interchangeable with the one below.

## Tenant boundary

Allocate `sixth_u_<opaque-server-id>` per authenticated user. The mapping lives in trusted server configuration/SQL. Graphiti, if enabled, uses a separate mapped memory graph and a server-selected group ID; test actual driver routing. A graph name or group filter alone is not authentication. Never accept a graph selector from the browser or model.

## Entities

All domain nodes also carry label `Entity`, stable `id`, `kind`, `name`, `created_at`. Core labels are Person, Event, Place, Recipe, Ingredient, Product, Plan, Task, Action, Outcome, Decision, Source, Episode and Assertion. Node IDs are application-generated UUIDs in production; fixtures use readable IDs.

| Relationship | Meaning |
|---|---|
| KNOWS | User knows a person |
| ATTENDS | Person attends an event |
| HAS_SUBJECT | Assertion concerns an entity |
| HAS_OBJECT | Assertion references another entity when applicable |
| SUPPORTED_BY | Assertion or outcome points to a source |
| SUPERSEDES | New assertion replaces a prior one |
| HAS_TASK | Plan contains a task |
| DEPENDS_ON | Task depends on another task or entity |
| BASED_ON | Plan, task or decision uses an assertion |
| HAS_ACTION | Task contains an executable action |
| PRODUCED | Action produced an outcome |
| USES | Recipe uses an ingredient, with unit and quantity properties |

## Assertions and time

An Assertion stores `id`, `predicate`, `value_json`, `status`, `confidence`, `valid_from`, optional `valid_to`, `recorded_at`, `scope_type`, `scope_id`, `sensitivity`, and `version`. Status is proposed, confirmed, superseded or disputed. Times use UTC epoch milliseconds in queries; retain the original timezone in source metadata.

`valid_from` describes when a fact applies. `recorded_at` describes when Sixth learned it. A temporary "no dairy at this dinner" assertion must not replace a general dietary preference. Supersession applies only to the same subject, predicate, scope and overlapping effective interval. Different sources can disagree; a recent statement is not automatically true.

Source nodes hold artifact ID, message/provider reference, capture time, hash and optional excerpt offsets. Store full private text in protected artifact storage, not in every graph node. Confidence is an extraction estimate, not a probability of truth or a substitute for confirmation.

## Retrieval contract

A context bundle returns entities, current assertions, evidence paths, unresolved conflicts, plan revision and retrieval time. Bound traversals to known relationships and at most three hops initially; limit result count and payload bytes. Seed retrieval with exact entity IDs or alias matches, optionally augmented by full-text/vector search after version-specific tests.

See [seed](../examples/graph/seed.cypher), [queries](../examples/graph/queries.cypher), and [client example](../examples/graph/query_example.py). These are illustrative and require a live-server smoke test. No query was executed against FalkorDB during this documentation task.

## Writes and identity

Use parameter values, static labels/relationship names, stable IDs, and application validation. Serialize writes per tenant in the initial implementation; do not assume MERGE alone prevents concurrent duplicate entities. Create indexes only with syntax verified against the pinned server; indexes accelerate lookup and are not an identity-resolution policy.

## Correction, deletion and backup

Correction adds a new assertion and closes the previous validity interval when justified. Forget removes the selected assertion, derived embeddings, cached retrieval, and attributable graph projections. Deleting a source requires removing or recalculating facts that lose all support. Preserve a content-free audit marker; do not preserve the forgotten content in logs or checkpoints. Backup retention and restore-time tombstone replay are specified in [privacy](11-security-and-privacy.md).
