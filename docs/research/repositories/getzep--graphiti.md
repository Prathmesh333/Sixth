# Graphiti

Repository: [getzep/graphiti](https://github.com/getzep/graphiti)  
Category: Temporal graph memory  
Inspected commit: `d50741d1bf463cbe3859eb73914cbff1b66839e6`  
Upstream commit timestamp: 2026-10-15T19:00:06Z  
License text inspected: Apache-2.0

## Problem and implementation

Turns episodes into temporal graph memory and retrieves connected facts for agent context.

graphiti_core/graphiti.py exposes episode ingestion, triplets and search. FalkorDriver provides a native FalkorDB implementation with backend-specific operations. The quickstart initializes Graphiti with that driver. The MCP server exposes episode and entity tools and documents grouped retrieval.

## Published direction

The MCP README labels that server experimental. The inspected files document supported backends and setup, not a guaranteed future schedule.

## Application to Sixth

Run an optional spike for temporal extraction and memory retrieval. Wrap results in Sixth's evidence contract and verify graph/group routing, correction and deletion.

Do not treat group_id as authentication or write Sixth domain nodes into Graphiti's internal schema. Keep its extraction as one owned memory route if selected, rather than duplicating facts across engines.

## Repository structure

Selected directories in the pinned tree:

```text
graphiti_core/
graphiti_core/driver/falkordb/
mcp_server/
server/
examples/
```

[Browse the pinned tree](https://github.com/getzep/graphiti/tree/d50741d1bf463cbe3859eb73914cbff1b66839e6). This is a selected map, not the complete repository.

## Evidence inspected

- [graphiti_core/graphiti.py](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/graphiti_core/graphiti.py)
- [graphiti_core/driver/falkordb_driver.py](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/graphiti_core/driver/falkordb_driver.py)
- [examples/quickstart/quickstart_falkordb.py](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/examples/quickstart/quickstart_falkordb.py)
- [mcp_server/README.md](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/mcp_server/README.md)
- [mcp_server/docker/docker-compose-falkordb.yml](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/mcp_server/docker/docker-compose-falkordb.yml)
- [README.md](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/README.md)
- [LICENSE](https://github.com/getzep/graphiti/blob/d50741d1bf463cbe3859eb73914cbff1b66839e6/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
