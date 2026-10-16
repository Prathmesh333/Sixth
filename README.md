# Sixth

**Your sixth sense for everyday life.**

Sixth is a proposed consumer assistant inspired by the conversational experience at [Instinct](https://instinct.com/). It connects personal context, remembers decisions, and uses tools to carry out requests. FalkorDB supplies the relationships that change its plans and actions.

This workspace currently contains research, specifications, and implementation examples. **The application has not been built or deployed.** Examples are not evidence of working integrations. Research was conducted on October 16, 2026; repository references use pinned commits.

## Read first

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
