# Letta Code

Repository: [letta-ai/letta-code](https://github.com/letta-ai/letta-code)  
Category: Stateful agents  
Inspected commit: `1297870b0aa6662d6c70729d273f5073c1bcbdea`  
Upstream commit timestamp: 2026-10-16T05:24:29Z  
License text inspected: Apache-2.0

## Problem and implementation

Provides a stateful agent harness with persistent identity, editable context and multiple interaction channels.

The README describes memory blocks, message search and Git-tracked MemFS. Workflow implementation separates tool dispatch from an execution engine and bounded scheduling. The old letta repository directs active projects here and preserves the former API server on an archive branch.

## Published direction

Current documentation describes self-configuration, channels and memory evolution. No standalone delivery schedule was verified; the retired API architecture should not be presented as current.

## Application to Sixth

Borrow explicit memory inspection, multi-session continuity and discoverable action state. Sixth should keep executable policy outside model-editable memory.

Letta's context system is not a drop-in FalkorDB backend. Avoid introducing a second persistent agent platform when LangGraph and Sixth memory already own those responsibilities.

## Repository structure

Selected directories in the pinned tree:

```text
src/tools/
src/channels/
src/cli/
src/skills/
```

[Browse the pinned tree](https://github.com/letta-ai/letta-code/tree/1297870b0aa6662d6c70729d273f5073c1bcbdea). This is a selected map, not the complete repository.

## Evidence inspected

- [src/tools/impl/workflow.ts](https://github.com/letta-ai/letta-code/blob/1297870b0aa6662d6c70729d273f5073c1bcbdea/src/tools/impl/workflow.ts)
- [src/tools/workflow/workflow-engine.ts](https://github.com/letta-ai/letta-code/blob/1297870b0aa6662d6c70729d273f5073c1bcbdea/src/tools/workflow/workflow-engine.ts)
- [README.md](https://github.com/letta-ai/letta-code/blob/1297870b0aa6662d6c70729d273f5073c1bcbdea/README.md)
- [LICENSE](https://github.com/letta-ai/letta-code/blob/1297870b0aa6662d6c70729d273f5073c1bcbdea/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
