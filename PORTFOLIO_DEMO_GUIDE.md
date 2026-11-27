# AgroSense-360 Proposed Portfolio Demo Configuration

## Purpose and authorization boundary

This guide documents a technically available, read-only portfolio-demo configuration for local review. It does not authorize a public demonstration, data distribution, or deployment; current governance records mark portfolio/demo use **NOT AUTHORIZED**. Technical capability, public accessibility, read-only mode, or historical acquisition does not establish permission for an activity. Internal inventory licence/terms classifications assess publisher terms only; they are not source-owner permission, project-owner authorization, or activity-specific authorization. Publisher terms may support specified uses subject to exact resource terms and applicable conditions. Any proposed public demonstration, data sharing, or deployment requires separate, valid project-owner authorization and any required source-owner rights.

The prototype is not a launched agricultural service and is not production-ready. It presents the Kerala district/crop catalogue, record-level verification and source status, an architecture overview, and data licensing status.

This configuration does not provide sign-up, login, farmer records, farm/plot boundary display or editing, uploads, AI advice, weather observations, market prices, yield estimates, or prediction history. Those services are unavailable, not represented by sample results. The local development build retains the existing authenticated farm workspace.

## Read-only mode

The settings below describe technical controls only; enabling demo mode does not authorize public release or use of any dataset. For local testing, the frontend and backend can be configured for demo mode:

- Backend: `PUBLIC_DEMO_MODE=true`
- Frontend build: `VITE_PUBLIC_DEMO=true`
- Frontend API origin: `VITE_API_URL` (public build-time URL; never put credentials in any `VITE_*` setting)
- Backend CORS: `FRONTEND_ORIGINS` set to the exact public frontend origin(s)

The backend reports `public_demo_mode` from `GET /api/v1/status`. The UI checks this value and warns if the backend did not confirm demo mode. Backend demo mode returns `503` for registration, login, and every authenticated route, including farm, plot, dashboard, and admin operations. Public catalogue `GET` routes remain technically available. Frontend hiding is only a usability layer; the backend flag is the security boundary. These technical controls do not establish permission to expose the catalogue or demonstrate the application publicly.

The local demo-mode startup clears any browser-stored AgroSense token before calling the API. Do not rely on that behavior to secure a database or API. Verify the mode during local testing; this check is not authorization to share or deploy the frontend.

## Catalogue and verified information

The district and crop explorer calls the existing paginated public catalogue API. District/crop names are displayed as catalogue entries, not as evidence of cultivation suitability. A crop profile or district association is a confirmed claim only when its API verification status is `verified` and it includes source references. Pending and rejected records retain their status labels; empty profile fields are not inferred.

The Stage 6A migration seeds crop records with pending profiles and does not seed district suitability recommendations. Review and verify any production catalogue content before exposing it publicly. Do not insert farmer names, farm identifiers, private notes, precise farm locations, or private boundaries in public catalogue fields or source notes.

The Data Sources page reads the repository's non-secret source inventory. It displays internal publisher-terms classifications separately from the Stage 6B training/commercial review. Open-Meteo's free API carries an internal portfolio/research classification with attribution requirements; it is not integrated or queried. The classification is not source-owner permission, project-owner authorization, or permission to query, integrate, research, or publicly demonstrate the source. No source is approved for commercial reuse or model training.

## Local preview of the demo-mode build

These commands are for a local technical preview only. They do not authorize a public demonstration, data distribution, or deployment.

In PowerShell, from the project root:

```powershell
$env:VITE_PUBLIC_DEMO = "true"
$env:VITE_API_URL = "http://localhost:8000"
npm.cmd run dev
```

In a second terminal, start the backend with `PUBLIC_DEMO_MODE=true` and a configured local database and safe JWT secret. Use the local-development instructions in [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md). Confirm `GET /api/v1/status` reports `public_demo_mode: true` for local testing. Do not share or publicly deploy based on this check; that requires separate, valid project-owner authorization and any applicable source-owner rights.

For a local static preview, set the same `VITE_*` values before `npm.cmd run build`. The values are embedded in public JavaScript and must not contain secrets. A successful build does not authorize public release.

## Technical release safeguards (not authorization)

The following are technical safeguards for a possible future release, not approval to release. Public demonstration, data distribution, and deployment remain **NOT AUTHORIZED** unless separately authorized for the exact activity.

- [ ] Use a sanitized database and review every public catalogue/source field for personal or private data.
- [ ] Set backend `PUBLIC_DEMO_MODE=true`; check `GET /api/v1/status`.
- [ ] Set frontend `VITE_PUBLIC_DEMO=true` and a public `VITE_API_URL`.
- [ ] Set exact HTTPS CORS origins; do not use `*`.
- [ ] Verify registration, login, authenticated farm reads/writes, and admin writes return `503` in demo mode.
- [ ] Verify district/crop GET routes return only intended public catalogue content.
- [ ] Verify unresolved source rights and model/data availability are visible.
- [ ] Do not advertise predictions, forecasts, diagnoses, or recommendations unless their sources/models have independently passed review and are actually deployed.
- [ ] Confirm HTTPS, backups, logs, database grants, and hosting access controls with the deployment owner.

No public deployment is performed or claimed by this guide.
