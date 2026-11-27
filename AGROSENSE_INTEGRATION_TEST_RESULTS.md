# AgroSense-360 — Stage 15 Integration Test Results

**Run date:** 2026-11-20  
**Environment:** Existing repository `.venv`, existing backend settings, local Vite development server. Secret values were not inspected or emitted.

## Commands and checks performed

| Check | Invocation / method | Result |
|---|---|---|
| Backend startup | From `backend`, started `..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning`. | Process remained running. No warning/error lines were emitted at warning log level. Health and status endpoints responded successfully. |
| API health | Read-only HTTP GETs to `http://127.0.0.1:8000/health`, `/health/database`, `/api/v1/status`. | **200, 200, 200.** Status fields: API online, database connected, public demo mode false. |
| PostgreSQL and catalogue SQL | Python using `app.database.engine`; `SELECT current_setting('server_version')`, PostGIS extension/version/schema query, Alembic revision query, and count queries for districts/crops/categories. | **Passed.** PostgreSQL 17.12; PostGIS 3.3.7 in `extensions`; revision `5d3cbf283629`; 14 districts, 31 crops, 4 categories. |
| PostGIS function and SRID | `SELECT ST_SRID(ST_SetSRID(ST_MakePoint(0, 0), 4326))` through the configured engine. | **Passed:** `4326`. |
| Public list endpoints | GET `/api/v1/districts?limit=100`, `/api/v1/crop-categories?limit=100`, `/api/v1/crops?limit=100`. | **200 each.** Totals 14, 4, and 31; first page item shapes contained expected IDs/names and crop category. |
| Public detail endpoints | GET for one returned crop ID: `/api/v1/crops/{id}`, `/profile`, `/varieties?limit=100`; one returned district ID: `/api/v1/districts/{id}/crops?limit=100`. | **200 each.** Profile verification `pending`, source count 0, variety total 0, district association total 0. |
| Catalogue search | GET `/api/v1/crops?search=rice&limit=5`. | **200**, total 1. |
| Vite development server | `npm.cmd run dev -- --host 127.0.0.1 --port 5173` (package script also supplies `--host 0.0.0.0`). | Vite 5.4.21 ready; HTTP response from both `localhost:5173` and `127.0.0.1:5173` was 200. |
| Browser dashboard | Opened `http://localhost:5173`, then used the dashboard Refresh control and waited for the backend status. | Dashboard heading rendered; connection banner displayed “Workspace connected”; no console errors in this pass. |
| Browser catalogue | Navigated to Crop catalogue, waited for real records, selected Alappuzha and Arecanut. | 31 crop cards; 14 district options; pending profile and source/variety/association empty states appeared. No console errors or failed API requests in the successful localhost-origin pass. |
| Loading/empty/error UI states | Observed initial catalogue loading labels, then the completed response; inspected no-variety/no-association/pending profile states; opened the app at `127.0.0.1:5173` to exercise the origin mismatch. | Loading and empty states verified. The mismatched origin produced CORS console errors and visible “Failed to fetch” alerts. Correct origin `localhost:5173` passed. |
| CORS preflight | OPTIONS preflight to `/api/v1/status` with `Origin: http://localhost:5173`, requested method GET and expected headers. | **200**, `Access-Control-Allow-Origin: http://localhost:5173`. The `127.0.0.1:5173` browser origin was not allowed. |

The database and API SQL probes used only `SELECT`; API calls were public `GET` requests except the non-mutating preflight `OPTIONS`. No login, registration, farm/plot mutation, migration, seed, or schema operation was performed.

## Browser error detail

- At `http://127.0.0.1:5173`, the browser console reported that fetch to the API was blocked by CORS because the response did not include `Access-Control-Allow-Origin` for that origin. The app displayed “Failed to fetch”.
- At `http://localhost:5173`, which matches the configured CORS origin, the dashboard status refresh and catalogue/profile flow succeeded. The final tested pass reported no console errors or failed API requests.
- The dashboard correctly shows farm metrics and weather/soil/crop-health results as unavailable; no farm account or test data was created to populate them.

## Not claimed / not tested

- Supabase provider identity was not asserted from a hostname or connection string. PostgreSQL/PostGIS capabilities were directly verified through the configured application engine.
- Authenticated user, farm, and plot flows were not run because they would require account/session handling and are outside the read-only public catalogue workflow.
- Weather, market, soil, disease inference, ML, and copilot endpoints remain unavailable and were not claimed as functional.
- No production deployment, external provider, or Supabase control-plane configuration was tested.

## Overall outcome

**The local read-only catalogue integration is verified end to end.** The one observed integration issue was a development-origin mismatch: the API allows `http://localhost:5173`, not `http://127.0.0.1:5173`. Using the configured localhost origin resolved the browser CORS failure without changing application or database configuration.
