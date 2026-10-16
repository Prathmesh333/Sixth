# Repository-to-Sixth integration map

These are proposed adaptations, not claims that upstream projects implement Sixth or use FalkorDB. Consult the [repository comparison](comparison.md) for pinned evidence.

| Project | Useful responsibility | Where FalkorDB fits | Decision |
|---|---|---|---|
| Khoj | Personal retrieval and actions | Use Sixth ContextService in place of a full-product fork | Reference |
| Leon | Per-profile tools and context | Map trusted profile identity to a personal graph | Reference |
| Open Interpreter | Execution bridge | Pass bounded context, not full memory, into a future executor | Future reference |
| Agent S | GUI observation and action | Provide task constraints; persist independently verified outcomes | Future adapter |
| Browser Use | Browser execution | ToolRunner supplies graph-derived constraints and records sourced outcomes | Adopt after spike |
| Skyvern | Workflow recovery | Supply context at start; retain Sixth action ownership | Alternative |
| LangGraph | Durable task stages | Context stage queries graph; outcome stage projects through outbox | Adopt |
| Graphiti | Temporal memory | Native FalkorDriver with dedicated schema and verified tenant routing | Optional spike |
| Cognee | Staged knowledge ingestion | Custom MemoryBackend would be required; native support not established here | Reference |
| Mem0 | Scoped memory API | Use lifecycle patterns; native FalkorDB support not established here | Reference |
| Letta Code | Persistent identity/context | Avoid duplicating authoritative personal memory across platforms | Reference |
| GraphRAG SDK | Document retrieval | Separate SDK-owned graph; map evidence into Sixth context bundle | Later adapter |
| FalkorDB | Personal relationship store | Official client, parameterized queries and server-owned graph selection | Core dependency |
| assistant-ui | Chat rendering | Render evidence from backend; no direct browser-to-database access | Evaluate |
| LobeHub | Themes and runtime boundaries | Original semantic tokens and server-side graph access | Reference |

## Source and schema boundaries

Only Graphiti and GraphRAG-SDK were verified here as having direct FalkorDB integration code. FalkorDB itself is the database. Other projects inform a boundary or need a custom adapter; they are not drop-in graph integrations.

A document adapter can write a separate owned graph, but only one memory backend owns each personal assertion. Retrieve into a bounded context bundle rather than mixing incompatible schemas. Do not introduce a second graph database into the primary path.

## Adoption gate

Establish tested versions, source mapping, tenant isolation, correction and deletion behavior, output contracts, failure handling and measurable benefit before adopting an adapter. An upstream README mention is not an integration test.
