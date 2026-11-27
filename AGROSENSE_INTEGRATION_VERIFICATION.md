# AgroSense-360 — Stage 15 Integration Verification

**Verification date:** 2026-11-20  
**Result:** The local read-only catalogue workflow was verified end to end using the application's existing backend database configuration. No application code, database schema, data, or migration was changed.

## Safety and scope

- `.env` and `.cdsapirc` were not opened, printed, or inspected. Connection strings and credentials were not printed.
- Backend database probes were read-only `SELECT` statements. API requests used only health and public `GET` endpoints, plus a CORS preflight `OPTIONS`.
- No account, farm, or other database record was created or changed. No migration, seed operation, external acquisition request, dataset download, or model training was run.
- The database provider's identity was not independently established by inspecting its host or connection URL. The verified facts below are the PostgreSQL/PostGIS capabilities reachable through the application's existing configuration.
- Pre-existing worktree changes were preserved. This stage added only the two requested verification documents.

## Verification summary

| Area | Result | Evidence |
|---|---|---|
| Backend startup | **PASS** | Existing `.venv` Uvicorn process remained running; `/health`, `/health/database`, and `/api/v1/status` returned HTTP 200. No warning/error output was emitted at the selected warning log level. |
| Database connectivity | **PASS** | The application engine connected to PostgreSQL; `/health/database` returned 200 and `/api/v1/status` reported `database=connected`. |
| PostgreSQL/PostGIS | **PASS** | Read-only queries returned PostgreSQL `17.12`, PostGIS `3.3.7` in schema `extensions`, and SRID `4326` from `ST_SRID(ST_SetSRID(ST_MakePoint(0,0),4326))`. |
| Migration status | **PASS** | Read-only query to `alembic_version` returned `5d3cbf283629`. |
| Public catalogue APIs | **PASS** | Districts: 200 / 14 total; categories: 200 / 4; crops: 200 / 31. Crop detail/profile/varieties and district association endpoints returned 200 with valid expected shapes. |
| Frontend dashboard | **PASS** | Vite dev server and React app loaded at `http://localhost:5173`; dashboard displayed “Workspace connected” after refresh. No user login or writes were performed. |
| Frontend catalogue integration | **PASS** | UI loaded 14 district options and 31 crop cards from the live API; selecting Alappuzha and Arecanut displayed the pending profile, no-source state, no varieties, and empty association state. |
| Browser errors | **PASS at configured origin; CORS issue reproduced at alias** | At `http://localhost:5173`, the tested dashboard/catalogue flow had no browser console errors or failed API requests. At `http://127.0.0.1:5173`, API calls were blocked by CORS because that origin was not allowed. |
| Full application readiness | **PARTIAL** | The read-only dashboard/catalogue path is verified. Authenticated farm CRUD and unavailable weather, soil, market, image inference, and copilot features were not exercised as working workflows. |

## Read-only database evidence

Executed through `app.database.engine`, without printing the engine URL:

- `SELECT current_setting('server_version')` → `17.12`
- `SELECT extversion, extnamespace::regnamespace::text FROM pg_extension WHERE extname = 'postgis'` → `3.3.7`, `extensions`
- `SELECT version_num FROM alembic_version` → `5d3cbf283629`
- `SELECT count(*) FROM districts` → `14`
- `SELECT count(*) FROM crops` → `31`
- `SELECT count(*) FROM crop_categories` → `4`
- `SELECT ST_SRID(ST_SetSRID(ST_MakePoint(0, 0), 4326))` → `4326`

These queries confirm that PostgreSQL, the PostGIS extension, its spatial function/search path, migration table, and seeded catalogue are available through the running application's current configuration. They do not identify the hosting provider or establish production safety.

## API-to-UI workflow verified

The observed UI/API origin was `http://localhost:5173` → `http://localhost:8000` (API host only; no database URL was exposed).

1. `GET /health` → HTTP 200.
2. `GET /health/database` → HTTP 200.
3. `GET /api/v1/status` → HTTP 200; `api=online`, `database=connected`, `public_demo_mode=false`.
4. `GET /api/v1/districts?limit=100` → HTTP 200; 14 items.
5. `GET /api/v1/crop-categories?limit=100` → HTTP 200; 4 items.
6. `GET /api/v1/crops?limit=100` → HTTP 200; 31 items.
7. `GET /api/v1/crops?search=rice&limit=5` → HTTP 200; 1 result.
8. Selected crop detail and profile → HTTP 200; Arecanut is pending and has zero source references.
9. Selected crop varieties → HTTP 200; total 0.
10. Selected district crop associations → HTTP 200; total 0.
11. The React UI rendered the district selector, crop cards, and selected crop profile from these actual API/database records. Empty and pending states were shown without fabricated recommendations.

## CORS root cause and safe local correction

The API's configured allowed origin is `http://localhost:5173`: an OPTIONS preflight from that origin returned HTTP 200 with `Access-Control-Allow-Origin: http://localhost:5173`. When the same Vite app was opened as `http://127.0.0.1:5173`, browser requests to the API failed because the origin did not match; the browser displayed “Failed to fetch” and logged a CORS error.

The successful verification used the already-allowed `http://localhost:5173` origin. No CORS, frontend, or backend configuration was changed. If `127.0.0.1` must also be supported, the smallest correction is to have the operator explicitly add that exact origin to `FRONTEND_ORIGINS` and restart the API; no application-code change is needed.

## Conclusion

The complete **local read-only catalogue demonstration workflow**—React dashboard → FastAPI → configured PostgreSQL/PostGIS → API responses → React catalogue/profile—**is verified**. It is not evidence that the whole application is production-ready, that the database is definitely hosted by Supabase, or that unavailable ML/weather/RAG/disease features work. No authentication or database writes were used in this verification.
