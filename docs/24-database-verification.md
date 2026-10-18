# Database and demo-account verification

Verified on 18 October 2026 against the updated frontend and current hosted configuration.

## Demo access

The hosted service has `SIXTH_DEMO_LOGIN=false`. Calling the production `/v1/session/demo` endpoint with the configured private code returns HTTP 403, "Demo sign-in is disabled." The current landing page offers Google sign-in, not an Alex/Jordan demo-account form. A fresh authenticated production demo-account workflow therefore could not be exercised.

Local demo-account browser tests pass for message sending, sourced memory, meal planning, explicit sandbox-cart review, corrections, account isolation and reload persistence.

## Live Google account verification

A live Google sign-in succeeded on 18 October 2026. The first challenge expired while the account chooser was open. A fresh challenge completed sign-in and opened a personal workspace.

The authenticated check sent the synthetic message `Remember that Rowan prefers green tea.` The application returned a memory confirmation. After a page reload, the session, conversation, and saved memory remained available. The interface reported `Graph connected` and `Model-assisted · FalkorDB memory`.

Independent read-only database queries confirmed one Google identity for the tested owner. PostgreSQL contained one conversation, two messages, one profile, and one task. FalkorDB contained the Rowan assertion linked to its source. The report is stored in ignored `artifacts/google-login-live-verification.json`. The screenshot is stored in ignored `artifacts/sixth-google-login-verified.jpg`.

This check verifies a fresh hosted message and sourced memory through a personal Google account. It does not verify every account feature or a hosted cart workflow. Alex and Jordan demo login remains disabled.

## Storage paths

| Configuration | Conversations, messages and tasks | Personal memory | Workflow checkpoints |
| --- | --- | --- | --- |
| Local fixture | SQLite | SQLite fixture assertions | SQLite |
| Local graph mode | SQLite | FalkorDB | SQLite |
| Current hosted service | PostgreSQL | FalkorDB | PostgreSQL |

SQLite and PostgreSQL are alternative operational stores. The hosted service does not mirror operational records into a second SQLite database. FalkorDB stores the graph relationships and sourced assertions rather than a duplicate of every chat record.

## Fresh local SQLite proof

A synthetic memory message sent through the application's API created one conversation, two messages, one task, one fact, three task events and four LangGraph checkpoints. The application was closed before those persisted files were queried directly.

The twelve application tests also passed against SQLite. These include checkpoint resumption after restart, correction and forgetting, action replay, CSRF, account isolation and hosted-access configuration checks.

## Real FalkorDB proof

Both real-graph integration tests passed against the configured FalkorDB instance using isolated test owners and local SQLite operational stores. Assertions covered sourced memory and subject edges, event context, correction, account isolation, plan-to-memory relationships, reviewed sandbox outcomes and the applied outbox record.

## Existing hosted demo data

The PostgreSQL application suite is not fully verified. The pooled endpoint rejected the test harness's startup `search_path` option. A retry through the direct endpoint completed two tests but then stalled; it was stopped after more than six minutes. Existing hosted records below were independently confirmed with read-only queries. The separate live Google account check above verifies a fresh hosted message write.

Direct read-only queries found the following existing records for Alex. These demonstrate stored data from earlier use; they are not a new successful production demo login.

| PostgreSQL record kind | Count |
| --- | --- |
| Conversation | 2 |
| Message | 7 |
| Task | 4 |
| Plan | 2 |
| Cart | 1 |
| Outbox | 1 |

FalkorDB contains two assertions, two sources, two plans, four people, two events, one recipe, one action and one outcome in Alex's graph. Source, subject, plan, attendance and outcome edges are present. Jordan's graph is empty, and no Jordan operational records were returned by the scoped count query.

Detailed local results are in ignored `artifacts/database-verification.json`, `artifacts/hosted-database-counts.json` and `artifacts/falkordb-verification.log`. Credentials and access codes are not included in the report.
