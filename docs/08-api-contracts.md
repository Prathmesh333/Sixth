# API and event contracts

The machine-readable [OpenAPI document](../specs/openapi.json) specifies the proposed HTTP API. [JSON Schemas](../specs/contracts.json) define reusable payload contracts. Both are design artifacts; no server implements them yet.

## Identity and request conventions

All endpoints require a server-validated session. The owner comes from that session, not a request-body user ID. Resolve conversation, task, source, fact and action IDs through ownership checks on every call. Cookie-authenticated mutation requests require CSRF protection. Use HTTPS outside localhost.

Times use RFC3339 with offsets at the API boundary, with an IANA timezone for local scheduling. Normalize graph query times to UTC milliseconds. Monetary amounts use integer minor units plus currency. Ingredient quantities use explicit units; do not add grams and pieces without a conversion rule.

## Main flow

1. POST `/v1/conversations` creates a conversation.
2. POST `/v1/conversations/{conversation_id}/messages` returns a task ID and events URL with HTTP 202.
3. GET `/v1/tasks/{task_id}/events` streams persisted events using SSE.
4. GET `/v1/tasks/{task_id}` retrieves a current snapshot after reconnect.
5. POST `/v1/tasks/{task_id}/decisions` answers a question or reviews an exact action revision.
6. POST `/v1/tasks/{task_id}/cancel` requests cancellation; already-issued effects may need reconciliation.

Mutation requests carry `Idempotency-Key`. Reusing the same key and same body returns the prior response. Reusing it with a different body returns 409. Keys are scoped by owner and route. An action-execution idempotency key is separate from an HTTP retry key.

## Events

SSE event IDs are durable sequence offsets per task. Resume with `Last-Event-ID`. Each event contains task_id, sequence, type, timestamp and payload. Persist before publishing so reconnects do not lose committed state. Deduplicate received events by sequence.

| Event | Payload purpose |
|---|---|
| task.started | Task identity and initial state |
| context.retrieved | Evidence references and unresolved conflicts |
| memory.updated | Fact IDs and update kind |
| plan.updated | Current plan revision and typed steps |
| input.required | Pending question or action preview ID |
| tool.started | Action ID, tool and execution mode |
| tool.completed | Verified result and evidence references |
| tool.failed | Structured failure and retry/reconciliation status |
| task.completed | Completed and outstanding outcomes |
| task.cancelled | Cancellation state and in-flight action status |
| task.failed | Terminal error and recoverable next step |

Do not stream private chain-of-thought. Progress events describe observable work and evidence, such as "Checked calendar availability."

## Review semantics

The server issues a decision ID, action fingerprint, plan revision, expiry and preview. Client decisions carry that reference plus approve/reject or an answer. The server checks ownership, expiry, current plan revision, current evidence versions and exact action arguments. Stale decisions return 409 and a new preview; approval of an old cart cannot authorize an updated cart.

## Memory and deletion

GET `/v1/memory` supports subject and status filters with bounded pagination. PATCH `/v1/memory/{fact_id}` creates a sourced correction with an expected version. DELETE creates a deletion job and suppresses retrieval immediately. GET `/v1/deletions/{job_id}` reports cleanup state. Export is an authenticated download of personal entities, assertions and sources, excluding credentials.

## Errors

Return code, message, request_id and retryable. Use 401 for absent/invalid identity; 403 for denied capability; 404 for inaccessible or missing owned resources; 409 for stale version or idempotency conflict; 422 for invalid input; 429 for budget/rate limits; 503 for unavailable dependencies. Redact provider secrets and avoid exposing another user's resource existence.
