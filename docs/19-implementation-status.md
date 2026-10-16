# Implementation status

October 16, 2026. This is the current implementation record; earlier design documents describe the broader product target.

## Working locally

- React 19 + TypeScript + Vite interface with chat, Memory, Plans, Settings and an evidence panel.
- Three themes, responsive navigation, keyboard-accessible controls and visible fixture/sandbox labels.
- FastAPI session boundary, separate Alex/Jordan demo accounts, ownership checks and CSRF-protected mutations.
- Durable sourced memory with explicit correction, supersession and forgetting.
- LangGraph execution with persistent SQLite checkpoints and resumption from action review after restart.
- Fixture calendar and recipe catalog; guest-count scaling, temporary restrictions, pantry subtraction and unsupported-constraint handling.
- A reviewed sandbox cart with transactional verification, a unique action ledger and replay-safe retries.
- Persisted SSE task events, reconnect offsets, conversations, plans and account-specific exports.
- An optional OpenAI-compatible model adapter for typed intent parsing. Without a configured model, the UI labels the deterministic local planner.

## FalkorDB implementation

The native client adapter is implemented. It selects server-owned per-user graph names and stores people, sources and assertions. Dinner context traverses Event <- ATTENDS - Person <- HAS_SUBJECT - Assertion -> SUPPORTED_BY - Source. Plans link back to the assertions and recipes behind their decisions. Verified cart outcomes use an idempotent projection outbox.

FalkorDB mode fails closed when unavailable; it never substitutes fixture memory. A real-server integration test and a dedicated CI database job are included. Local graph execution remains unverified because Docker is absent and the registered WSL distribution cannot mount its missing disk. Container image digest pinning remains a release gate.

## Verification

- Eight API/application tests pass, including correction, isolation, stale reviews, idempotency, event replay, timezone validation, unsupported restrictions and restart/resume.
- The browser workflow passes against real local API/frontend processes, with isolated test data.
- Browser layout checks cover 320, 768, 1024 and 1440 pixels without horizontal document overflow.
- Axe checks found no WCAG A/AA violations on the welcome and checked settings screens across the supplied themes. This is not a full accessibility certification.
- TypeScript and production frontend build pass. Python Ruff checks pass.
- React Doctor full scan reports 100/100 after fixing the identified issues.

## Not yet verified or implemented

- Live model-provider calls require server-side configuration and have not been exercised.
- The Docker build/Compose path is supplied but has not run on this host.
- Browser-use execution, real calendar OAuth, real merchant integrations, voice and messaging are not implemented.
- File ingestion, arbitrary task execution, advanced temporal/entity resolution, and Graphiti integration remain future work.
- Production authentication, distributed workers, comprehensive rate limits, encrypted credential storage and backup/deletion policies remain deployment work.
- The first catalog and schedule are a controlled dinner scenario, not a complete travel, gifts or household assistant.

## Implementation boundaries

Operational storage is SQLite. Fixture memory also uses SQLite only in the explicitly selected fixture mode. The sandbox store is an in-process local provider; its mutation and action-ledger write share one transaction. Those guarantees do not establish exactly-once behavior for external merchants.

The original draft OpenAPI specification covers the planned product. FastAPI's `/openapi.json` is the implemented API. The current model adapter classifies requests; deterministic typed code owns planning and action permissions. General responses do not execute arbitrary tools.

The forgetting operation removes the selected assertion and attributable source/conversation context and invalidates affected plans. It is not an implemented account-deletion or backup-erasure system. Historical assertions are separately inspectable through the API.

## Next implementation gates

Verify the graph job against a real database, exercise a configured model, then add browser execution against a controlled storefront. Add live calendar read access only after the core loop stays reliable. Keep the sample/live distinction visible as each integration arrives.
