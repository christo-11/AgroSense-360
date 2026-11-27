# AgroSense-360

AgroSense-360 is a full-stack agriculture intelligence workspace scaffold. The dashboard, interactive illustrative farm scene, account flow, farm records, PostgreSQL/PostGIS schema, and model-training entry points are implemented. External measurements and model outputs are deliberately **not** simulated: providers and validated model artifacts must be connected and deployed before those results are available.

The project is **not a launched or production-ready service**. Local development retains the authenticated farm workspace. `VITE_PUBLIC_DEMO` and `PUBLIC_DEMO_MODE` can configure a read-only technical preview, but those flags do not authorize a public demonstration, data distribution, or deployment; those activities remain NOT AUTHORIZED.

## Problem statement

Agricultural decisions depend on trustworthy, locally relevant information, but farm, crop, weather, soil, and market data are often fragmented. AgroSense-360 is being developed as a Kerala-focused platform to bring these capabilities together. Integrations and recommendations are shown as available only when supported by real, verified data; unfinished AI features are not represented as working predictions.

## Geographic scope

The catalogue is structured for all 14 Kerala districts. Idukki and cardamom are the initial pilot focus. District and crop catalogue entries do not imply that a crop is suitable for a district: suitability and agronomic profile data remain pending until supported by reviewed sources.

## Technology stack and architecture

- **Frontend:** React 18, TypeScript, Vite, Recharts, and Three.js / React Three Fiber.
- **Backend:** Python 3.11+, FastAPI, Pydantic Settings, and SQLAlchemy.
- **Data:** PostgreSQL with PostGIS, GeoAlchemy2, and Alembic migrations.
- **Authentication:** JWT access tokens with owner-scoped farm and plot APIs.

The browser application calls the FastAPI REST API. The API validates requests, enforces authentication and ownership for private farm data, and accesses PostgreSQL/PostGIS through SQLAlchemy. Alembic manages schema changes. Optional model-training entry points are separate and blocked until dataset approval and provenance requirements are met.

## Screenshots

No reviewed project screenshots are currently included. Add screenshots here only after checking that they contain no credentials, private farmer information, or real farm boundaries.

Project guides:

- [Proposed local technical preview](./PORTFOLIO_DEMO_GUIDE.md)
- [Local development](./LOCAL_DEVELOPMENT_GUIDE.md)
- [Dataset licensing and provenance](./DATASET_LICENSING_STRATEGY.md)
- [Future product roadmap](./FUTURE_PRODUCT_ROADMAP.md)
- [Deployment requirements](./DEPLOYMENT_GUIDE.md)
- [Research data and dependency inventory](./RESEARCH_DATA_AND_DEPENDENCY_INVENTORY.md)

## What works now

- Responsive React/TypeScript dashboard, light/dark theme, reduced-motion support, navigation, source status, and an interactive Three.js schematic with selectable illustrative plots.
- FastAPI service with account registration/sign-in, short-lived JWT access tokens, owner-scoped farm and plot CRUD, database readiness, and a farm/plot dashboard summary.
- A server-allowlisted admin overview for account, farm, catalogue, evidence, integration, and model status. Admin accounts are bootstrapped/reset through a one-time CLI and must change the temporary password before private access.
- Authenticated NASA POWER daily-history queries with bounded caching, explicit gridded-estimate labels, and source attribution. Open-Meteo current conditions, hourly forecasts, and seven-day summaries are available only for qualifying non-commercial use and retain CC BY 4.0 attribution.
- A protected AGMARKNET/data.gov.in daily market-price adapter with crop and Kerala district filters, bounded caching, source dates, and no fabricated values. It remains disabled until an API key is configured and the resource-specific reuse terms are confirmed.
- Private local document upload (PDF/Markdown/text), text extraction, chunked lexical retrieval and cited excerpts; Ollama is optional and never downloaded automatically.
- A user-supplied CSV regression/classification workflow for numeric yield targets or categorical suitability/recommendation labels, with group/time holdouts, measured evaluation metrics, per-account model persistence and prediction history. No model or accuracy result is included until the researcher supplies eligible labeled data.
- PostgreSQL/PostGIS model and initial Alembic migration.
- Approval-gated training entry points for soil and crop-image tasks. ERA5-Land archives are recorded as historically acquired, but that does not authorize their use; no dataset is cleared for model training and no model has been trained or validated.
- Offline app-shell caching. API responses and farm data are not stored by the service worker.
- Dockerfiles and Compose deployment for the frontend, API, and PostGIS.

## Explicitly not connected

Sentinel Hub image retrieval/processing, SoilGrids requests, NASA GPM/ERA5-Land ingestion, live mandi-price retrieval without the required data.gov.in key and reuse confirmation, validated crop-suitability recommendations, disease-risk/Hold-or-Sell models, TreeSHAP explanations, and voice/report generation remain unavailable. Local document retrieval returns cited source excerpts; optional Ollama synthesis is not required. The research regression model can only be trained from a user-supplied labeled CSV and its measured holdout results are not independent validation or agronomic advice.

The digital twin is a **schematic scene**, not a farm survey, satellite image, or real terrain. Its plot names are illustrative identifiers only.

## Real-data discovery

See the [agricultural dataset inventory](./DATASET_INVENTORY.md) and [research data/licence inventory](./RESEARCH_DATA_AND_DEPENDENCY_INVENTORY.md) for source, access, licensing, and quality records. Setup does not download datasets. Existing ERA5-Land archives are excluded and are not read by the research modules.

## Run locally

Requirements: Docker Desktop with its engine running for the documented PostgreSQL/PostGIS Compose setup. For frontend hot reload and tests, install Node.js 22+; Python 3.11+ is needed for backend tests and local secret generation. The core app needs no ML model. Install the optional lightweight research set from `backend/requirements-research.txt` to train models; it excludes PyTorch and XGBoost.

```powershell
if (-not (Test-Path .env)) {
  $dbPassword = [guid]::NewGuid().ToString("N")
  $jwtSecret = (& python -c "import secrets; print(secrets.token_urlsafe(48))").Trim()
  @"
POSTGRES_PASSWORD=$dbPassword
JWT_SECRET=$jwtSecret
FRONTEND_ORIGINS=http://localhost:8080,http://localhost:5173
PUBLIC_DEMO_MODE=false
VITE_PUBLIC_DEMO=false
VITE_API_URL=http://localhost:8000
"@ | Set-Content -Path .env -Encoding ascii
}
# Set this only if your use qualifies as non-commercial under Open-Meteo's terms.
$env:OPEN_METEO_NONCOMMERCIAL_ENABLED = "true"
docker compose up --build -d
Remove-Item Env:\OPEN_METEO_NONCOMMERCIAL_ENABLED
docker compose ps
$apiReady = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
  try {
    $health = Invoke-RestMethod -Uri http://localhost:8000/health -TimeoutSec 2
    $apiReady = $true
    break
  } catch {
    Start-Sleep -Seconds 2
  }
}
if (-not $apiReady) {
  docker compose logs api
  throw "The API did not become ready; inspect the logs above."
}
$health
```

Open the frontend at `http://localhost:8080` and API docs at `http://localhost:8000/docs`. The API container runs Alembic migrations on startup. The generated `.env` is local-only; never commit it. If `.env` already exists, preserve it and replace any example secrets with private local values rather than overwriting it. Stop the stack with `docker compose down`; the database volume is retained.

For frontend hot reload, first start only the database and API in the same PowerShell session after creating `.env` as above:

```powershell
docker compose up --build -d db api
```

In another PowerShell terminal:

```powershell
npm.cmd ci
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_PUBLIC_DEMO = "false"
npm.cmd run dev
```

The development frontend is at `http://localhost:5173`. PostgreSQL/PostGIS and migrations are managed by Compose; the API exposes `/health/database` and `/api/v1/dashboard/summary`. Migrations create or add schema objects; do not run a downgrade against a database containing data without a verified backup.

### Research tools

Weather is shown on each saved plot; farmers do not enter coordinates or weather parameters. Select the plot location through the browser's location permission. Current conditions, hourly forecasts, and daily seven-day summaries use Open-Meteo model estimates only when `OPEN_METEO_NONCOMMERCIAL_ENABLED=true` is enabled for qualifying non-commercial use; they are not direct station observations and include CC BY 4.0 attribution. Current and forecast data are cached in process (10 minutes). Optional date/time lookups use the official NASA POWER daily point API for historical estimates through two days ago, or the hourly Open-Meteo forecast for the next seven days. NASA values are gridded estimates, not station observations. The separate monthly climate research endpoint remains available through the API, but is no longer a farmer-facing navigation tab.

Open-Meteo access is disabled by default. Enable `OPEN_METEO_NONCOMMERCIAL_ENABLED=true` only when the intended use qualifies under the [free API terms](https://open-meteo.com/en/terms); the free service is non-commercial and API data require CC BY 4.0 attribution. The setting is optional in local startup; do not enable it for commercial use. No API key or automatic model download is involved.

Current and forecast condition descriptions are derived from Open-Meteo's WMO weather codes. Daily mean humidity is calculated from that day's hourly forecast estimates; all displayed weather remains model output, not a station observation.

Market prices use the Government of India AGMARKNET daily mandi resource through the [data.gov.in API](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi). Prices are daily reported records, not real-time quotes, and missing values are never estimated. Configure `AGMARKNET_API_KEY` on the API server and set `AGMARKNET_REUSE_CONFIRMED=true` only after verifying the resource-specific licence, attribution, intended-use terms, and reported price unit from the official resource page. The current project has no API key and the resource page was inaccessible during verification, so live prices are intentionally unavailable by default. The adapter displays the source's standard INR-per-quintal fields only after this explicit operator gate.

Install the research dependencies and start the backend from PowerShell:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pip install -r requirements-research.txt
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, start the existing frontend:

```powershell
$env:VITE_API_URL = "http://localhost:8000"
npm.cmd run dev -- --host localhost
```

The Research assistant displays live catalogue evidence for Idukki black pepper and explicitly withholds suitability results while sources/measurements are unverified. In Research assistant, uploads are stored under `.agrosense/research_documents` on the backend host (up to 10 MiB/file and 100 MiB/account); the owner can delete them. PDF text is extracted locally. Scanned-PDF OCR is optional: install `python -m pip install -r requirements-research-ocr.txt` from `backend` and install the separate Tesseract executable on `PATH`, then opt in per upload. OCR is limited to 50 scanned pages, 4 megapixels per rendered page and 30 seconds per page. Search works without OCR or Ollama and returns ranked excerpts with filename/page citations. Optional Ollama must already be running locally with a model installed; set `OLLAMA_BASE_URL=http://127.0.0.1:11434` and `OLLAMA_MODEL` to that local model name. The Qwen2.5 0.5B model is a small Apache-2.0 candidate (about 398 MB per the Ollama library), but is not downloaded automatically or RAM-benchmarked. If Ollama is unavailable, the assistant falls back to excerpt retrieval.

The research ML form accepts the user's own labeled CSV (max 20 MiB, 50,000 rows, 30 features). Choose numeric regression (e.g. yield) or classification (e.g. reviewed suitability classes), provide the exact source/licence, and use a group column (e.g. farm) or time column for the leakage-aware holdout. Training requires explicit rights confirmation. Model artifacts and prediction history remain under `.agrosense/research_models`; the CSV itself is not retained. Metrics are computed from the actual holdout and do not establish suitability, causation, or production performance. No synthetic training data are bundled.

Farm and plot routes require a bearer token. Register at `/api/v1/auth/register`, obtain a token at `/api/v1/auth/token`, then use the protected `/api/v1/farms` and nested `/api/v1/farms/{farm_id}/plots` endpoints. Plot records store the crop catalogue ID, area and unit, and location coordinates. Polygon boundaries remain optional for existing API clients; where supplied, they are GeoJSON in WGS84 (longitude/latitude), validated for ring closure, coordinate ranges and PostGIS geometry topology.

### Kerala agricultural catalogue

The agricultural master migration adds districts, crop categories, crops, crop profiles, crop varieties, source references, and district-crop suitability records. It seeds the 14 Kerala districts, the four requested crop categories, and the requested crop names. Initial crop profiles contain no agronomic measurements and are marked `pending`; no district-crop suitability associations are preloaded. A missing association means “not yet assessed,” not unsuitable.

The read APIs are `GET /api/v1/districts`, `GET /api/v1/crop-categories`, `GET /api/v1/crops`, `GET /api/v1/crops/{crop_id}`, `GET /api/v1/crops/{crop_id}/profile`, `GET /api/v1/crops/{crop_id}/varieties`, and `GET /api/v1/districts/{district_id}/crops`. List endpoints return `{items, total, limit, offset}` and cap `limit` at 100.

`GET /api/v1/agricultural-research/idukki-black-pepper` reports the current verified profile/association and missing-evidence blockers. It does not generate a suitability claim or yield estimate. Kerala Ecostat EARAS reports, SoilGrids, IMD gridded rainfall and their rights/access limits are tracked in the [research data/licence inventory](./RESEARCH_DATA_AND_DEPENDENCY_INVENTORY.md).

Catalog administration uses the comma-separated `AGRICULTURAL_ADMIN_EMAILS` environment variable. Only authenticated users whose email is on that allowlist can create/update crops, profiles, varieties, source references, or district-crop associations. Leave the setting empty to disable catalog administration. Marking profile, variety, or district suitability data verified requires at least one source reference. The API records references and does not fetch arbitrary source URLs.

To securely create the initial admin account, add the intended owner's email to `AGRICULTURAL_ADMIN_EMAILS` in the local `.env`, then recreate the API with `docker compose up -d api`. Generate a one-time password from a local PowerShell window; it is printed only by this command and is not stored in `.env` or source:

```powershell
$env:ADMIN_BOOTSTRAP_EMAIL = Read-Host "Admin email (must match AGRICULTURAL_ADMIN_EMAILS)"
docker compose exec -e ADMIN_BOOTSTRAP_EMAIL api python -m app.bootstrap_admin
Remove-Item Env:\ADMIN_BOOTSTRAP_EMAIL
```

Sign in immediately with the printed username and temporary password; the API blocks private/admin routes until a new password is chosen. For an existing allowlisted account, use the same command with `--reset` to issue a fresh temporary password and require another change. Public registration is blocked for allowlisted admin addresses.

```powershell
$env:ADMIN_BOOTSTRAP_EMAIL = Read-Host "Admin email (must match AGRICULTURAL_ADMIN_EMAILS)"
docker compose exec -e ADMIN_BOOTSTRAP_EMAIL api python -m app.bootstrap_admin --reset
Remove-Item Env:\ADMIN_BOOTSTRAP_EMAIL
```

The catalogue UI reads only these APIs. Pending profile fields are left blank and pending district associations are explicitly not recommendations. Source citations and suitability need human verification before publishing any agronomic guidance.

The new plot/admin migration adds optional plot metadata, allows location-only plot records, and adds a first-login password-change flag; existing plot boundaries are preserved. The agricultural catalogue migration has a downgrade for schema rollback, but it drops catalog tables and their contents. Do not downgrade after catalog data has been entered; use a forward-fix migration instead.

Run backend tests without PostgreSQL using an isolated in-memory SQLite test database:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest
Pop-Location
```

### Hosted PostgreSQL/PostGIS verification

The local workspace does not currently have PostgreSQL or a running Docker daemon. A free Supabase project is one hosted option: its current Free plan includes a 500 MB database and pauses projects after one week of inactivity. See [Supabase pricing](https://supabase.com/pricing). Enable PostGIS in the project's **Database → Extensions** page and keep it in the `extensions` schema, as described in the [Supabase PostGIS guide](https://supabase.com/docs/guides/database/extensions/postgis).

For an IPv4-only machine, use **Connect → Session pooler** and copy the host and username exactly from the dashboard. Supabase documents the shared session pooler as IPv4 reachable; direct Free-plan connections are IPv6. See [Supabase connection options](https://supabase.com/docs/guides/database/connecting-to-postgres). Store the connection string only in the root `.env` file; do not paste it into chat or commit it. The URL form for this app is:

```text
postgresql+psycopg://<POOLER_USER>:<URL_ENCODED_PASSWORD>@<POOLER_HOST>:5432/postgres?sslmode=require&options=-csearch_path%3Dextensions%2Cpublic
```

Use the pooler values from **Connect**, URL-encode reserved characters in the password, and keep `options` so PostGIS types/functions installed in `extensions` resolve for the app and migrations. Generate a separate `JWT_SECRET` of at least 32 random characters in `.env`.

Before migrating, use Supabase's SQL editor to verify the extension and ensure the new project has no conflicting AgroSense tables:

```sql
SELECT e.extname, e.extversion, n.nspname AS extension_schema
FROM pg_extension AS e
JOIN pg_namespace AS n ON n.oid = e.extnamespace
WHERE e.extname = 'postgis';

SELECT to_regclass('public.alembic_version') AS migration_table,
       to_regclass('public.users') AS users_table,
       to_regclass('public.farms') AS farms_table,
       to_regclass('public.plots') AS plots_table;

SELECT extensions.ST_SRID(
  extensions.ST_SetSRID(extensions.ST_MakePoint(0, 0), 4326)
);
```

Use a fresh project or stop if those table names already belong to existing data. From the backend directory, inspect the current migration revision and apply the additive migrations:

```powershell
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Then run the same API suite against that migrated database. The test fixture checks the PostGIS extension, spatial function search path, and expected migration revision; it does not create or drop the database schema. It cleans up only its uniquely named test accounts:

```powershell
$env:AGROSENSE_TEST_DATABASE_URL = (& ..\.venv\Scripts\python.exe -c "from app.config import Settings; print(Settings().database_url_value)").Trim()
..\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:AGROSENSE_TEST_DATABASE_URL
```

The command captures the configured URL into an environment variable without printing it. The SQLite test mode remains the default when `AGROSENSE_TEST_DATABASE_URL` is unset.

## Docker Compose configuration

For local use, keep `.env` secrets private and do not expose the database port. The frontend is served on port 8080 and the API on port 8000.

`VITE_PUBLIC_DEMO` and `PUBLIC_DEMO_MODE` only change technical interface and route behavior; they do not grant source-owner permission or project-owner authorization. Public demonstration, data distribution, and deployment are currently NOT AUTHORIZED. Keep both flags `false` and do not expose endpoints.

## Commercial dataset approval gate

The resource-level commercial review is recorded in `data/metadata/source_inventory.json`; the source findings and status definitions are in `DATASET_INVENTORY.md`. Current commercial candidates are `BLOCKED` or `CONDITIONAL`; **none is approved or acquired**. Portfolio-only statuses are separate. A public URL or a general website license does not constitute resource approval.

The `backend/scripts/dataset_governance.py` gate is called by both ML training entry points. It rejects every status other than `APPROVED`, requires a complete resource/license/rights review signed by an allowlisted reviewer, and requires a separate provenance manifest whose source, version, license, local input path, retrieval timestamp, and SHA-256 digest match the training input. Directory digests are computed in streaming order to limit memory use. There is no `--force` bypass.

For controlled administrative review, configure `DATASET_REVIEWER_EMAILS` and a private `DATASET_APPROVAL_HMAC_KEY` in the local `.env` or secret manager. Keep the signing key private and do not commit `.env`. The review command records a status only for an allowlisted reviewer:

```powershell
python backend\scripts\review_dataset.py --dataset-id "actual-inventory-id" --status CONDITIONAL --reviewer reviewer@example.org --reason "Terms require further verification"
```

Changing a source to `APPROVED` also requires the resource entry to contain the exact resource and download/API URLs, license and evidence links, verified commercial permission, cleared third-party rights, attribution/share-alike/redistribution terms, no unresolved concerns, and known Kerala/crop scope. The HMAC signature makes manual edits to an approved review fail validation; approval changes should be made by an authorized reviewer and committed through the repository's protected review process. An approval does not by itself establish training readiness: acquisition, data-quality review, geographic/crop relevance, and a matching provenance manifest are also required.

No training dataset or validated model is bundled. Open-Meteo remains unsuitable for commercial use on its free service, and is disabled by default; its opt-in is limited to qualifying non-commercial research. FAOSTAT access and licensing, PlantVillage and PlantDoc image rights remain conditional on resource-specific review.

## ML workflow boundaries

The Research assistant's optional CSV workflow accepts user-provided labeled data after the user confirms research-use rights and records the source and licence. It uses a group or temporal holdout and reports measured metrics for that one split. This confirmation is not a project source approval, and the metrics are not independent scientific validation, agronomic evidence, or production readiness. Do not train on the project's existing ERA5-Land archives: the governance and quality assessments reject them for training.

The separate soil and crop-image training scripts are not part of the Research assistant workflow. Do not run them unless their exact datasets have passed the repository's signed approval, provenance, quality, and relevance gates. Their current random split strategies are not leakage-safe; they must be replaced with task-appropriate spatial/group and temporal evaluation before those workflows can be considered for use. No dataset is currently approved for these project-specific training workflows, and no model is claimed to be trained or validated.
