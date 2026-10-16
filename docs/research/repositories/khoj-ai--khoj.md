# Khoj

Repository: [khoj-ai/khoj](https://github.com/khoj-ai/khoj)  
Category: Personal assistant  
Inspected commit: `ae229ca894c0b80ad84664afcfdde523b5e87057`  
Upstream commit timestamp: 2026-08-02T01:55:40Z  
License text inspected: AGPL-3.0

## Problem and implementation

Combines personal-document retrieval, web research, conversations and automation in a self-hostable assistant.

The tree separates Python services under src/khoj from the web interface under src/interface/web. api_chat.py retrieves recent and relevant long-term memories before answering. A separate grounding agent handles browser observations; Compose defines a sandbox service.

## Published direction

README positions the product around personal knowledge and autonomous assistance. No standalone delivery roadmap was verified in the inspected files.

## Application to Sixth

Borrow the continuous experience between recall and action. Implement Sixth context retrieval behind a dedicated service and render its source references in chat.

Do not fork the full product for this deadline or assume its memory storage is FalkorDB. Keep this as an architectural reference; the inspected license is AGPL-3.0.

## Repository structure

Selected directories in the pinned tree:

```text
src/khoj/
src/interface/web/
documentation/
tests/
```

[Browse the pinned tree](https://github.com/khoj-ai/khoj/tree/ae229ca894c0b80ad84664afcfdde523b5e87057). This is a selected map, not the complete repository.

## Evidence inspected

- [src/khoj/routers/api_chat.py](https://github.com/khoj-ai/khoj/blob/ae229ca894c0b80ad84664afcfdde523b5e87057/src/khoj/routers/api_chat.py)
- [src/khoj/processor/operator/grounding_agent.py](https://github.com/khoj-ai/khoj/blob/ae229ca894c0b80ad84664afcfdde523b5e87057/src/khoj/processor/operator/grounding_agent.py)
- [docker-compose.yml](https://github.com/khoj-ai/khoj/blob/ae229ca894c0b80ad84664afcfdde523b5e87057/docker-compose.yml)
- [README.md](https://github.com/khoj-ai/khoj/blob/ae229ca894c0b80ad84664afcfdde523b5e87057/README.md)
- [LICENSE](https://github.com/khoj-ai/khoj/blob/ae229ca894c0b80ad84664afcfdde523b5e87057/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
