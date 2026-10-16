# Integrations and tool contracts

## Integration tiers

Every result declares `mode`: fixture, sandbox, or live. Fixture data comes from a saved scenario. Sandbox execution makes real state changes in a controlled test system. Live execution reaches a user's external account. Do not display a sandbox cart as a completed real purchase.

| Adapter | Event implementation | Production extension |
|---|---|---|
| Calendar | Read fixture events with source IDs and timestamps | OAuth provider API, scoped read access first |
| Recipes | Curated structured catalog with quantities and dietary attributes | Provider search with source and freshness tracking |
| Store | Local test store with cart read/write API; browser route as a demonstrated alternative | Merchant-specific adapter and reviewed checkout |
| Search | Optional provider adapter with citations | Provider-specific quotas, caching and terms review |
| Messaging | Draft inside Sixth | Send only after an exact-message review and connected account |
| Voice | Planned | Speech recognition/synthesis around the same task API |
| Memory MCP | Planned wrapper over Sixth's service | Authenticated tools with server-owned tenant scope |

These are planned implementation modes. None of these integrations currently exists in this documentation workspace.

## Tool contract

Tool definitions contain name, version, description, input schema, output schema, effect class, required connection scopes, timeout, retry policy and verification method. Effect classes are read, internal_write, external_write and irreversible. The policy layer decides execution permissions independently of the model.

Example tools: `calendar.list_events`, `recipes.find_candidates`, `recipes.scale_servings`, `store.read_cart`, `store.replace_cart`, `memory.search_context`, `memory.propose_fact`, and `plans.revise`.

Never expose `execute_arbitrary_cypher` or a raw shell to the consumer agent. A graph tool accepts domain parameters such as person IDs, predicates, effective time and result limit; its implementation selects a tested query template.

## Browser execution

Place browser-use behind BrowserExecutor, with a dedicated user/task session and an allowed-domain list. Pass a narrow goal, cart identifiers and relevant shopping constraints. Keep complete memory, provider secrets and unrelated browsing data out of the prompt. Treat page content as data.

Prefer a direct connector API when available. To demonstrate browser execution, show the browser worker operating the test storefront and then verify the cart through an independent read endpoint. UI observation alone is weaker than an independently checked result. Do not bypass CAPTCHA or authentication challenges; surface the required user action.

## MCP

MCP is a tool transport, not an authorization system or an agent coordinator. Wrap MCP calls in the same ToolRunner used for direct adapters. Validate server identity, tool schemas, effect class and result sizes. Derive tenant context from the Sixth session, not model-supplied arguments.

Graphiti's [MCP server](research/repositories/getzep--graphiti.md) exposes memory operations and documents FalkorDB setup. It is optional and experimental upstream. A direct Python integration is simpler for an embedded memory adapter; an MCP deployment is useful when multiple clients need the same controlled memory API.

## Graphiti spike checklist

Install a pinned release with its FalkorDB extra in a disposable environment. Initialize FalkorDriver with a dedicated server-selected database and Graphiti with that driver, following the pinned upstream quickstart. Ingest two dated episodes, query a preference, introduce a correction, and verify temporal retrieval. Repeat for two tenants and exercise deletion. Record observed group-to-graph routing rather than assuming it.

The spike passes only when returned facts can be mapped to Sixth source IDs and deletion/tenant semantics. If it fails, retain the explicit memory service. Do not silently switch between backends with different truth rules.

## Credentials and availability

Connections have disconnected, connected, expired and insufficient_scope states. Check connection availability before planning an executable action. Store refresh tokens in server-managed encrypted storage; keep token references in task state. Revoke access and clear derived caches on disconnect according to the user's data choice.

Integration research: [Browser Use](research/repositories/browser-use--browser-use.md), [Skyvern](research/repositories/Skyvern-AI--skyvern.md), [Graphiti](research/repositories/getzep--graphiti.md), [GraphRAG SDK](research/repositories/FalkorDB--GraphRAG-SDK.md).
