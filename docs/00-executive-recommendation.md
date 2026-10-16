# Executive recommendation

Status: proposed design, October 16, 2026. This is an implementation plan, not a report of completed features.

## Build decision

Build Sixth as a chat-first personal assistant with a durable personal graph. Give it three working skills for the hackathon: read a calendar, build a suitable meal plan, and prepare a shopping cart in a test storefront. These skills share memory and execution state. A separate Memory view lets the user inspect, correct, and forget facts.

A user should be able to say, "Plan Maya's birthday dinner," without repeating Maya's preferences. A later change should alter the menu and cart, with a short explanation pointing to the relevant sources.

## Recommended stack

| Concern | Recommendation | Reason |
|---|---|---|
| Interface | React + TypeScript + Vite; evaluate assistant-ui primitives | Small chat application with explicit tool cards |
| API | Python + FastAPI + Pydantic | Typed agent and connector boundaries |
| Workflow | LangGraph with a persistent SQLite checkpointer for the local demo | Resume interrupted tasks without replaying effects |
| Personal context | Official Python FalkorDB client; explicit Sixth schema | Predictable, inspectable graph queries |
| Operational state | SQLite locally; PostgreSQL after deployment needs grow | Atomic action ledger and workflow records |
| Browser work | browser-use in a separate worker | Browser interaction isolated from personal context |
| Tool access | Direct adapters first; MCP adapter for additional tools | Avoid unnecessary services during the event |
| Memory enhancement | Optional Graphiti + FalkorDB spike | Temporal extraction already has a native driver |
| Deployment | Docker-backed FalkorDB, persistent backend process, static frontend | Browser tasks require a long-lived worker |

These are Sixth recommendations informed by the [research](research/README.md). Exact package versions and container digests must be pinned after an integration smoke test. No compatibility matrix has been executed yet.

## What we borrow

Use Leon's separation of tools, context, and execution as a design reference. Adopt LangGraph for workflow durability and browser-use for bounded browser execution. Learn memory correction patterns from Graphiti, Cognee, and Mem0. Use assistant-ui as a candidate component layer. Write Sixth's graph and consumer experience ourselves.

Do not combine Letta, Mem0, Cognee, Graphiti, and GraphRAG-SDK as simultaneous memory engines. They overlap, add operational dependencies, and make source-of-truth behavior hard to explain.

## Why this can compete

The official [brief](https://www.wemakedevs.org/hackathons/falkordb) asks for connected reasoning, durable memory, and traceable decisions. Sixth's demo will show each through real queries, a changed action plan, a worker restart, and a source-backed explanation. These are fit arguments, not judging scores or a promise of winning.

## Go/no-go gates

Before polishing: prove tenant-scoped graph retrieval, confirm a changed preference changes an action, restart the worker without duplicating a cart mutation, and show source evidence. If browser automation is unstable, retain the same tool contract with the test store's deterministic API and label the execution route accurately.
