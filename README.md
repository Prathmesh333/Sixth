# Sixth

**Your sixth sense for everyday life.**

[Open the hosted synthetic demo](https://sixth-one.vercel.app/) · Enter the private access code configured in Render. [Deployment verification and limits](docs/21-hosted-demo.md).

Sixth is a proposed consumer assistant inspired by the conversational experience at [Instinct](https://instinct.com/). It connects personal context, remembers decisions, and uses tools to carry out requests. FalkorDB supplies the relationships that change its plans and actions.

Sixth now includes a working local application: React chat, sourced memory, persistent LangGraph workflows, dinner planning and a reviewed sandbox cart. The default is explicitly labeled fixture memory with a local planner. A native FalkorDB adapter and optional model endpoint are implemented; live service verification is tracked in the [implementation status](docs/19-implementation-status.md). Research references use pinned commits.

## Run Sixth locally

Requirements: Node.js 22 and [uv](https://docs.astral.sh/uv/). The lockfile selects Python 3.12.

```powershell
uv sync --frozen
npm ci
Copy-Item .env.example .env
```

Start the API and frontend in separate terminals:

```powershell
npm run dev:api
```

```powershell
npm run dev
```

Open [Sixth](http://127.0.0.1:5173/). Choose the local Alex account. Try these messages in order:

1. `Maya is vegetarian.`
2. Start a new conversation, then `Plan Maya's birthday dinner for four.`
3. `Two more people are joining and Maya avoids dairy for this dinner.`
4. Review **Prepare test cart**, then inspect **Why this plan?**

Preferences, plans and cart results survive restarts. The calendar, recipe catalog, pantry and prices are sample data. A sandbox cart is a real local state change, never a real purchase. Demo accounts are for private localhost use, not production authentication.

## Connect the real graph and a model

To use an existing FalkorDB server, set `SIXTH_MEMORY_BACKEND=falkordb` and the `SIXTH_FALKORDB_*` fields in `.env`, then restart the API. FalkorDB mode does not silently fall back to SQLite. Fixture facts are not automatically migrated to a live graph.

With Docker available, the root Compose configuration builds the application and starts FalkorDB:

```powershell
docker compose up --build
```

Open [Sixth with the graph backend](http://127.0.0.1:8000/) and [FalkorDB Browser](http://127.0.0.1:3000/). [CI verifies the container path and real graph integration](https://github.com/Prathmesh333/Sixth/actions/runs/38935709597); Docker is unavailable on the Windows development host. The database image is pinned to the tested service digest. This remains a private local demo, not a production deployment.

To enable model-assisted intent parsing, set `SIXTH_MODEL_BASE_URL`, `SIXTH_MODEL_NAME`, and `SIXTH_MODEL_API_KEY` server-side. Without those settings, the supported local intents remain usable. No model credentials go to the browser. A live model call has not been verified yet.

## Verify

```powershell
uv run pytest tests/test_application.py -q
uv run ruff check apps/api tests scripts
npm run build
npm run test:e2e
```

The browser runner starts its own isolated servers and fixture data. It defaults to installed Google Chrome. For bundled Chromium, run `uv run playwright install chromium` and set `SIXTH_BROWSER_CHANNEL` to an empty string. Screenshots and logs go to ignored `artifacts/`.

For an existing real FalkorDB server, set `SIXTH_GRAPH_TEST=1` and run `uv run pytest tests/test_falkordb.py -q`. The dedicated GitHub Actions graph job also runs this test with a database service. Runtime API documentation is served at `/docs`; the original `specs/openapi.json` remains the broader design contract.

## Read first

Current build: [implementation status and verification](docs/19-implementation-status.md).

New research: [Instinct evidence, Sixth capability gaps, and the messaging/agent implementation plan](docs/20-instinct-capability-map.md).

Deployment: [Vercel, Render, Neon and FalkorDB hosted demo setup](docs/21-hosted-demo.md).

1. [Executive recommendation](docs/00-executive-recommendation.md)
2. [Product requirements](docs/01-product-requirements.md)
3. [User journeys and acceptance criteria](docs/02-user-journeys.md)
4. [System architecture](docs/03-system-architecture.md)
5. [FalkorDB integration and graph schema](docs/04-falkordb-design.md)
6. [Memory lifecycle](docs/05-memory-lifecycle.md)
7. [Agent orchestration and execution](docs/06-agent-runtime.md)
8. [Integrations and tool contracts](docs/07-integrations.md)
9. [API and event contracts](docs/08-api-contracts.md)
10. [Codebase structure](docs/09-repository-structure.md)
11. [Interface, brand, and themes](docs/10-design-and-themes.md)
12. [Security, privacy, and user control](docs/11-security-and-privacy.md)
13. [Evaluation and test plan](docs/12-evaluation.md)
14. [Build plan and backlog](docs/13-build-plan.md)
15. [Deployment and operations](docs/14-deployment-and-operations.md)
16. [Demo and submission](docs/15-demo-and-submission.md)
17. [Product strategy and costs](docs/16-product-strategy.md)
18. [Architecture decisions](docs/17-architecture-decisions.md)
19. [Risks and open decisions](docs/18-risks-and-decisions.md)
20. [Research synthesis](docs/research/README.md), [comparison](docs/research/comparison.md), and [15 repository reviews](docs/research/repositories/)
21. [Source register](docs/research/sources.md) and [machine-readable evidence manifest](docs/research/evidence-manifest.json)

## Supporting artifacts

- [OpenAPI contract](specs/openapi.json) and [structured data schemas](specs/contracts.json)
- [Illustrative graph seed](examples/graph/seed.cypher), [queries](examples/graph/queries.cypher), and [client example](examples/graph/query_example.py)
- [Proposed operational SQL schema](examples/infra/operational-schema.sql)
- [Local FalkorDB infrastructure example](examples/infra/compose.yaml) and [environment template](examples/infra/.env.example)
- [Three visual themes](design/themes.css) and [semantic tokens](design/tokens.json)
- [Synthetic demo fixture](examples/fixtures/birthday-dinner.json)
- [Documentation validation report](docs/validation-report.md)

## Product boundaries

The product is broad; the hackathon implementation is one complete loop across calendar, meal planning, and a test shopping cart. Travel, gifts, voice, and additional messaging channels are planned extensions. No real purchase, booking, or message is implied by a generated plan.

Target Track 01 (connected-data actions) and Track 02 (persistent memory and coordination). Do not claim consumer knowledge automatically qualifies for Company Brain. [Official event brief](https://www.wemakedevs.org/hackathons/falkordb).
