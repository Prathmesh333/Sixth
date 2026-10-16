# Research synthesis

## Findings that change Sixth's architecture

1. A personal assistant needs distinct context, execution and tool boundaries. [Leon](repositories/leon-ai--leon.md) and [Khoj](repositories/khoj-ai--khoj.md) make those responsibilities visible.
2. Durable execution and durable personal memory solve different problems. Adopt [LangGraph](repositories/langchain-ai--langgraph.md) for workflow continuation and FalkorDB for relationship-aware personal context.
3. [Graphiti](repositories/getzep--graphiti.md) already has a FalkorDB driver. Test it before building advanced temporal extraction, but preserve a simple explicit schema as the hackathon baseline.
4. [Browser Use](repositories/browser-use--browser-use.md) supplies a browser executor; it does not replace Sixth's credential boundary, action ledger or personal memory.
5. [GraphRAG SDK](repositories/FalkorDB--GraphRAG-SDK.md) owns a document-oriented graph schema. It needs an adapter or separate namespace, not blind mixing with Sixth nodes.
6. Source freshness matters: the inspected [Open Interpreter](repositories/OpenInterpreter--open-interpreter.md) is Rust-based, and active [Letta](repositories/letta-ai--letta-code.md) implementation moved. Several older integration assumptions would be wrong.
7. Theme design should use semantic tokens, as illustrated by [LobeHub](repositories/lobehub--lobe-chat.md), while Sixth uses original colors, layouts and assets.

## Read the evidence

- [Comparison and adoption decisions](comparison.md)
- [Repository-to-Sixth integration map](integration-map.md)
- [Pinned source register](sources.md)
- [Machine-readable manifest](evidence-manifest.json)
- [Per-repository implementation reviews](repositories/)

The reviews cover 15 implementation repositories plus one migration notice. They are selective source reviews, not execution or security audits. No upstream performance claim is adopted as a Sixth result.

## Recommended implementation order

Build a deterministic memory-to-action loop first. Add model-based extraction after typed fixtures work. Add browser execution after the action ledger works. Evaluate Graphiti and document ingestion only after the primary demo passes. This order gives every added dependency a concrete problem to solve.
