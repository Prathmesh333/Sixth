# Deployment and operations

## Current state

The API and frontend run locally. The root [Compose configuration](../compose.yaml) builds Sixth and starts FalkorDB, but Docker execution has not been verified on this host. The older [infrastructure example](../examples/infra/compose.yaml) starts only FalkorDB. See [implementation status](19-implementation-status.md).

## Local development target

Use Docker Desktop with Linux containers on Windows, an isolated Python environment and a supported Node LTS selected during the compatibility gate. The host's installed Python version is not proof that all agent dependencies support it; start with a Python 3.12 compatibility spike.

1. Select a published FalkorDB image and pin its digest after testing.
2. Copy the example environment template into a local untracked environment file and set the image reference.
3. From examples/infra, run `docker compose --env-file .env up -d`.
4. Confirm database health and use the official client to execute an isolated fixture query.
5. Once implemented, start API, execution/projection workers, frontend and demo store separately.

The example binds database/browser ports to loopback and uses a persistent volume. Its unauthenticated default is for private local development. A remote deployment needs authenticated private networking and tested persistence settings before accepting personal data.

## Deployment target

Host the frontend as static assets. Run API and workers in long-lived containers with persistent operational storage. Keep FalkorDB on a private network or use an appropriately configured managed service. Browser automation belongs on a worker that supports Chromium processes and sufficient memory, not a short-lived function with an assumed persistent filesystem.

Single-node SQLite is acceptable for the private demo. Use one writer/worker and persistent disk; do not mount the same SQLite file across distributed replicas. Move operational state/checkpoints to PostgreSQL before horizontal execution scaling. FalkorDB continues to own personal relationships.

## Persistence and recovery

Mount database and artifact volumes. Select and verify FalkorDB persistence configuration for the pinned image; do not assume a volume alone guarantees durable writes after a crash. Exercise clean restart and abrupt termination. Back up graph, SQL and artifacts with a consistent recovery point; restore into an isolated environment and replay deletion tombstones and pending projections before serving users.

## Health

`/health/live` checks process responsiveness. `/health/ready` checks required storage and worker availability without exposing credentials. Include model/provider connectivity as a distinct capability state; a temporarily unavailable recipe connector need not make memory inspection unavailable.

## Observability

Record task/action IDs, tool versions, state transitions, graph query latency, model tokens, provider cost inputs and verification failures. Redact personal content. Track outbox lag, expired leases, unresolved provider effects, SSE reconnects and deletion-job backlog. Avoid logging every prompt or browser screenshot by default.

## Failure runbook

| Failure | Response |
|---|---|
| FalkorDB unavailable | Stop personalized planning; retain task for retry; do not invent context |
| Worker crash | Reclaim expired lease; reconcile running effects before resume |
| Model budget exhausted | Save partial state and show completed/outstanding steps |
| Browser login expired | Pause for reconnect; keep previous results |
| Graph projection lag | Read ledger for execution truth; retry projection, never action |
| Deletion failure | Suppress retrieval immediately, retry cleanup and expose status |

## Release checklist

Pin versions and images, validate contracts, run graph and replay tests, verify account boundaries, inspect notices, document simulation, and confirm rollback/restore. Use actual observed resource usage to select hosting; no production sizing is implied by this plan.
