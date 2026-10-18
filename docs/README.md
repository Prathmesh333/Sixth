# Sixth documentation

[Product overview](../README.md) · [Hosted app](https://sixth-one.vercel.app/)

Use the guides below to run Sixth, understand the implementation, or review the product design. The numbered design documents include proposals that extend beyond the current app.

## Start here

| Goal | Guide |
| --- | --- |
| Install Sixth and try a local sample account | [Local setup](getting-started.md) |
| Understand accounts, friends, and Google sign-in | [Personal React app](23-personal-react-app.md) |
| Deploy the frontend and API | [Hosted demo](21-hosted-demo.md) |
| Check database behavior and current access limits | [Database verification](24-database-verification.md) |
| Understand chat updates and model replies | [Chat responsiveness](25-chat-responsiveness.md) |
| Read the implementation history | [Implementation status](19-implementation-status.md) |
| Configure the optional WhatsApp test connector | [WhatsApp integration](22-whatsapp-integration.md) |

## Architecture and behavior

- [System architecture](03-system-architecture.md)
- [FalkorDB design and graph schema](04-falkordb-design.md)
- [Memory lifecycle](05-memory-lifecycle.md)
- [Agent runtime](06-agent-runtime.md)
- [API and event contracts](08-api-contracts.md)
- [Security, privacy, and user control](11-security-and-privacy.md)
- [Architecture decisions](17-architecture-decisions.md)

Read these documents as design references. Use the local setup guide, source code, and dated verification records to establish current behavior.

## Product design and research

The [capability map](20-instinct-capability-map.md) compares the product target with the implementation. The [research index](research/README.md) links the source reviews and integration analysis.

<details>
<summary>All design documents and research references</summary>

1. [Executive recommendation](00-executive-recommendation.md)
2. [Product requirements](01-product-requirements.md)
3. [User journeys and acceptance criteria](02-user-journeys.md)
4. [System architecture](03-system-architecture.md)
5. [FalkorDB integration and graph schema](04-falkordb-design.md)
6. [Memory lifecycle](05-memory-lifecycle.md)
7. [Agent orchestration and execution](06-agent-runtime.md)
8. [Integrations and tool contracts](07-integrations.md)
9. [API and event contracts](08-api-contracts.md)
10. [Codebase structure](09-repository-structure.md)
11. [Interface, brand, and themes](10-design-and-themes.md)
12. [Security, privacy, and user control](11-security-and-privacy.md)
13. [Evaluation and test plan](12-evaluation.md)
14. [Build plan and backlog](13-build-plan.md)
15. [Deployment and operations](14-deployment-and-operations.md)
16. [Demo and submission](15-demo-and-submission.md)
17. [Product strategy and costs](16-product-strategy.md)
18. [Architecture decisions](17-architecture-decisions.md)
19. [Risks and open decisions](18-risks-and-decisions.md)
20. [Research synthesis](research/README.md), [comparison](research/comparison.md), and [15 repository reviews](research/repositories/)
21. [Source register](research/sources.md) and [machine-readable evidence manifest](research/evidence-manifest.json)


</details>

## Supporting files

- [OpenAPI contract](../specs/openapi.json) and [structured data schemas](../specs/contracts.json)
- [Illustrative graph seed](../examples/graph/seed.cypher), [queries](../examples/graph/queries.cypher), and [client example](../examples/graph/query_example.py)
- [Proposed operational SQL schema](../examples/infra/operational-schema.sql)
- [Local FalkorDB infrastructure example](../examples/infra/compose.yaml) and [environment template](../examples/infra/.env.example)
- [Three visual themes](../design/themes.css) and [semantic tokens](../design/tokens.json)
- [Synthetic demo fixture](../examples/fixtures/birthday-dinner.json)
- [Documentation validation report](validation-report.md)


## Documentation layout

```text
README.md                  Product introduction
docs/
  README.md                Documentation index
  getting-started.md       Installation and local workflow
  00-*.md ... 18-*.md      Product design and engineering proposals
  19-*.md ... 25-*.md      Implementation, hosting, and verification records
  research/                Sources and repository reviews
  assets/                  Images used in GitHub documentation
specs/                     Structured API and data contracts
examples/                  Sample fixtures, graph queries, and infrastructure
```

Existing numbered filenames remain stable so links from research and engineering documents continue to resolve.
