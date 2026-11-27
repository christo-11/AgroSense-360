# AgroSense-360 — Tomorrow's Portfolio Demo Action Plan

**Goal:** Demonstrate the smallest real, reliable workflow supported by the current code while clearly distinguishing catalogue records from verified agricultural advice. No synthetic observations, ML predictions, forecasts, diagnoses, or recommendations.

## Priority plan

| Priority | Task and completion criteria | Estimate | Dependencies |
|---|---|---:|---|
| **Critical** | **Resolve non-production database configuration and verify the current PostGIS target.** Use an isolated local PostGIS database or explicitly authorized non-production Supabase project. Run `/health/database`, confirm PostGIS/SRID support, query `alembic current`, and check that the existing migration head is `5d3cbf283629`. Do not point test setup at production or alter migrations. | 1–3 hours | Database owner provides a disposable target and credentials via the approved secret/environment mechanism; network access. |
| **Critical** | **Run the public catalogue workflow end to end.** Align backend `PUBLIC_DEMO_MODE=true`, frontend `VITE_PUBLIC_DEMO=true`, `VITE_API_URL`, and exact `FRONTEND_ORIGINS`; verify status, 14 districts, 4 categories, and 31 seeded crop entries, then search/select a crop and show pending/blank profile data honestly. Confirm registration, login, and private farm routes are disabled by the backend. | 1–2 hours | Critical database task completed; reviewed non-production database contents; frontend/API reachable. |
| **High** | **Reconcile the ERA5-Land archive/provenance conflict before using or mentioning the files.** Existing local ZIP names/sizes conflict with `source_inventory.json` (`NOT_ACQUIRED`, `not_downloaded`, no path/version/checksum) and the downloader’s approximate request size mapping. Have the data owner match files to original requests, verify provenance and checksums, and correct metadata only after review. Do not download, extract, or use these archives until authorized. | 1–3 hours (review-dependent) | File/source owner, original request records, permitted license and provenance evidence. |
| **High** | **Make API-unavailable messaging actionable.** Replace generic network “Failed to fetch” presentation with a user-safe explanation and retry/recheck affordance; retain the explicit unavailable state and never insert fallback records. Verify both offline and HTTP error states in the browser. | 1–2 hours | Frontend owner; no backend/data dependency. |
| **High** | **Curate one real, source-backed catalogue claim only if evidence is available.** Review an official source, applicable license, Kerala relevance, exact claim, and attribution; then use the existing admin workflow to add source and verified profile/association. If evidence or approval is missing, keep the record pending and demonstrate the transparent empty state instead. | 2–4 hours or blocked | Authorized catalog admin; reviewer and provenance; authoritative source and licensing decision. |
| **Medium** | **Run the existing API suite against a disposable PostGIS database.** Set `AGROSENSE_TEST_DATABASE_URL` only in the test process; confirm extension and current revision prerequisites; exercise real polygon validity, SRID, serialization, and spatial indexes. Keep SQLite tests as fast unit coverage. | 2–4 hours | Isolated PostGIS database at current revision; database credentials available through approved configuration. |
| **Medium** | **Add a lightweight release smoke checklist/gate.** Verify frontend/backend demo flag parity, allowed CORS origins, database health, migration revision, catalogue counts, and disabled private routes before a public demo is shared. | 0.5–1 day | Working deployment target and release owner. |
| **Medium** | **Define minimum operational logs/alerts and recovery checks.** Add redacted structured request/error logs and basic latency/availability monitoring; document backup and perform a restore test before any production claim. | 1–2 days | Hosting/database choice, ownership, retention and backup policy. |
| **Future** | **Build an approved-data ML lifecycle.** Only after dataset approval and real labels: establish repeatable splits, leakage/subgroup checks, model card, artifact checksum/version registry, offline evaluation, abstention thresholds, and a separately tested inference endpoint. | 1–3+ weeks, data-dependent | Approved data and labels, domain review, reproducible compute and evaluation criteria. |
| **Future** | **Implement grounded RAG only after corpus and evidence rules are approved.** Add provider interface, retrieval metadata, evidence IDs, citation validation, abstention, prompt-injection handling, and tests that citations actually support claims. | 1–3+ weeks | Approved source corpus, product requirements, provider/security review. |
| **Future** | **Add background processing only when ingestion/inference workload requires it.** Start with a simple managed/background-job design and persisted job status; avoid introducing microservices preemptively. | 2–5 days | Defined job workload, retry/idempotency and operational requirements. |

## Suggested demo run-of-show

1. Open the public portfolio build. Point out that the UI is read-only and the backend confirms public demo mode.
2. Show API/database status and district/category/crop counts from the live non-production API.
3. Search a crop and inspect its record. Explicitly identify whether the profile is `pending`, which fields are undocumented, and whether sources or district associations exist.
4. Explain that an empty association means “no sourced record is available,” not “the crop is unsuitable.”
5. Show the data-source/rights page and clearly state that no live weather, market, soil, disease, or AI output is available.
6. If the API/database setup is not verified, switch to a build/UI walkthrough and label the backend unavailable. Do not use database fixtures, hard-coded sample metrics, or fabricated recommendations to simulate a live result.

## Highest-priority next task

**Obtain an explicitly authorized non-production PostGIS connection and verify database health, PostGIS, and the current Alembic revision.** This is the current blocker to proving the frontend → FastAPI → database catalogue workflow. Do not inspect secret files to obtain the connection; have the environment owner provide it through the approved secret/config channel.
