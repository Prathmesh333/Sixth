# GraphRAG SDK

Repository: [FalkorDB/GraphRAG-SDK](https://github.com/FalkorDB/GraphRAG-SDK)  
Category: FalkorDB document retrieval  
Inspected commit: `35e67a0b27fdcc7f2c28508b09e86169851a8187`  
Upstream commit timestamp: 2026-10-14T12:40:01Z  
License text inspected: Apache-2.0

## Problem and implementation

Ingests documents into FalkorDB and retrieves evidence for grounded answers.

The architecture document separates strategy-based ingestion and retrieval. LexicalGraphWriter creates document/chunk provenance. Extracted entities use __Entity__; semantic relations use RELATES with a rel_type property. This differs from Sixth's proposed explicit assertion schema.

## Published direction

The README lists milestones, including Q4 2026 temporal/dynamic retrieval. Treat milestone entries as roadmap statements unless implemented behavior is separately verified.

## Application to Sixth

Consider a later document-ingestion adapter in its own graph namespace. Map retrieved source references into Sixth's evidence bundle.

Do not mix generated SDK graph writes with Sixth domain writes without a translation layer. Its own benchmark figures have not been reproduced and do not establish Sixth accuracy.

## Repository structure

Selected directories in the pinned tree:

```text
graphrag_sdk/src/graphrag_sdk/
graphrag_sdk/tests/
docs/
assets/
```

[Browse the pinned tree](https://github.com/FalkorDB/GraphRAG-SDK/tree/35e67a0b27fdcc7f2c28508b09e86169851a8187). This is a selected map, not the complete repository.

## Evidence inspected

- [docs/architecture.mdx](https://github.com/FalkorDB/GraphRAG-SDK/blob/35e67a0b27fdcc7f2c28508b09e86169851a8187/docs/architecture.mdx)
- [graphrag_sdk/src/graphrag_sdk/retrieval/router.py](https://github.com/FalkorDB/GraphRAG-SDK/blob/35e67a0b27fdcc7f2c28508b09e86169851a8187/graphrag_sdk/src/graphrag_sdk/retrieval/router.py)
- [graphrag_sdk/src/graphrag_sdk/ingestion/lexical_graph.py](https://github.com/FalkorDB/GraphRAG-SDK/blob/35e67a0b27fdcc7f2c28508b09e86169851a8187/graphrag_sdk/src/graphrag_sdk/ingestion/lexical_graph.py)
- [README.md](https://github.com/FalkorDB/GraphRAG-SDK/blob/35e67a0b27fdcc7f2c28508b09e86169851a8187/README.md)
- [LICENSE](https://github.com/FalkorDB/GraphRAG-SDK/blob/35e67a0b27fdcc7f2c28508b09e86169851a8187/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
