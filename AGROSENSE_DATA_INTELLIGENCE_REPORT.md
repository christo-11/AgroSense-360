# AgroSense-360 Agricultural Data Intelligence Report

## Executive summary

Implemented a read-only Agricultural Data Intelligence dashboard backed by FastAPI, the existing JSON governance and quality artifacts, and live database counts. The dashboard presents source approvals, acquisition records, weather-data quality, crop and district catalogue coverage, provenance, and training eligibility. It makes no predictions and does not present the ERA5-Land archives as training data.

The source inventory contains 13 candidates and no commercially approved source: 11 are `CONDITIONAL` and 2 are `BLOCKED`. Three sources are separately approved for portfolio research only. At the Stage 16 snapshot, the inventory said ERA5-Land was `not_downloaded` while the manifest described two user-reported archive requests. Stage 17 reconciled that discrepancy using existing files and quality evidence: ERA5-Land is now `ACQUIRED_VERIFIED`, archive integrity is `VERIFIED`, and data quality remains `QUALITY_REJECTED`. Its product version remains unpinned and its exact CDS request parameters remain unconfirmed.

## Implemented API

All endpoints are GET-only, versioned under `/api/v1`, return validated Pydantic response models, and project only whitelisted metadata. Source, approval, acquisition, training-eligibility, and provenance lists accept `limit` (1–100) and `offset` pagination.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/data-intelligence/summary` | Source, approval, acquisition, archive-integrity, data-quality, training, and weather status counts |
| `GET /api/v1/data-intelligence/sources` | Paged source inventory with separate approval, acquisition, integrity, and quality statuses |
| `GET /api/v1/data-intelligence/approvals` | Paged approval/restriction status plus full status counts |
| `GET /api/v1/data-intelligence/acquisitions` | Reconciled acquisition state, live file existence/size checks, archive integrity evidence, quality decision, and sanitized manifest artifacts |
| `GET /api/v1/data-intelligence/quality` | Overall quality decision and archive-level quality evidence |
| `GET /api/v1/data-intelligence/weather-coverage` | Dynamic weather timestamp counts, coverage windows, and observed gaps |
| `GET /api/v1/data-intelligence/training-eligibility` | Fail-closed metadata assessment and reasons; does not grant training clearance |
| `GET /api/v1/data-intelligence/provenance` | Paged source/version and archive integrity provenance |
| `GET /api/v1/data-intelligence/catalogue-completeness` | Read-only district, crop, profile, variety, and suitability counts from PostgreSQL |

Metadata is validated before use. Missing or malformed files return a safe HTTP 503 response and a sanitized log message. Provenance validation checks source identifiers, duplicate request IDs/references, timestamps, checksum formats and agreement, file existence and size, quality-report agreement, and training-permission contradictions. API responses omit local paths, source/download URLs, hostnames, request references, credentials, and other nonessential acquisition metadata. The catalogue endpoint issues SELECT-only queries and returns HTTP 503 if its database read fails.

## Dashboard

Added **Data intelligence** navigation in both workspace and portfolio navigation. The responsive dashboard displays:

- Registered source and approval counts, keeping portfolio-only approval separate from commercial approval.
- Source permission, inventory acquisition state, archive integrity, data quality, and training eligibility as separate statuses.
- ERA5-Land quality, dynamic timestamp counts, UTC coverage windows, observed intervals/gaps, and clearly labeled global-grid missingness.
- Live crop and district catalogue counts, profile verification, varieties, and district suitability associations.
- Per-source governance status, training-blocker explanations, and provenance details including archive checksums and integrity flags.
- Loading, partial-error, whole-dashboard error/retry, and empty states.

There are no charts because the current evidence is best represented as discrete coverage and quality facts. No synthetic measurements, agronomic recommendations, or model outputs are generated.

## Stage 16 verification evidence (historical)

### Live application

Using the existing project configuration, without opening secret files or changing database settings:

- Frontend responded with HTTP 200 at `http://localhost:5173`.
- `/health` and `/health/database` returned HTTP 200.
- Every implemented data-intelligence endpoint returned HTTP 200, including the live catalogue query.
- Live database-backed catalogue counts were: 14 districts, 4 crop categories, 31 crops, 31 profile records, 0 verified profiles, 0 varieties, and 0 district-crop associations.
- The browser loaded the dashboard using live API responses. The inspected page showed the inventory/manifest disagreement, 2 and 12 weather timestamps, 65.87% global-grid missingness for each archive, and the live catalogue counts. No dashboard alert or browser console/network error was present in the fresh verification page.
- At a 390-pixel viewport, the dashboard had no horizontal document overflow and no role-alert errors.
- Endpoint responses were checked for sensitive path/URL fields; none were present.

### Tests and builds

- Backend: `python -m pytest -q` from `backend/` — **40 passed**.
- Frontend component tests: `npm test` — **3 passed** (loading, populated render, and failure/retry state).
- Frontend type check and production build: `npm run build` — **passed**.
- `git diff --check` — **passed**.

The production build still reports the existing large FarmTwin chunk warning (838.42 kB minified). It is not caused by the dashboard and was not changed in this stage. Installing the frontend test dependencies reported 6 npm audit advisories (3 moderate, 1 high, 2 critical); dependency remediation was not part of this implementation.

Backend tests use the repository's temporary SQLite test fixture. No writes, schema changes, migrations, or seeds were performed against the configured live database. No datasets were downloaded, no external acquisition APIs were called, and no models were trained.

## Stage 17 provenance reconciliation and verification

The Stage 16 inventory/manifest discrepancy is now reconciled with explicit, separate decisions:

| Dimension | ERA5-Land result |
| --- | --- |
| Portfolio permission | `APPROVED_PORTFOLIO_RESEARCH_ONLY` |
| Commercial/source approval | `CONDITIONAL` |
| Acquisition | `ACQUIRED_VERIFIED` |
| Archive integrity | `VERIFIED` for both recorded archives |
| Data quality | `QUALITY_REJECTED`; quality report remains `NEEDS_MORE_DATA` / `REJECT_FOR_TRAINING` |
| Product version | Unpinned (`dataset_version: null`) |
| ML training eligibility | Not eligible; total eligible-source count remains 0 |

Both archive files exist at their recorded byte sizes. Their independently recomputed SHA-256 digests match the manifest and quality-report records, and the recorded ZIP CRC results pass. The original acquisition request records and the prior `2026-11-19` inventory state are retained in the audit trail. The inventory now records the acquisition; the manifest carries an explicit `dataset_id`; the downloader will include that identifier in future manifests. The API validates the source/request relationship and filesystem sizes without returning paths or archive URLs. It does not recompute archive hashes or reopen ZIP members on each request.

The remaining provenance warning is material: the request-history MHT was not inspected, so exact request parameters remain unconfirmed. The product version is also unpinned. The two archives remain prohibited for training regardless of their verified acquisition and integrity status. Commercial approval remains unchanged.

Stage 17 checks:

- Backend: complete suite — **51 passed**. Tests use the existing project virtual environment with Pydantic `.env` loading disabled and the temporary SQLite fixture; no configured database was contacted.
- Frontend: `npm.cmd test` — **3 passed**.
- TypeScript and production build: `npm.cmd run build` — **passed**. The pre-existing 838.42 kB FarmTwin chunk-size warning remains.
- Dataset governance: read-only `load_inventory` succeeded for 13 sources; the existing training gate rejected ERA5-Land as `CONDITIONAL` before any training input was read.
- Data Intelligence API: endpoint tests passed, including live metadata reconciliation, status separation, missing files, size/checksum/timestamp validation, unknown approvals, training restrictions, and path-safe responses.
- Frontend dashboard: render tests passed for loading, populated evidence, unresolved provenance conflict warnings, and retryable errors.
- Pylance syntax/diagnostic checks: no diagnostics; both `_eligibility_item` call sites are signature-compatible.

No datasets were downloaded; no CDS or other external acquisition requests were made; no training was run; no credentials or secret files were accessed; and no database migrations or writes were performed.

## Remaining blockers and architectural notes

1. **Remaining provenance evidence:** the inventory/manifest state conflict is reconciled with an explicit `dataset_id`, audit trail, file-size checks, and recorded checksum/CRC evidence. The exact CDS request-history MHT was not inspected and the product version remains unpinned.
2. **Weather evidence:** both inspected archives are `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`. They are sparse, globally gridded samples, not a continuous Kerala-specific weather series.
3. **Catalogue evidence:** crop profile records exist, but none is verified; the database currently contains no varieties or district-crop suitability associations. A profile-record count is not evidence that profile fields are complete or agronomically validated.
4. **Training clearance:** all 13 candidates are ineligible based on their current metadata. The dashboard does not verify approval signatures or replace the existing signed-provenance governance gate.
5. **Operations:** metadata is read from repository JSON files at request time. A future deployment must package and version those artifacts consistently with the API. No new service or database schema is needed for the current read-only feature.

## Recommended next stage

**Stage 18 — Close remaining data-evidence gaps.** Verify the exact ERA5-Land CDS request parameters from the retained request-history MHT, pin the product version and applicable accepted terms, and define temporal/spatial quality acceptance criteria. In parallel, curate crop profiles, varieties, and district suitability records from attributable sources. Keep ML training blocked until approved, versioned, quality-checked data passes the existing governance gate.
