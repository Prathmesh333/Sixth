# LobeHub

Repository: [lobehub/lobe-chat](https://github.com/lobehub/lobe-chat)  
Category: Interface and runtime reference  
Inspected commit: `6d65ee7067311af0a9c326fc076af369abd3a4fd`  
Upstream commit timestamp: 2026-10-16T14:22:53Z  
License text inspected: LobeHub Community License

## Problem and implementation

Combines agent-oriented interfaces, model adapters and orchestration in a larger application.

Architecture docs distinguish model runtime from agent runtime. The current tree contains multiple apps and packages. DESIGN.md and DESIGN.dark.md define semantic theme tokens; agent runtime handles plans, tool execution and review state.

## Published direction

The README describes operator, creation, collaboration and evolution themes. These are product directions, not a dated roadmap. The inspected license has conditions beyond Apache-2.0 despite an Apache-style README badge.

## Application to Sixth

Borrow the principle of semantic tokens and a separation between model access and task execution. Sixth's themes and components should be original.

Do not copy its visual assets or assume unrestricted derivative reuse from the badge. The monorepo and provider breadth are too large for the MVP.

## Repository structure

Selected directories in the pinned tree:

```text
apps/
packages/agent-runtime/
packages/model-runtime/
src/
docs/development/
```

[Browse the pinned tree](https://github.com/lobehub/lobe-chat/tree/6d65ee7067311af0a9c326fc076af369abd3a4fd). This is a selected map, not the complete repository.

## Evidence inspected

- [DESIGN.md](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/DESIGN.md)
- [DESIGN.dark.md](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/DESIGN.dark.md)
- [docs/development/basic/architecture.mdx](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/docs/development/basic/architecture.mdx)
- [packages/agent-runtime/src/core/runtime.ts](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/packages/agent-runtime/src/core/runtime.ts)
- [README.md](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/README.md)
- [LICENSE](https://github.com/lobehub/lobe-chat/blob/6d65ee7067311af0a9c326fc076af369abd3a4fd/LICENSE)

Review scope: repository tree, README, license text, and selected implementation/architecture sections. Large files were inspected selectively. No repository was installed, executed, benchmarked, or audited end to end. Sixth recommendations above are our design choices.
