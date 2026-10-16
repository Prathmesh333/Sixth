# Risks and open decisions

## Highest risks

| Risk | Mitigation | Evidence needed |
|---|---|---|
| Broad product, unfinished demo | One complete calendar/meal/cart loop | End-to-end verified outcome |
| Graph is decorative | Compare plans before and after graph fact correction | Changed query result and action |
| Wrong person or preference | Stable IDs, scoped assertions, ambiguity questions | Duplicate-name tests |
| Duplicate action after restart | Ledger, provider idempotency, reconciliation | Crash-point suite |
| Stale or conflicting memory | Effective dates, sources, explicit supersession | Temporal fixture tests |
| Browser automation instability | Bounded test store and direct API alternative | Execution trace and verification |
| Personal data leakage | Trusted identity, isolated graphs/sessions, minimal context | Tenant and injection tests |
| Dependency/API drift | Pin tested releases; source snapshots are references | Compatibility record |
| Licensing assumptions | Inspect actual license files and notices | Dependency inventory |
| Misleading demo | Visible fixture/sandbox/live modes | Screenshots and accurate narration |

## Decisions that can use defaults

Use web chat, Dusk theme, English text, synthetic fixture data, Python backend and explicit graph memory. Keep voice, messaging, real purchases and production identity as later capabilities. None requires blocking documentation or initial implementation.

## Decisions requiring evidence during build

- Which pinned FalkorDB image and Python client pass the example queries and restart test?
- Which model reliably emits the schemas at acceptable measured cost?
- Does the selected LangGraph SQLite checkpointer work on the chosen runtime?
- Does assistant-ui's current custom runtime fit the FastAPI event stream without another backend layer?
- Does browser-use reach the test store reliably in the deployment environment?
- Does Graphiti's extra complexity improve temporal extraction enough to adopt?

## Product decisions for later user input

Preferred long-term channel, first live connector, hosting budget, desired autonomous permissions, and whether household sharing belongs in version one. These do not change the recommended hackathon core.

## Completion definition for this documentation task

At least ten repository implementation reviews with traceable sources; a product and architecture recommendation; FalkorDB schema and integration options; execution/memory/privacy contracts; interface themes; build and demo plans; supporting machine-readable examples; and a validation report that states what was and was not tested. Building the application is a subsequent task.
