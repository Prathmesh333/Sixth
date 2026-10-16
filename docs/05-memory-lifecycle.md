# Memory lifecycle

## Four kinds of state

Working state is the active request and recent tool observations. Episodic memory records what happened, such as a cart revision or rejected suggestion. Semantic memory contains sourced facts about people and preferences. Procedural memory contains reusable, verified task methods. Workflow checkpoints are execution state and belong in operational storage, not an LLM summary pretending to be durable execution.

## Ingestion

1. Persist the source with ownership, capture time and a stable ID.
2. Extract candidate entities and assertions into a validated structure.
3. Resolve identity through exact connector IDs first, then scoped aliases. Ask when ambiguous.
4. Check scope, time, contradictions and sensitivity.
5. Confirm explicit user facts where unambiguous; leave inferred facts proposed.
6. Write assertions and source links idempotently.
7. Emit a visible memory update and invalidate relevant cached plans.

Connector observations establish provider state at a time. They cannot establish a user's general preference. Model output is never independent evidence for its own claim.

## Retrieval

Resolve who and what the request concerns. Retrieve current confirmed assertions and relevant plan history; bring disputed facts back as questions, not constraints. Include source IDs and short explanations in a bounded context bundle. Refresh time-sensitive external state before acting.

Rank by subject match, scope, effective time, source quality, and relevance. Do not retrieve all facts about a user into every tool call. A browser shopping task does not need their entire calendar or private relationship history.

## A correction example

An old assertion says Maya prefers dairy-based desserts. A new direct message says Maya now avoids dairy. Confirm that it is a persistent change, then write a new assertion, link SUPERSEDES, and close the old interval. Plans BASED_ON the old assertion become stale. Invalidate pending approvals if their action arguments change.

The next session retrieves the new assertion. A historical question can still explain the earlier menu, unless the user requested deletion.

## Forget is different from supersede

Forgetting should remove content from graph assertions, source artifacts when requested, search indexes, prompt caches, conversation-derived summaries, exported artifacts under our control, and checkpoint snapshots that contain it. If selective checkpoint rewriting is unsafe, remove affected checkpoints and mark tasks for safe reconstruction from a redacted ledger.

A deletion job has queued/running/completed/failed state. Reads suppress tombstoned items immediately. Retained backups follow a disclosed retention policy; restored data must replay tombstones before becoming available. Do not claim instantaneous physical deletion from immutable backups.

## Optional Graphiti integration

Keep a MemoryBackend interface: ingest_episode, search_context, correct_assertion, forget_source, health. A Graphiti adapter must return Sixth's evidence bundle and respect tenant, scope and deletion semantics. Graphiti owns its graph schema; avoid writing Sixth assertions directly into its internal nodes. Only one backend owns a given memory fact. Passing the spike is required before changing the default architecture.

## Procedural learning

After repeated verified success, propose a reusable method with prerequisites and tool versions. Save failures as outcomes, not permanent prohibitions. A model must not rewrite executable tool definitions, connector permissions, or approval policy based on a conversation.

Design references: [Graphiti](research/repositories/getzep--graphiti.md), [Mem0](research/repositories/mem0ai--mem0.md), [Cognee](research/repositories/topoteretes--cognee.md), [Letta Code](research/repositories/letta-ai--letta-code.md).
