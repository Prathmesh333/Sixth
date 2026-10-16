# Cognee

Repository: [topoteretes/cognee](https://github.com/topoteretes/cognee)  
Category: Knowledge ingestion  
Inspected commit: `f154b32a9e544dac73e7ddf2010327cf9988edcd`  
Upstream commit timestamp: 2026-10-13T15:20:39Z  
License text inspected: Apache-2.0

## Problem and implementation

Builds retrievable memory from source data through ingestion and graph-processing pipelines.

cognify.py constructs tasks for classifying documents, extracting chunks, extracting graph data and loading results. Provenance and contradiction handling are configurable. search.py exposes multiple retrieval modes, including hybrid completion.

## Published direction

The README offers several deployment and agent-entry paths. Some storage capabilities are labeled demo or licensed; inspect those boundaries before adoption. No standalone dated roadmap was verified.

## Application to Sixth

Borrow staged ingestion, explicit provenance and separation of extraction from retrieval. Sixth should validate candidate assertions before making them planning constraints.

Do not run Cognee alongside another extraction engine for the same facts. A FalkorDB adapter is not assumed from this review; verify provider support before proposing a direct integration.

## Repository structure

Selected directories in the pinned tree:

```text
cognee/api/
cognee/infrastructure/
cognee/modules/
cognee-frontend/
cognee-mcp/
evals/
```

[Browse the pinned tree](https://github.com/topoteretes/cognee/tree/f154b32a9e544dac73e7ddf2010327cf9988edcd). This is a selected map, not the complete repository.

## Evidence inspected

- [cognee/api/v1/cognify/cognify.py](https://github.com/topoteretes/cognee/blob/f154b32a9e544dac73e7ddf2010327cf9988edcd/cognee/api/v1/cognify/cognify.py)
- [cognee/api/v1/search/search.py](https://github.com/topoteretes/cognee/blob/f154b32a9e544dac73e7ddf2010327cf9988edcd/cognee/api/v1/search/search.py)
- [README.md](https://github.com/topoteretes/cognee/blob/f154b32a9e544dac73e7ddf2010327cf9988edcd/README.md)
- [LICENSE](https://github.com/topoteretes/cognee/blob/f154b32a9e544dac73e7ddf2010327cf9988edcd/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
