# AgroSense-360

AgroSense-360 is a full-stack agriculture intelligence workspace scaffold. The dashboard, interactive illustrative farm scene, account flow, farm records, PostgreSQL/PostGIS schema, and model-training entry points are implemented. External measurements and model outputs are deliberately **not** simulated: providers and validated model artifacts must be connected and deployed before those results are available.

The project is **not a launched or production-ready service**. Local development retains the authenticated farm workspace. A separate public portfolio build is read-only and requires both `VITE_PUBLIC_DEMO=true` and backend `PUBLIC_DEMO_MODE=true`; the backend blocks registration, login, and authenticated data routes in that mode.

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

- [Public portfolio demonstration](./PORTFOLIO_DEMO_GUIDE.md)
- [Local development](./LOCAL_DEVELOPMENT_GUIDE.md)
- [Dataset licensing and provenance](./DATASET_LICENSING_STRATEGY.md)
- [Future product roadmap](./FUTURE_PRODUCT_ROADMAP.md)
- [Deployment requirements](./DEPLOYMENT_GUIDE.md)

## What works now

- Responsive React/TypeScript dashboard, light/dark theme, reduced-motion support, navigation, source status, and an interactive Three.js schematic with selectable illustrative plots.
- FastAPI service with account registration/sign-in, short-lived JWT access tokens, owner-scoped farm and plot CRUD, database readiness, and a farm/plot dashboard summary.
- PostgreSQL/PostGIS model and initial Alembic migration.
- Approval-gated training entry points for soil and crop-image tasks. No dataset is approved/acquired and no model has been trained or validated; current split strategies must be replaced before evaluation.
- Offline app-shell caching. API responses and farm data are not stored by the service worker.
- Dockerfiles and Compose deployment for the frontend, API, and PostGIS.

## Explicitly not connected

Sentinel Hub image retrieval/processing, SoilGrids requests, NASA GPM/ERA5-Land forecast ingestion, AGMARKNET retrieval, inference endpoints, yield/disease-risk/Hold-or-Sell stacked models, TreeSHAP explanations, RAG, voice, and report generation need provider integrations, validated data/model assets, and operational evaluation before they can return results. The API reports these as unavailable and returns `503` for unavailable insight and copilot requests. A credential being present is not treated as a successful data integration.

The digital twin is a **schematic scene**, not a farm survey, satellite image, or real terrain. Its plot names are illustrative identifiers only.

## Real-data discovery

See the [agricultural dataset inventory](./DATASET_INVENTORY.md) for official sources, access and licensing notes, data-quality risks, and a staged download/training plan. No external datasets have been downloaded and no models have been trained.

## Run locally

Requirements: Node.js 22+ and Python 3.11+ for the API. The ML training dependencies are optional and installed separately.

```powershell
npm install
npm run dev
```

In another terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-test.txt
$env:DATABASE_URL = "postgresql+psycopg://agrosense:password@localhost:5432/agrosense"
$env:JWT_SECRET = (& python -c "import secrets; print(secrets.token_urlsafe(48))").Trim()
$env:FRONTEND_ORIGINS = "http://localhost:5173"
Push-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
Pop-Location
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

The existing workspace `.venv` is reused; do not recreate it if it already exists. The test requirements install only the API and test dependencies. Add the separate training dependencies only when needed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-ml.txt
```

The API is documented at `http://localhost:8000/docs`. PostgreSQL must have the PostGIS extension installed; the initial migration enables it, the second adds plot boundaries, and the third adds a concurrent GIST index for farm boundaries. The fourth migration adds the Kerala district and crop catalog. The API provides `/health/database` for database readiness and `/api/v1/dashboard/summary` for the authenticated user's farm and plot counts. Migrations create or add schema objects; do not run a downgrade against a database containing data without a verified backup.

Farm and plot routes require a bearer token. Register at `/api/v1/auth/register`, obtain a token at `/api/v1/auth/token`, then use the protected `/api/v1/farms` and nested `/api/v1/farms/{farm_id}/plots` endpoints. Polygon boundaries are GeoJSON in WGS84 (longitude/latitude); the API validates ring closure and coordinate ranges and PostGIS validates geometry topology.

### Kerala agricultural catalogue

The agricultural master migration adds districts, crop categories, crops, crop profiles, crop varieties, source references, and district-crop suitability records. It seeds the 14 Kerala districts, the four requested crop categories, and the requested crop names. Initial crop profiles contain no agronomic measurements and are marked `pending`; no district-crop suitability associations are preloaded. A missing association means “not yet assessed,” not unsuitable.

The read APIs are `GET /api/v1/districts`, `GET /api/v1/crop-categories`, `GET /api/v1/crops`, `GET /api/v1/crops/{crop_id}`, `GET /api/v1/crops/{crop_id}/profile`, `GET /api/v1/crops/{crop_id}/varieties`, and `GET /api/v1/districts/{district_id}/crops`. List endpoints return `{items, total, limit, offset}` and cap `limit` at 100.

Catalog administration uses the comma-separated `AGRICULTURAL_ADMIN_EMAILS` environment variable. Only authenticated users whose email is on that allowlist can create/update crops, profiles, varieties, source references, or district-crop associations. Leave the setting empty to disable catalog administration. Marking profile, variety, or district suitability data verified requires at least one source reference. The API records references and does not fetch arbitrary source URLs.

The catalogue UI reads only these APIs. Pending profile fields are left blank and pending district associations are explicitly not recommendations. Source citations and suitability need human verification before publishing any agronomic guidance.

The new migration has a downgrade for schema rollback, but it drops the agricultural catalog tables and their contents. Do not downgrade after catalog data has been entered; use a forward-fix migration in production. The migration does not alter existing users, farms, plots, or boundaries.

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

## Docker deployment

Copy `.env.example` to `.env`, replace all placeholder secrets with strong random values, and set `VITE_API_URL` to the API's browser-reachable URL. Then run `docker compose up --build`. The frontend is served on port 8080 and the API on port 8000. Do not expose the database port publicly.

For a public portfolio build, set both `VITE_PUBLIC_DEMO=true` (frontend build argument) and `PUBLIC_DEMO_MODE=true` (API runtime environment), and set `FRONTEND_ORIGINS` to the exact HTTPS origin. The local Compose stack defaults these flags to `false` so local account/farm development remains available. Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) before exposing any endpoint.

## Commercial dataset approval gate

The resource-level commercial review is recorded in `data/metadata/source_inventory.json`; the source findings and status definitions are in `DATASET_INVENTORY.md`. Current resources are `BLOCKED`, `CONDITIONAL`, or `UNVERIFIED`; **none is approved for training**. A public URL or a general website license does not constitute resource approval.

The `backend/scripts/dataset_governance.py` gate is called by both ML training entry points. It rejects every status other than `APPROVED`, requires a complete resource/license/rights review signed by an allowlisted reviewer, and requires a separate provenance manifest whose source, version, license, local input path, retrieval timestamp, and SHA-256 digest match the training input. Directory digests are computed in streaming order to limit memory use. There is no `--force` bypass.

For controlled administrative review, configure `DATASET_REVIEWER_EMAILS` and a private `DATASET_APPROVAL_HMAC_KEY` in the local `.env` or secret manager. Keep the signing key private and do not commit `.env`. The review command records a status only for an allowlisted reviewer:

```powershell
python backend\scripts\review_dataset.py --dataset-id "actual-inventory-id" --status UNVERIFIED --reviewer reviewer@example.org --reason "Review source terms"
```

Changing a source to `APPROVED` also requires the resource entry to contain the exact resource and download/API URLs, license and evidence links, verified commercial permission, cleared third-party rights, attribution/share-alike/redistribution terms, no unresolved concerns, and known Kerala/crop scope. The HMAC signature makes manual edits to an approved review fail validation; approval changes should be made by an authorized reviewer and committed through the repository's protected review process. An approval does not by itself establish training readiness: acquisition, data-quality review, geographic/crop relevance, and a matching provenance manifest are also required.

No acquisition or model training has been performed. In particular, Open-Meteo's free API and FAOSTAT are blocked for this commercial project under the currently verified terms; PlantVillage and PlantDoc remain unverified pending image-rights review.

## Train models with your data

Training is unavailable until a dataset has passed the commercial approval gate, has been acquired with a versioned provenance manifest, and has a verified quality/relevance review. The disease trainer's random image split and the soil trainer's random row split are not leakage-safe; correct task-specific splitting and validation before running either trainer.

After those prerequisites are met, soil CSVs must include the ten feature columns and five lab-measured target columns defined in `backend/scripts/train_soil_model.py`. The command also requires an approved inventory id and provenance manifest:

```powershell
python backend\scripts\train_soil_model.py --data path\to\curated-soil.csv --dataset-id "approved-resource-id" --provenance data\metadata\provenance\soil.json --output backend\models\soil_xgb.joblib
```

Disease training expects an ImageFolder layout with one verified class directory per label and the same approval/provenance arguments:

```text
dataset/
  healthy/
  verified_disease_label/
```

```powershell
python backend\scripts\train_disease_model.py --data path\to\dataset --dataset-id "approved-resource-id" --provenance data\metadata\provenance\disease.json --output backend\models\disease_resnet18.pt
```

Review the validation metrics, geographic/data leakage, class balance, calibration, and agronomic applicability before deploying any resulting artifact. Training outputs alone do not enable inference or imply production validation.
