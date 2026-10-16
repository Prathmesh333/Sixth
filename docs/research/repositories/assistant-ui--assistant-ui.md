# assistant-ui

Repository: [assistant-ui/assistant-ui](https://github.com/assistant-ui/assistant-ui)  
Category: Chat interface  
Inspected commit: `2f3690c03954cac275f9bf9c26d81a18fc1e5ec0`  
Upstream commit timestamp: 2026-10-16T11:27:42Z  
License text inspected: MIT

## Problem and implementation

Provides reusable conversation UI and runtime adapters for agent-backed applications.

The tree separates core runtime interfaces, React components, provider adapters and examples. A LangGraph runtime adapter manages streaming/checkpoint-related interaction; external-store runtime support offers a boundary for custom state.

## Published direction

The README documents installation, backend options and customization. No standalone future delivery roadmap was verified.

## Application to Sixth

Evaluate chat primitives and tool-result cards for Sixth. If the custom FastAPI stream does not match a built-in adapter, write a small external-store adapter rather than assuming wire compatibility.

This library does not supply authentication, personal memory, connector policy or backend durability. Start with only the components needed for Sixth's conversational experience.

## Repository structure

Selected directories in the pinned tree:

```text
packages/core/
packages/react/
packages/react-langgraph/
packages/ui/
examples/
apps/docs/
```

[Browse the pinned tree](https://github.com/assistant-ui/assistant-ui/tree/2f3690c03954cac275f9bf9c26d81a18fc1e5ec0). This is a selected map, not the complete repository.

## Evidence inspected

- [packages/react-langgraph/src/useLangGraphRuntime.ts](https://github.com/assistant-ui/assistant-ui/blob/2f3690c03954cac275f9bf9c26d81a18fc1e5ec0/packages/react-langgraph/src/useLangGraphRuntime.ts)
- [packages/core/src/react/runtimes/useExternalStoreRuntime.ts](https://github.com/assistant-ui/assistant-ui/blob/2f3690c03954cac275f9bf9c26d81a18fc1e5ec0/packages/core/src/react/runtimes/useExternalStoreRuntime.ts)
- [README.md](https://github.com/assistant-ui/assistant-ui/blob/2f3690c03954cac275f9bf9c26d81a18fc1e5ec0/README.md)
- [LICENSE](https://github.com/assistant-ui/assistant-ui/blob/2f3690c03954cac275f9bf9c26d81a18fc1e5ec0/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
