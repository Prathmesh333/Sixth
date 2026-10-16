# Proposed codebase structure

This is the intended application layout. Only docs, specs, design tokens and examples exist today.

```text
sixth/
  apps/
    web/
      src/
        app/                  # Routes, providers and responsive shell
        features/chat/        # Composer, messages and stream adapter
        features/actions/     # Action previews and outcomes
        features/memory/      # Inspect, correct and forget
        features/plans/       # Active plans and revisions
        components/           # Shared interface primitives
    api/
      sixth/
        api/                  # HTTP endpoints, sessions and SSE
        runtime/              # LangGraph stages and typed task state
        memory/               # Assertion service and context bundles
        graph/                # FalkorDB repository and query templates
        tools/                # Registry, policy, runner and verification
        connectors/           # Calendar, recipes, store and MCP adapters
        storage/              # SQL ledger, checkpoints, outbox and artifacts
        workers/              # Execution, projection and deletion jobs
        observability/        # Redacted events, traces and usage
  services/
    demo-store/               # Test storefront and independent cart API
  packages/
    contracts/                # Generated TypeScript API types
  tests/
    unit/
    integration/
    e2e/
    evaluations/
  examples/                   # Current documentation examples
  specs/                      # Current contracts
  design/                     # Current semantic tokens and themes
  docs/                       # Current product and implementation documents
```

## Dependency direction

API routes call application services. Runtime nodes call memory and tools through interfaces. Tool adapters cannot choose the current user or bypass policy. Graph repositories accept trusted scope and validated domain arguments. Browser execution is a worker dependency, not an import inside a UI component.

Keep MemoryBackend, CalendarAdapter, RecipeCatalog, StoreAdapter, BrowserExecutor and ActionLedger interfaces small. Add a new skill by supplying typed tools and planning guidance; do not add another agent framework for each use case.

## Contracts and migrations

Generate frontend types from the OpenAPI contract after schema validation. Version API and graph schema changes. Use idempotent migration jobs with a recorded schema version per graph. Backfill new relationships before relying on them in queries. Never let an LLM issue schema migrations.

## Configuration

Validate environment variables at startup. Distinguish provider configuration, runtime budgets, tool permissions and user preferences. Tests can inject fixture adapters without conditional logic scattered through production services. Pin Python and Node dependencies in lockfiles after the first working compatibility test.

## Contributions

A change should include user behavior, relevant contract changes, an appropriate test, and evidence of any new integration working. Do not count documentation examples as implemented features in the main application README. Preserve upstream notices when actual code is incorporated.
