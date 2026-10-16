# Skyvern

Repository: [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern)  
Category: Browser workflows  
Inspected commit: `74ef06fc8f220d200a8479de62beb30041042cf6`  
Upstream commit timestamp: 2026-10-16T14:42:02Z  
License text inspected: AGPL-3.0

## Problem and implementation

Automates browser tasks and reusable workflows with structured run results.

The Python forge agent and workflow service separate individual browser execution from workflow dispatch and retries. The inspected services include step verification, artifact handling, state recovery and workflow-attempt bookkeeping. A frontend and database migrations support the broader product.

## Published direction

The README describes task, workflow and SDK surfaces. No standalone future delivery roadmap was verified; enterprise/cloud features must not be assumed to exist in the core distribution.

## Application to Sixth

Borrow workflow-level result records and terminal-state reconciliation. Sixth can adopt those boundaries without importing the entire service.

The full runtime is heavy for this event and overlaps with browser-use plus LangGraph. Keep it as an alternative/reference, not a second simultaneous browser backend.

## Repository structure

Selected directories in the pinned tree:

```text
skyvern/forge/
skyvern/webeye/
skyvern-frontend/
alembic/
integrations/
```

[Browse the pinned tree](https://github.com/Skyvern-AI/skyvern/tree/74ef06fc8f220d200a8479de62beb30041042cf6). This is a selected map, not the complete repository.

## Evidence inspected

- [skyvern/forge/agent.py](https://github.com/Skyvern-AI/skyvern/blob/74ef06fc8f220d200a8479de62beb30041042cf6/skyvern/forge/agent.py)
- [skyvern/forge/sdk/workflow/service.py](https://github.com/Skyvern-AI/skyvern/blob/74ef06fc8f220d200a8479de62beb30041042cf6/skyvern/forge/sdk/workflow/service.py)
- [README.md](https://github.com/Skyvern-AI/skyvern/blob/74ef06fc8f220d200a8479de62beb30041042cf6/README.md)
- [LICENSE](https://github.com/Skyvern-AI/skyvern/blob/74ef06fc8f220d200a8479de62beb30041042cf6/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
