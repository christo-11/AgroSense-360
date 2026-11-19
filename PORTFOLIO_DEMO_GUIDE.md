# AgroSense-360 Public Portfolio Demonstration

## Purpose and current scope

This is a non-commercial, read-only portfolio demonstration of the existing AgroSense-360 prototype. It is not a launched agricultural service and is not production-ready. It presents the Kerala district/crop catalogue, record-level verification and source status, an architecture overview, and data licensing status.

The portfolio build does not provide sign-up, login, farmer records, farm/plot boundary display or editing, uploads, AI advice, weather observations, market prices, yield estimates, or prediction history. Those services are unavailable, not represented by sample results. The local development build retains the existing authenticated farm workspace.

## Read-only mode

The frontend and backend must both be configured for demo mode:

- Backend: `PUBLIC_DEMO_MODE=true`
- Frontend build: `VITE_PUBLIC_DEMO=true`
- Frontend API origin: `VITE_API_URL` (public build-time URL; never put credentials in any `VITE_*` setting)
- Backend CORS: `FRONTEND_ORIGINS` set to the exact public frontend origin(s)

The backend reports `public_demo_mode` from `GET /api/v1/status`. The portfolio UI checks this value and warns if the backend did not confirm demo mode. Backend demo mode returns `503` for registration, login, and every authenticated route, including farm, plot, dashboard, and admin operations. Public catalogue `GET` routes remain available. Frontend hiding is only a usability layer; the backend flag is the security boundary.

The demo startup clears any browser-stored AgroSense token before calling the API. Do not rely on that behavior to secure a database or API. Deploy the backend in demo mode and verify the check below.

## Catalogue and verified information

The district and crop explorer calls the existing paginated public catalogue API. District/crop names are displayed as catalogue entries, not as evidence of cultivation suitability. A crop profile or district association is a confirmed claim only when its API verification status is `verified` and it includes source references. Pending and rejected records retain their status labels; empty profile fields are not inferred.

The Stage 6A migration seeds crop records with pending profiles and does not seed district suitability recommendations. Review and verify any production catalogue content before exposing it publicly. Do not insert farmer names, farm identifiers, private notes, precise farm locations, or private boundaries in public catalogue fields or source notes.

The demo's Data Sources page reads the repository's non-secret source inventory. It separates portfolio rights from the Stage 6B training/commercial approval gate. Open-Meteo's free API is marked portfolio/research-only with attribution; it is not integrated or queried. This status is not commercial permission. No source is approved for commercial reuse or model training.

## Local preview of the public build

In PowerShell, from the project root:

```powershell
$env:VITE_PUBLIC_DEMO = "true"
$env:VITE_API_URL = "http://localhost:8000"
npm.cmd run dev
```

In a second terminal, start the backend with `PUBLIC_DEMO_MODE=true` and a configured local database and safe JWT secret. Use the local-development instructions in [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md). Confirm `GET /api/v1/status` reports `public_demo_mode: true` before sharing the frontend.

For a static build, set the same `VITE_*` values before `npm.cmd run build`. The values are embedded in public JavaScript and must not contain secrets.

## Public release checklist

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
