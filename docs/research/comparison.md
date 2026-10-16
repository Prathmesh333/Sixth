# Repository comparison

These 15 repositories cover complementary layers. Most are infrastructure or reference projects rather than direct consumer competitors. Assessment is qualitative; no performance benchmark was run.

| Project | Layer | Inspected license | Sixth decision |
|---|---|---|---|
| [Khoj](repositories/khoj-ai--khoj.md) | Personal assistant | AGPL-3.0 | Design reference |
| [Leon](repositories/leon-ai--leon.md) | Personal assistant | MIT | Design reference |
| [Open Interpreter](repositories/OpenInterpreter--open-interpreter.md) | Execution harness | Apache-2.0 | Design reference |
| [Agent S](repositories/simular-ai--Agent-S.md) | Computer use | Apache-2.0 | Design reference |
| [Browser Use](repositories/browser-use--browser-use.md) | Browser execution | MIT | Adopt behind adapter |
| [Skyvern](repositories/Skyvern-AI--skyvern.md) | Browser workflows | AGPL-3.0 | Design reference |
| [LangGraph](repositories/langchain-ai--langgraph.md) | Orchestration | MIT | Adopt workflow runtime |
| [Graphiti](repositories/getzep--graphiti.md) | Temporal graph memory | Apache-2.0 | Optional memory spike |
| [Cognee](repositories/topoteretes--cognee.md) | Knowledge ingestion | Apache-2.0 | Design reference |
| [Mem0](repositories/mem0ai--mem0.md) | Personalized memory | Apache-2.0 | Design reference |
| [Letta Code](repositories/letta-ai--letta-code.md) | Stateful agents | Apache-2.0 | Design reference |
| [GraphRAG SDK](repositories/FalkorDB--GraphRAG-SDK.md) | FalkorDB document retrieval | Apache-2.0 | Later document adapter |
| [FalkorDB](repositories/FalkorDB--FalkorDB.md) | Graph database | SSPLv1 | Required graph database |
| [assistant-ui](repositories/assistant-ui--assistant-ui.md) | Chat interface | MIT | Evaluate UI primitives |
| [LobeHub](repositories/lobehub--lobe-chat.md) | Interface and runtime reference | LobeHub Community License | Design reference |

## Integration choices

Choose one workflow runtime, one browser executor, and one authoritative memory route. Start with LangGraph, browser-use and explicit Sixth graph operations. assistant-ui is a frontend candidate. Test Graphiti only if the default memory extraction needs temporal capabilities worth its added complexity.

Khoj and Leon show the breadth of a personal assistant. They are references for the product shape, not ready-made FalkorDB integrations. Agent S and Open Interpreter inform future execution surfaces. Skyvern illustrates deeper workflow recovery. Mem0, Cognee, and Letta inform memory lifecycle and user control.

## Reuse boundaries

License names are observations from pinned license files, not legal advice. Retain notices for incorporated code. Review dependency and service terms before distribution. In particular, do not infer permissive reuse from README badges, conflate an SDK license with the database license, or treat hosted features as self-hosted capabilities.
