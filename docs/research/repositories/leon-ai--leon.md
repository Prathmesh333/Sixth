# Leon

Repository: [leon-ai/leon](https://github.com/leon-ai/leon)  
Category: Personal assistant  
Inspected commit: `21baf11714f618a9367f25882e59e856d3308037`  
Upstream commit timestamp: 2026-10-12T12:24:27Z  
License text inspected: MIT

## Problem and implementation

Provides a personal assistant with declared tools, context, layered memory and ongoing agent execution.

The architecture document describes client-agnostic Socket.IO, per-profile runtimes and tools organized into skills, actions and functions. agent-loop.ts implements the continuing tool transcript. Dedicated runtime guards handle structured observations, repeated calls and bounded continuation.

## Published direction

The README warns that older documentation reflects a legacy architecture. Current architecture notes describe the rebuild; the linked external roadmap was not independently audited.

## Application to Sixth

Borrow tool availability checks, per-user services, progressive tool loading and observation-based completion. Sixth uses its own FalkorDB context service instead of adopting the QMD-backed memory layout.

Copying the entire voice/device stack would expand the event scope. Treat personality and autonomous pulse work as later product choices.

## Repository structure

Selected directories in the pinned tree:

```text
server/
core/context/
tools/
bridges/
web-app/
tcp_server/
```

[Browse the pinned tree](https://github.com/leon-ai/leon/tree/21baf11714f618a9367f25882e59e856d3308037). This is a selected map, not the complete repository.

## Evidence inspected

- [core/context/ARCHITECTURE.md](https://github.com/leon-ai/leon/blob/21baf11714f618a9367f25882e59e856d3308037/core/context/ARCHITECTURE.md)
- [server/src/core/llm-manager/llm-duties/react-llm-duty/agent-loop.ts](https://github.com/leon-ai/leon/blob/21baf11714f618a9367f25882e59e856d3308037/server/src/core/llm-manager/llm-duties/react-llm-duty/agent-loop.ts)
- [README.md](https://github.com/leon-ai/leon/blob/21baf11714f618a9367f25882e59e856d3308037/README.md)
- [LICENSE.md](https://github.com/leon-ai/leon/blob/21baf11714f618a9367f25882e59e856d3308037/LICENSE.md)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
