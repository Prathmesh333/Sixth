# Documentation validation report

Historical report from the documentation-only phase. For application checks, see [implementation status](19-implementation-status.md).

Run date: October 16, 2026. Checks apply to documentation and supporting artifacts, not an implemented Sixth application.

| Check | Result | Evidence |
|---|---|---|
| Local Markdown links | PASS | 92 local links checked; no broken targets |
| JSON parsing | PASS | 5 JSON files parsed |
| JSON Schema | PASS | Meta-schema plus 7 positive/negative payload checks |
| OpenAPI 3.1 | PASS | 13 paths and 14 operations validated with openapi-spec-validator |
| Compose YAML | PASS | YAML parsed; required image variable and loopback ports inspected. Docker startup not run. |
| SQLite DDL | PASS | 6 proposed tables created in an in-memory database; service behavior not tested |
| Python example syntax | PASS | AST parsed without importing the client or connecting to a database |
| Research evidence | PASS | 15 unique implementation repositories; 69 pinned file references match retrieved trees. Additional Letta migration notice is separate. |
| Theme token parity | PASS | 3 themes have matching JSON and CSS values |
| Theme color contrast | PASS | 60 proposed text/focus token pairs checked; all meet chosen thresholds |
| Fixture quantities | PASS | Rice deficit 100g initially and 250g after guest-count change |
| Markdown fences | PASS | All Markdown code/diagram fences balanced. Mermaid rendering not tested. |

## Limits

- No FalkorDB server or Cypher execution was tested.
- No upstream repository was installed or benchmarked.
- No model, browser automation, OAuth connector, live calendar, cart service or application API was executed.
- CSS token contrast is a mathematical check, not a rendered accessibility audit.
- Compose was parsed, not started; dependency versions and image digests remain an implementation gate.
- Repository files were selectively reviewed at pinned commits; external source URLs were fetched during research, not subjected to an exhaustive link crawler.
- OpenAPI and JSON Schema validation establish contract structure, not server correctness.

## Artifact inventory

53 files counted outside ignored research cache at validation time, including this report. 40 are Markdown documents.
