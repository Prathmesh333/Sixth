# Architecture decision records

Status: recommended, pending implementation smoke tests. Source evidence appears in the [research register](research/sources.md).

## ADR-001: Explicit FalkorDB personal graph

Decision: use the official client and Sixth's assertion schema as the baseline. Reason: predictable source paths, constraints and correction semantics. Alternative: Graphiti-managed extraction. Consequence: we own entity resolution and temporal rules; Graphiti remains a time-boxed spike.

## ADR-002: Separate workflow state from knowledge

Decision: LangGraph checkpoints plus SQL action ledger; personal relationships stay in FalkorDB. Reason: resuming computation and recalling facts are different concerns. Alternative: store everything in a graph. Consequence: cross-store projection requires an outbox and idempotent graph updates.

## ADR-003: One coordinator before multiple agents

Decision: one orchestrator with typed stages and bounded tools. Reason: a clear execution trace and fewer moving parts. Alternative: independent planner/researcher/executor agents. Consequence: specialist nodes can be introduced when a measured need justifies a handoff.

## ADR-004: API before browser when practical

Decision: direct adapters for reliable structured operations; browser-use for a bounded test-store route and later unsupported sites. Reason: provider state can be verified and retries controlled. Alternative: browser-only execution. Consequence: both paths implement the same action/result contract and disclose the actual route.

## ADR-005: No overlapping memory engines

Decision: do not combine Mem0, Cognee, Letta, Graphiti and GraphRAG-SDK on the same fact stream. Reason: conflicting ownership, deletion and extraction semantics. Consequence: alternatives stay behind MemoryBackend or a separate document adapter.

## ADR-006: Chat-first with inspectable state

Decision: one conversational surface plus Plans, Memory and contextual evidence. Reason: preserve the low-friction Instinct inspiration while enabling correction. Alternative: a graph-first dashboard. Consequence: graph visualization remains optional and has a textual equivalent.

## ADR-007: Authenticated graph selection

Decision: backend selects an opaque per-user graph name. Reason: model/user-controlled graph selection risks leakage. Alternative: shared graph with filters. Consequence: graph migration and deletion jobs operate per user; graph keys do not replace authorization.

## ADR-008: Local demo before production platform

Decision: persistent single-node operational storage and a test storefront. Reason: finish and verify the full loop during the event. Alternative: distributed queues, production merchants and many channels. Consequence: scaling/auth/merchant rollout has explicit gates after the hackathon.

## ADR-009: Original interface themes

Decision: original Dusk/Paper/Grove semantic tokens, optional assistant-ui primitives. Reason: distinct identity with a small component surface. Alternative: fork an entire assistant frontend. Consequence: check actual package licenses before reuse and verify accessibility in rendered screens.
