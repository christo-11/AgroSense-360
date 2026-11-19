# Deployment Guide

## Status

This document describes deployment requirements; it does not claim that any environment is deployed, production-ready, or tested. The repository has Dockerfiles and a local Docker Compose stack, but the current Compose database is local PostGIS. No public portfolio or commercial deployment has been run.

## Deployment modes

### Local development

Use the instructions in [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md). Keep `PUBLIC_DEMO_MODE=false` and `VITE_PUBLIC_DEMO=false` to use local authentication and farm/plot flows.

### Public portfolio demonstration

Deploy a static frontend build with `VITE_PUBLIC_DEMO=true` and `VITE_API_URL` pointing to the intended API. Deploy the backend with `PUBLIC_DEMO_MODE=true` and `FRONTEND_ORIGINS` set to the exact HTTPS frontend origin. Both flags are required. The API status endpoint reports the backend mode; the UI warns if it is not enabled.

Before exposing the API, use a sanitized database, inspect all public crop/source fields, verify catalogue rights, restrict network/database access, and run the smoke checks below. Publicly accessible catalogue GET endpoints are intentionally separate from owner-scoped farm endpoints.

## Environment and secret boundaries

Backend secrets belong in the hosting provider's secret manager: database URL/password, JWT signing secret, admin/reviewer allowlists, dataset approval HMAC key, and any provider credentials. Never commit `.env` or put secrets in frontend build arguments. `VITE_API_URL` and `VITE_PUBLIC_DEMO` are public build-time settings.

Use a private database connection and least-privilege database role. Do not place a Supabase service-role key in the browser; this app uses SQLAlchemy server-side database access. Restrict database ingress to the API where possible. Enable TLS and rotate credentials if exposed.

Set explicit CORS origins and methods. Do not use wildcard origins with credentials. Keep secrets out of logs, error responses, source maps, and telemetry. The current `/api/v1/status` reports connectivity/mode but should not be expanded to return secret values.

## Database and migrations

For local Compose, the API waits for its PostGIS database and runs `alembic upgrade head` on container start. For an existing Supabase or production database:

1. Confirm the target database and current Alembic revision.
2. Take and verify a restorable backup.
3. Inspect `alembic history` and the target migration SQL/operations.
4. Confirm PostGIS is enabled and the connection search path resolves its extension schema.
5. Apply `alembic upgrade head` in a controlled release step.
6. Verify current revision, health, catalog counts, indexes, and API smoke tests.

Do not use `downgrade` as a recovery plan on a populated database. Restore from a verified backup or apply a reviewed forward-fix migration. No migration is required for public demo mode.

## Health, monitoring, and recovery

- `GET /health` checks that the API process responds.
- `GET /health/database` performs a database readiness query.
- `GET /api/v1/status` reports integration/model availability and `public_demo_mode`.

The repository does not currently configure centralized monitoring, alerting, tracing, or a backup scheduler. Before a commercial service, add structured redacted logs, request/error/latency metrics, alert ownership, retention policy, database backup schedule, point-in-time recovery where appropriate, and a tested restore/rollback procedure.

Farm and plot data are private user data. Define retention and deletion policies and test backup access controls. Never put private boundaries into static frontend assets or public logs.

## Public demo smoke checks

Against the intended deployed API, verify without using real farmer accounts:

1. `/health` and `/health/database` return the expected status.
2. `/api/v1/status` reports `public_demo_mode: true`.
3. Public district/crop/profile GET routes expose only reviewed public catalogue data.
4. `/api/v1/auth/register` and `/api/v1/auth/token` return `503`.
5. All farm, plot, summary, and admin routes reject valid local/test tokens with `503`.
6. Frontend has no sign-up, login, farm editing, plot boundary, or upload controls.
7. Browser network inspection shows no secrets and no unexpected private API calls.
8. CORS rejects unlisted origins; HTTPS and host/database access restrictions are verified.

Do not run destructive smoke tests against production or real farmer records.

## Deployment limitations

No hosting platform, Supabase production project, DNS, TLS, monitoring vendor, paid API, or production secret has been configured or verified in this work. Choose providers and costs separately. A successful local build or test suite is not evidence of deployment readiness.
