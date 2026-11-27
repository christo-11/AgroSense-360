# AgroSense-360 Stage 17 Provenance Reconciliation Report

**Reconciled:** 2026-11-20  
**Scope:** Existing ERA5-Land metadata and archive files; read-only provenance and governance changes. No acquisition or model training.

## Outcome

The source inventory was stale relative to the acquisition manifest and files. Evidence supports that both recorded ERA5-Land archives were acquired and pass the available archive-integrity checks. Their data quality remains insufficient and explicitly rejected for training. Source permission, acquisition, archive integrity, data quality, and training eligibility remain separate decisions.

## Evidence inspected

- `data/metadata/source_inventory.json`
- `data/metadata/era5_land_download_manifest.json`
- `data/metadata/era5_land_quality_report.json`
- `DATASET_INVENTORY.md`, `DATASET_ACQUISITION_REPORT.md`
- Existing `backend/app/data_intelligence.py`, `backend/scripts/dataset_governance.py`, and `backend/scripts/download_era5_requests.py`
- Existing Data Intelligence and dataset-governance tests
- `AGROSENSE_DATA_INTELLIGENCE_REPORT.md` and `AGROSENSE_DATA_QUALITY_DOCUMENTATION.md`
- The two archive files already present under `data/raw/weather/era5_land/`

No `.env` or `.cdsapirc` content, credentials, connection strings, or archive URLs were accessed or exposed.

## ERA5-Land archive evidence

| Request | Archive | Recorded format | Recorded and observed size | Retrieval timestamp (UTC) | SHA-256 / ZIP evidence |
| --- | --- | --- | ---: | --- | --- |
| 1 | `era5_land_request_1.zip` | NetCDF | 647,003,080 bytes | 2026-11-20 02:22:48.871335 | Recomputed digest matches the manifest and quality report; ZIP CRC `PASS` |
| 2 | `era5_land_request_2.zip` | GRIB | 2,026,384,498 bytes | 2026-11-20 02:23:35.455009 | Recomputed digest matches the manifest and quality report; ZIP CRC `PASS` |

Both named files exist, and actual byte sizes match the manifest and quality report. Their request references and archive names correspond to the downloader's fixed request records. The manifest records successful retrieval as user-reported; the request-history MHT was not inspected, so the exact CDS query parameters cannot be independently confirmed. The historical user-reported approximate sizes are reversed relative to the observed archive sizes; those original values were not rewritten.

The API rechecks file existence and byte size and compares checksum assertions in metadata. It does not recompute file hashes or inspect ZIP members during an API request. The Stage 17 file/hash/ZIP findings above are from the existing files and prior recorded quality evidence, not from a new acquisition.

## Reconciled status by decision

| Decision | Current result | Evidence / interpretation |
| --- | --- | --- |
| Internal portfolio licence/terms classification | `APPROVED_PORTFOLIO_RESEARCH_ONLY`; commercial review `CONDITIONAL` | Stage 17 recorded an internal inventory classification only. It is not a source-owner grant or project-owner authorization; activity-specific use remains subject to separate valid authorization and applicable source-owner rights. |
| Acquisition | `ACQUIRED_VERIFIED` | Both files exist, manifest request references are present, actual sizes match, and recorded checksum/integrity evidence agrees. |
| Archive integrity | `VERIFIED` | SHA-256 records agree and the quality report records ZIP CRC `PASS` for both. |
| Data quality | `QUALITY_REJECTED` | Both quality records are `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`; temporal coverage is inadequate and other quality concerns remain. |
| Dataset version | `ACQUIRED_VERSION_UNPINNED` | `dataset_version` remains null; archive existence does not identify a pinned product version. |
| Training eligibility | Not eligible; total eligible-source count is `0` | Commercial status is conditional, training quality/relevance are not verified, product version is unpinned, and the quality report rejects these archives. |

## Reconciliation changes

- Updated the ERA5-Land source inventory from stale `not_downloaded` / `NOT_ACQUIRED` values to `acquired`, `ACQUIRED_VERIFIED`, `VERIFIED`, and `QUALITY_REJECTED`. Recorded the two-file aggregate size and acquisition date. The source-level checksum remains null because each archive has its own checksum in the manifest.
- Updated the inventory's raw-data-directory presence flag based on the files already present.
- Added `dataset_id: era5_land` and a reconciliation audit record to the manifest. The audit preserves the prior inventory state and check date, leaves historical request records and size estimates intact, records the current independent status dimensions, and states the known limitations.
- Updated the existing downloader to emit the stable dataset identifier in future manifests. It was not executed.
- Updated the read-only `/api/v1/data-intelligence` responses with separate acquisition, archive-integrity, data-quality, explanation, and validation-warning fields. Existing fields remain; no local paths or archive URLs are returned.
- Updated the dashboard to display approval, acquisition, integrity, quality, training eligibility, and provenance conflicts as distinct statuses.
- No source license or approval decision was changed.

## Validation and tests

The API validates inventory source IDs and approval statuses, manifest source association, duplicate request IDs/references, required archive metadata, timezone-aware retrieval timestamps, SHA-256 format and recorded checksum agreement, archive existence and sizes, ZIP evidence, quality-report request/size/checksum agreement, and training-eligibility contradictions. Missing metadata and archives fail closed with explicit unresolved statuses; private paths are never included in responses.

- Backend full suite: **51 passed**. Executed using the existing project virtual environment, with Pydantic `.env` loading disabled and the repository's temporary SQLite fixture.
- Frontend tests: `npm.cmd test` — **3 passed**.
- TypeScript and production build: `npm.cmd run build` — **passed**. The build retains the existing 838.42 kB FarmTwin chunk-size warning.
- Governance validation: inventory loaded successfully (13 sources); the existing training gate rejected ERA5-Land because it is `CONDITIONAL`.
- Data Intelligence API tests cover current reconciliation, missing archive, missing location metadata, size mismatch, invalid/mismatched checksums, invalid timestamps, duplicate references, absent source ID, invalid approval status, training restrictions, and path-safe output.
- Dashboard tests cover loading, populated evidence, unresolved conflict/warning display, and retryable API failure.
- Pylance syntax and diagnostics found no issues; both `_eligibility_item` callers passed signature compatibility checks.

All tests used temporary fixtures or the in-memory SQLite fixture. No live database was contacted or written.

## Remaining warnings and blockers

1. The supplied request-history MHT was not inspected; exact variables, dates, and geographic bounds remain unconfirmed.
2. The exact ERA5-Land product version is not pinned.
3. Both archives remain rejected for training because of sparse/irregular temporal coverage and unresolved quality concerns. The reported missingness values are global-grid estimates, not Kerala-specific rates.
4. The commercial review remains `CONDITIONAL`. Stage 17's internal portfolio licence/terms classification and cited attribution requirements are historical inventory findings; they do not evidence source-owner permission or project-owner authorization. This report does not establish activity-specific authorization.
5. Other crop profiles, varieties, and district suitability associations remain incomplete or unverified.

No datasets were downloaded, no external acquisition calls were made, no model was trained, no database writes or migrations were performed, and no credentials were accessed.

## Recommended next stage

**Stage 18 — Close remaining data-evidence gaps.** Verify the exact request parameters from the retained MHT, pin the ERA5-Land product version and applicable terms evidence, and define temporal/spatial quality acceptance criteria. Continue curating crop profiles, varieties, and district suitability with attributable sources. Keep training disabled until the existing signed approval/provenance gate passes on adequate, quality-accepted data.
