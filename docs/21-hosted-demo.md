# Hosted synthetic demo

## Verified deployment — October 17, 2026

- Frontend: https://sixth-one.vercel.app
- Backend readiness: https://sixth-api.onrender.com/health/ready
- Vercel Hobby and Render Free are in use. Render's health-check path is `/health/ready`.
- Operational tables and native LangGraph checkpoints are initialized in Neon; client TLS was verified.
- The deployed backend connects to the actual FalkorDB Cloud instance. Its data remains synthetic.
- Browser login through the Vercel proxy and persisted memory rendering were verified with installed Chrome.
- Live Groq intent parsing, sourced graph memory, a dinner proposal, SSE progress, explicit approval, verified sandbox cart creation and cross-account task isolation all passed through the production frontend URL.
- Demo login is enabled only behind the user-set access code; the allowed browser origin is the exact frontend origin above. No credentials are included in this document.
- Operational PostgreSQL now uses a bounded connection pool. Live testing also identified model predicate and subject aliases; these are normalized before graph retrieval and covered by a regression test.
- All four jobs passed for backend commit `93ac69c` in [CI](https://github.com/Prathmesh333/Sixth/actions/runs/39036793623), including twelve application tests against PostgreSQL.

The frontend was deployed directly through the Vercel CLI. GitHub auto-deployment is not connected because the Vercel account still needs its GitHub Login Connection. Future frontend changes can be published with `vercel deploy --prod`. Render updates can be published with its authenticated CLI. The deployed services are a private synthetic demo, not production user authentication or a WhatsApp integration.

The hosted path uses Vercel Hobby for the frontend, Render Free for the Python API, Neon Free for operational PostgreSQL and LangGraph checkpoints, FalkorDB Cloud Free for graph context, and a Groq API key for model classification. Account creation alone does not establish a working deployment.

## Deployment sequence

1. Provision a Neon project. Supply its PostgreSQL connection string as `SIXTH_DATABASE_URL`, retaining `sslmode=require`. Prefer the direct endpoint for initial setup; test pooled connectivity separately. Never put this URL into frontend environment variables.
2. Create the FalkorDB free instance and wait for a ready/healthy status. Configure its actual host, port, username, password and TLS support. The published Free plan excludes TLS and automated backups: keep the graph limited to synthetic data and verify the actual endpoint before connecting.
3. Create a Sixth-only Groq API key. Set `SIXTH_MODEL_BASE_URL=https://api.groq.com/openai/v1`, a currently supported model, and `SIXTH_MODEL_API_KEY`. The adapter currently classifies intent; live JSON/schema compatibility must be tested.
4. Import `render.yaml` as a Render Blueprint or copy its settings to a free Python Web Service. Run a single API worker. Fill the secret values in Render, including a strong `SIXTH_DEMO_ACCESS_CODE`. Set `SIXTH_ALLOWED_ORIGINS` to a JSON array containing the exact Vercel origin. API startup creates missing version-1 operational tables and runs the official PostgreSQL checkpointer migrations.
5. Note Render's assigned service URL. Update both backend destinations in root `vercel.json` to that URL; the committed hostname is a proposed service name, not proof it has been allocated.
6. Import the repository into Vercel with repository root as Root Directory. Root configuration builds the frontend to `apps/web/dist` and proxies `/v1` and `/health` to Render. Do not deploy from `apps/web` unless equivalent proxy configuration is added there.
7. Verify the browser's Origin is accepted, `Set-Cookie` survives the proxy, secure session cookies work, and SSE task events are delivered. Never solve a proxy issue by disabling CSRF or allowing arbitrary credentialed origins.

The demo access code protects entry to the two shared sample accounts. It is not individual production authentication. Anyone holding the code can inspect or change the sample accounts; use no private messages or real linked accounts. The code is entered in the welcome form and held only in component/hook memory, not browser persistent storage.

## Durability and operational limits

When `SIXTH_DATABASE_URL` is set, records, conversations, sessions, event offsets, request replay records and the sandbox action ledger use PostgreSQL. LangGraph uses its PostgreSQL checkpointer. SQLite remains the local default. This is a fresh hosted database setup, not an automatic upload of local history.

Operational transactions use a shared advisory lock to serialize short mutations. Runtime changes and model calls use the existing single-process runtime lock; deploy one worker and one service instance. This is not distributed task leasing. On startup the API discovers stored owners, recovers queued/running tasks and retries outcome projections. An already persisted approval is resumed as an approval rather than reparsed as a new request.

Render Free can sleep and restart, so startup latency and interrupted requests are expected. PostgreSQL preserves durable state; it does not prevent service sleep. Review approvals expire and must still match current plan revisions. Free graph availability and retention require separate verification. Keep exportable synthetic fixtures and do not depend on free graph persistence as a backup.

## Verification gates

- SQLite application tests and hosted-code authentication tests.
- The same application suite against PostgreSQL in CI, including restart/checkpoint resumption and cross-account privacy.
- Frontend build and isolated browser journey after the login form change.
- Live Neon connection, table setup and restart persistence.
- Live FalkorDB sourced write/read/correction and account isolation.
- A synthetic Groq intent request, validating returned JSON.
- End-to-end Vercel proxy login, model-backed task, action review and verified sandbox outcome.

The deployment record above identifies the gates exercised against the configured accounts. Provider credentials remain outside Git and logs. WhatsApp and public-profile sharing are separate unimplemented integrations.
