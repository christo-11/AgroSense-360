# AgroSense-360 — Stage 14 Test Results

**Run date:** 2026-11-20  
**Repository state:** Existing user changes were preserved. No application source, configuration, migration, or schema was edited for this audit.

## Secret and side-effect boundaries

- `.env` and `.cdsapirc` were not read, printed, or modified.
- Python validation disabled the Pydantic settings dotenv file source and supplied only test-only reviewer/signing values. Dataset governance subprocess tests inherited those values, so the review helper did not need to read `.env`.
- Vite build/preview used an empty temporary env directory; no root dotenv file was loaded.
- No external API calls, dataset requests/downloads, model training, database migrations, or Docker services were started.

## Executed checks

| Check | Exact invocation / setup | Result | What it proves / does not prove |
|---|---|---|---|
| Backend unit/API/dataset governance tests | From `backend`, the repository `.venv` Python ran a small `-c` wrapper that disabled `Settings.model_config['env_file']`, removed `AGROSENSE_TEST_DATABASE_URL` to select the SQLite fixture, set test-only reviewer/signing values, then called `pytest.main(['-q'])`. | **33 passed in 3.23s.** | Covers `tests/test_api.py`, `tests/test_agriculture_catalog.py`, and `tests/test_dataset_governance.py`. The ordinary fixture used in-memory SQLite. Its PostGIS functions are stubs; this is not a PostgreSQL/PostGIS integration result. |
| Frontend TypeScript project check | `.\node_modules\.bin\tsc.cmd -b` | **Passed (exit 0).** | TypeScript project build/type check passed for `src`. |
| Frontend production bundle | `node --input-type=module -e "import { build } from 'vite'; await build({ envDir: process.env.AGROSENSE_EMPTY_ENV });"` with `AGROSENSE_EMPTY_ENV` pointing to an empty temporary directory. | **Passed.** Vite transformed 2,536 modules. | Production build succeeded. Vite warned that the lazy-loaded `FarmTwin` chunk is 838.42 kB minified, above the 500 kB warning threshold; the main JS chunk is 366.70 kB. |
| Frontend build-script attempt | `npm.cmd run build -- --envDir <temporary-empty-directory>` | **Invocation failed at Vite CLI:** Vite 5 reported unknown option `--envDir`. The `tsc -b` portion ran successfully before Vite rejected the option. | This was a command-line option mistake, not an application compile error. The explicit `tsc` check and Vite programmatic production build above then passed. |
| Built frontend browser smoke | Started Vite preview on `http://127.0.0.1:4173/`; opened it in the integrated browser; clicked **Crop catalogue**; waited for API requests. | **UI loaded and navigation rendered.** With no backend listening at `localhost:8000`, the catalogue showed two visible `Failed to fetch` alerts, zero crop cards, and no remaining loading state after settling. Preview was stopped afterward. | Confirms the built shell/navigation load and that unavailable API results are not fabricated. Does not verify live API connectivity, catalogue rendering from a database, or complete browser behavior. |
| API health assertions | Included in `tests/test_api.py::test_health_authentication_and_openapi` using FastAPI `TestClient` and SQLite fixture. | **Passed as part of 33 tests.** `/health`, `/health/database`, and `/api/v1/status` assertions succeeded. | Confirms in-process test behavior and SQLite `SELECT 1`; not a live service or production database health check. |
| Migration graph | From `backend`, Alembic Python API `command.history(cfg); command.heads(cfg)` with dotenv loading disabled. | **Passed.** Chain ends at `5d3cbf283629` (`add_agricultural_master_catalog`), reported as head. | Confirms repository migration graph only. No `alembic current` query was run against a database. |
| Dataset governance | Included in backend suite; no training entry point was run except tests invoking it with an explicitly blocked dataset and nonexistent temporary input. | **Passed as part of 33 tests.** Blocked sources were rejected before ML imports/artifact creation. | Tests policy-gate behavior only. No dataset was acquired, inspected, or used for training by this audit. |

## Not run / blocked

- **Supabase/PostgreSQL connection:** not run. A project URL/credentials were not supplied through a separately approved test configuration; `.env` was intentionally not inspected.
- **Real PostGIS integration:** not run. The test suite supports it when a separate `AGROSENSE_TEST_DATABASE_URL` is provided and expects PostGIS plus revision `5d3cbf283629`. The audit deliberately forced the isolated SQLite fixture.
- **Current migration status (`alembic current`):** not run; there was no approved target database connection. Static `history`/`heads` is not a substitute.
- **Live API process and HTTP health check:** not started. TestClient health assertions passed; browser smoke confirmed the API was unreachable at the default URL.
- **Docker/Compose build and deployment:** not run. Static configuration was reviewed, but no database/container/deployment side effects were initiated.
- **Live dataset ingestion, provider requests, ML training/inference, LLM/RAG, and valid image inference:** not run and not represented as working.

## Outcome

The frontend type-check/build and all 33 backend tests pass within their stated boundaries. The audit has **no evidence** of a live Supabase/PostGIS database, a current deployed Alembic revision, or a functioning backend-to-browser database workflow. The largest remaining validation blocker is a separately configured non-production PostGIS database.
