# Run Sixth locally

[Documentation index](README.md) · [Product overview](../README.md)

## Requirements

Use Node.js 22 and [uv](https://docs.astral.sh/uv/). The Python lockfile selects Python 3.12. Run the commands below from the repository root.

## Install dependencies

1. Install the Python dependencies.

   ```powershell
   uv sync --frozen
   ```

2. Install the frontend dependencies.

   ```powershell
   npm ci
   ```

3. If `.env` does not exist, copy the environment template.

   ```powershell
   Copy-Item .env.example .env
   ```

The template selects `sqlite_fixture` memory. This mode uses SQLite and a local planner without a model provider. It does not connect to FalkorDB.

## Start the app

1. Start the API in one terminal.

   ```powershell
   npm run dev:api
   ```

2. Start the frontend in a second terminal.

   ```powershell
   npm run dev
   ```

3. Open [Sixth](http://127.0.0.1:5173/).

The API listens on port 8000. The Vite frontend listens on port 5173 and proxies API requests. The welcome page shows Google sign-in. It has no sample-account form.

## Choose a local sign-in method

### Google sign-in

Set `SIXTH_GOOGLE_CLIENT_ID` in `.env`. Configure the local frontend origin in the Google OAuth Web client. Restart the API after you change the configuration. Follow the [Google setup guide](23-personal-react-app.md#google-setup) for the identity flow and account restrictions.

### Sample-account session

Use this method only for private localhost development. It does not enable production demo login.

1. Set the following values in `.env`.

   ```dotenv
   SIXTH_DEMO_LOGIN=true
   SIXTH_DEMO_ACCESS_CODE=
   SIXTH_COOKIE_SECURE=false
   ```

2. Restart the API.

3. Open the frontend at `http://127.0.0.1:5173/`.

4. In that page's browser developer console, run this request to create an Alex session.

   ```javascript
   const response = await fetch('/v1/session/demo', {
     method: 'POST',
     credentials: 'same-origin',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ account: 'alex' }),
   });
   if (!response.ok) throw new Error(`Demo sign-in failed: ${response.status}`);
   location.reload();
   ```

The server sets the session cookie. Use `jordan` instead of `alex` to open the other sample account. A shared hosted service requires a private access code if demo login is enabled. See the [hosting guide](21-hosted-demo.md).

## Try the dinner workflow

1. Send `Maya is vegetarian.`
2. Start a new conversation.
3. Send `Plan Maya's birthday dinner for four.`
4. Send `Two more people are joining and Maya avoids dairy for this dinner.`
5. Select **Why this plan?** to inspect the sources for the revised plan.
6. Select **Prepare test cart** to approve the sandbox action.

Preferences, plans, and cart results persist across restarts. Calendar events, recipes, pantry contents, and prices use sample data. A sandbox cart changes stored test data but does not place a purchase.

## Connect FalkorDB

For an existing FalkorDB server, set `SIXTH_MEMORY_BACKEND=falkordb` and the `SIXTH_FALKORDB_*` values in `.env`. Restart the API after you change the configuration.

FalkorDB stores sourced memories and graph relationships. SQLite remains the local operational store unless you set `SIXTH_DATABASE_URL`. Fixture memories do not automatically migrate to FalkorDB. FalkorDB mode does not silently fall back to SQLite fixture memory.

If Docker is available, the root Compose configuration builds Sixth and starts FalkorDB.

```powershell
docker compose up --build
```

Open [Sixth](http://127.0.0.1:8000/) and [FalkorDB Browser](http://127.0.0.1:3000/). Inspect [compose.yaml](../compose.yaml) for container settings. This configuration is a private local demo.

## Configure a model

Set `SIXTH_MODEL_BASE_URL`, `SIXTH_MODEL_NAME`, and `SIXTH_MODEL_API_KEY` on the server. Restart the API after you change these values. Without a configured model, the supported local intents use the deterministic planner. The frontend does not receive model credentials.

## Run checks

```powershell
uv run pytest tests/test_application.py -q
uv run ruff check apps/api tests scripts
npm run build
npm run test:e2e
```

The browser runner starts isolated servers and fixture data. It uses installed Google Chrome by default. To use bundled Chromium, run `uv run playwright install chromium` and set `SIXTH_BROWSER_CHANNEL` to an empty string. Screenshots and logs are written to the ignored `artifacts/` folder.

For an existing FalkorDB server, configure the connection, set `SIXTH_GRAPH_TEST=1`, then run `uv run pytest tests/test_falkordb.py -q`.

FastAPI serves the implemented API documentation at `http://127.0.0.1:8000/docs`. The [OpenAPI design contract](../specs/openapi.json) describes the broader product design.

See the [database verification report](24-database-verification.md) for the latest storage results and unresolved hosted checks.
