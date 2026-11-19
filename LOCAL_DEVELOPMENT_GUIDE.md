# Local Development Guide

## Requirements

- Node.js 22 or later and npm.
- Python 3.11 or later.
- PostgreSQL with PostGIS for a persistent local environment, or the existing isolated SQLite backend test setup.
- The repository's existing `.venv` and `node_modules` may be reused; do not recreate or reinstall them without a dependency failure.

## Configuration and secrets

The API settings loader reads the root `.env` file using an absolute path derived from `backend/app/config.py`; process environment variables override file values. Keep `.env`, `.env.local`, database URLs, JWT secrets, and provider credentials out of Git and out of `VITE_*` variables. The checked-in `.env.example` contains placeholders only.

Set at least:

- `DATABASE_URL` — local PostgreSQL/PostGIS URL or a deliberately selected Supabase connection URL.
- `JWT_SECRET` — a private random value of at least 32 characters.
- `FRONTEND_ORIGINS` — explicit local frontend origin, normally `http://localhost:5173`.
- `PUBLIC_DEMO_MODE=false` for local account, farm, and plot development.
- `VITE_API_URL=http://localhost:8000` and `VITE_PUBLIC_DEMO=false` for the local frontend.
- `AGRICULTURAL_ADMIN_EMAILS` only when testing authorized catalog administration.

Do not print `.env` or credential values to logs or chat. Supabase service-role keys and database passwords belong only in the backend secret store, never in the browser or a `VITE_*` setting.

## Start the application

Start the frontend from the project root:

```powershell
npm.cmd run dev
```

Start the backend in another PowerShell terminal after setting the local environment values:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
Pop-Location
```

The frontend is served at `http://localhost:5173`; FastAPI is served at `http://localhost:8000`. Configure CORS to include the exact frontend origin. The local Docker Compose stack uses its own PostGIS database; it is not the Supabase project.

Migrations are additive, but inspect the current revision and take a verified backup before applying them to any database with existing data. Do not downgrade the agricultural catalog migration in a database containing catalog content.

## Tests and checks

Run backend tests against the isolated in-memory SQLite fixture:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
```

Build and type-check the frontend:

```powershell
npm.cmd run build
```

This default test mode does not validate Supabase/PostGIS connectivity. Use only a separate test database for database integration tests; follow the README's hosted PostgreSQL test instructions and do not point destructive test setup at production.

## Dataset and model work

The Stage 6B eligibility gate is mandatory. The inventory currently contains no commercially approved dataset, and model training/inference Stages 7–9 remain stopped. Do not download, preprocess, train on, or present predictions from an unapproved dataset. ML libraries are optional and are not needed to run the API or frontend.

## Troubleshooting

- `503` from registration/login/farm routes: check `PUBLIC_DEMO_MODE`; it must be `false` for local private-workspace development.
- Portfolio UI warning that the backend did not confirm read-only mode: set backend `PUBLIC_DEMO_MODE=true` when `VITE_PUBLIC_DEMO=true`.
- CORS error: match `FRONTEND_ORIGINS` to the browser's exact scheme, hostname, and port.
- Database health unavailable: check the selected local database and `DATABASE_URL` without printing its value.
- Empty or pending crop details are intentional until sourced catalogue records are reviewed and verified.
