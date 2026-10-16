# Evaluation and test plan

No application tests have run because the application is not implemented. The [validation report](validation-report.md) covers documentation artifacts only.

## Prove the graph changes actions

Run identical requests through three conditions with the same model and tools: no personal context; top-k source text; Sixth graph context with source-backed traversals. Use fixed fixtures and record model parameters. Score actual structured outputs against expected constraints, not the model's confidence.

Measure dietary constraints met, correct quantities, relevant sources, unresolved ambiguity, action success, duplicate effects, latency and cost. A small curated experiment supports a demo claim, not a broad superiority claim over vector retrieval.

## Initial scenario suite

| Scenario | Expected behavior |
|---|---|
| Remember Maya | Attach preference to correct person and source |
| Two Mayas | Ask for disambiguation; do not merge |
| Temporary dietary request | Apply to dinner only |
| Persistent correction | Supersede scoped old assertion and replan |
| New guest count | Recalculate servings and shopping quantities |
| Calendar conflict | Explain overlap using timestamped events |
| Pantry stock | Subtract compatible units correctly |
| New session | Retrieve durable facts without old transcript |
| Worker restart | Resume without a duplicate cart effect |
| Provider timeout | Reconcile before retry |
| Rejected action | Preserve decision and avoid executing it |
| Plan change after review | Reject stale approval |
| Forget source | Remove unsupported memory from future retrieval |
| Cross-user request | Return no other user's facts or events |
| Prompt injection | Ignore page instructions requesting unrelated data |
| Tool unavailable | Explain limitation and preserve partial plan |

## Test layers

Unit-test assertion scope/time decisions, deterministic quantity conversion, argument validation and action fingerprints. Integration-test real FalkorDB queries, SQL uniqueness/leases/outbox, schema migrations, deletion and tenant routing. End-to-end test chat-to-plan-to-review-to-verified-cart and reconnect/restart behavior. Stub model responses for deterministic execution tests; run a separate live-model evaluation for extraction/planning quality.

## Memory benchmark

Prepare at least twenty sourced facts across two users, including overlapping names, changed preferences, temporary constraints and disputed statements. Query expected current and historical facts. Report precision and recall against a manually labeled fixture, missing evidence count and cross-user leakage. Preserve dataset and failures so improvements can be compared.

## Replay experiment

Crash the worker before tool dispatch, after dispatch but before result storage, after SQL commit, and before graph projection. Verify ledger states and provider cart state for every crash point. Provider actions without idempotency support must demonstrate reconciliation or explicit unresolved status.

## Acceptance gates

All deterministic tests pass; zero tenant leaks or duplicate mutations in the test suite; every personalized demo recommendation has a valid source; corrections change affected plans; forgotten data is unavailable in new sessions; simulated results are labeled. Establish latency and token baselines and report actual values after implementation.

## Interface verification

Test keyboard navigation, mobile layout at 360px width, large text, focus restoration after sheets, screen-reader state updates and theme contrast. Check the evidence list independently of the graph canvas. Automated checks supplement manual verification; neither is currently claimed complete.
