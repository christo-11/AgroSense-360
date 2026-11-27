# AgroSense-360 Data Quality Documentation

## Scope and evidence sources

This dashboard reads the source inventory, ERA5-Land acquisition manifest, ERA5-Land quality report, and the live crop catalogue. At request time, the API checks recorded archive paths remain within the project data boundary, checks file existence and byte sizes, and compares manifest checksum claims with the quality report. It does not recompute archive hashes, reopen ZIP contents, infer missing agronomic facts, or run training. The JSON artifacts are validated on load; responses expose only whitelisted status and provenance fields, never local paths or archive URLs.

The source/license review was checked at `2026-11-19`; the manifest records two ERA5-Land archive requests on `2026-11-20`. Stage 17 reconciled the inventory with file and quality evidence without changing the historical request records or source approvals.

## Source review and acquisition status

### Source inventory

The inventory contains 13 dataset candidates:

| Status dimension | Recorded counts |
| --- | --- |
| Commercial approval | 11 `CONDITIONAL`; 2 `BLOCKED`; 0 `APPROVED` |
| Internal portfolio licence/terms classification | 3 `APPROVED_PORTFOLIO_RESEARCH_ONLY`; 2 `CONDITIONAL`; 1 `BLOCKED`; 7 `UNVERIFIED` |
| Inventory acquisition | 10 `not_downloaded`; 1 `acquired`; 1 `metadata_verified_only`; 1 `blocked_pending_commercial_use_decision` |
| Acquisition reconciliation | 1 source `ACQUIRED_VERIFIED`; 1 archive set `VERIFIED`; 1 source `QUALITY_REJECTED` |
| Pinned dataset version | No candidate has a pinned version; ERA5-Land is acquired with `ACQUIRED_VERSION_UNPINNED` |

`APPROVED_PORTFOLIO_RESEARCH_ONLY` is an internal inventory assessment of apparent publisher licence/terms compatibility for a limited, non-commercial portfolio/research category. It is not source-owner permission, project-owner authorization, or effective permission to access/acquire data or conduct research, public demonstration, ML training, redistribution, or deployment. Those activities require separate, valid, purpose-specific project authorization and applicable source-owner rights. The classification is distinct from commercial review and training eligibility.

### ERA5-Land provenance reconciliation

The prior source inventory snapshot (checked on `2026-11-19`) said `era5_land` was `not_downloaded`. The acquisition manifest records two requests on `2026-11-20`, each “Successful (reported by user; MHT not independently inspected)”:

| Request | Archive | Format | Manifest / observed size | Manifest retrieval time |
| --- | --- | --- | ---: | --- |
| 1 | `era5_land_request_1.zip` | NetCDF | 647,003,080 bytes | 2026-11-20 02:22:48 UTC |
| 2 | `era5_land_request_2.zip` | GRIB | 2,026,384,498 bytes | 2026-11-20 02:23:35 UTC |

Both archive files exist at their recorded sizes. Fresh SHA-256 calculations match both the manifest and quality-report checksum records; recorded ZIP CRC checks pass. The manifest request references and archive names correspond to the downloader's fixed request records. The inventory now records `download_status: acquired`, `acquisition_status: ACQUIRED_VERIFIED`, and `archive_integrity_status: VERIFIED`; the source-level `sha256` remains null because each archive has its own checksum. `dataset_version` remains null and the version status is `ACQUIRED_VERSION_UNPINNED`.

The original `not_downloaded` state and its `2026-11-19` check date are preserved in the manifest reconciliation audit trail. The historical request references, user-reported size estimates, request timestamps, and quality records were not overwritten. The approximate size estimates were reversed relative to the observed archive sizes and are retained as originally reported.

**Remaining provenance limitations:** the request-history MHT was not inspected, so exact CDS query parameters (variables, dates and geographic bounds) are not independently confirmed. The product version remains unpinned. These limitations are shown as dashboard warnings; they do not overturn the file, size, checksum-comparison, or ZIP CRC evidence.

## ERA5-Land quality findings

The quality report's overall decision is `NEEDS_MORE_DATA`; its overall training status is `REJECT_FOR_TRAINING`. Each archive-level decision has the same statuses.

| Archive request | Dynamic weather evidence | Global-grid missingness | Training decision |
| --- | --- | --- | --- |
| 1 (NetCDF) | 2 timestamps, 2024-01-03 03:00–06:00 UTC, 3 hours apart | 8,541,474 of 12,967,200 values missing per main field (65.87%) | `NEEDS_MORE_DATA`; `REJECT_FOR_TRAINING` |
| 2 (GRIB) | 50 variables with 12 timestamps each, 2011-01-11 13:00 to 2011-01-29 22:00 UTC; irregular observed gaps of 2, 7, 15, 63, and 327 hours | 4,270,737 of 6,483,600 points missing per time-varying field (65.87%) | `NEEDS_MORE_DATA`; `REJECT_FOR_TRAINING` |

The missingness percentages are global-grid metrics, not Kerala-specific quality rates. The grids intersect Kerala, but the assessment did not apply a Kerala administrative boundary or establish valid-cell coverage within Kerala. Static and singleton ancillary records do not extend the dynamic weather time series. The quality documentation also notes internal message-length discrepancies in two ancillary GRIB1 members.

**Use restriction:** neither archive supports a continuous historical or seasonal weather series. Do not use either archive for model training, predictions, or farm recommendations. The dashboard communicates availability and limitations only.

## Live catalogue completeness

The read-only API measured the following from the configured database during integration verification:

| Catalogue measure | Count |
| --- | ---: |
| Districts | 14 |
| Crop categories | 4 |
| Crops | 31 |
| Crop profile records | 31 |
| Verified crop profiles | 0 |
| Varieties | 0 |
| Districts with suitability associations | 0 |
| District-crop associations | 0 |

The 100% profile-record ratio means only that a profile row exists for every crop. It does **not** mean all profile fields are complete, verified, sourced, or agronomically appropriate. The current absence of verified profiles, varieties, and suitability associations remains visible in the dashboard.

## Quality and governance interpretation

- **`APPROVED_PORTFOLIO_RESEARCH_ONLY`:** an internal licence/terms compatibility classification only; it does not authorize project activity. Preserve applicable attribution and restrictions, and obtain separate project authorization and any required source-owner permission before use.
- **Conditional:** rights, scope, access, or other review conditions remain unresolved.
- **Blocked:** the current review blocks the proposed use.
- **Insufficient data:** the evidence is not adequate for the intended purpose.
- **Rejected for training:** explicitly disallow model training on that evidence.
- **Training eligibility:** the endpoint is fail-closed and metadata-only. It does not grant clearance; signed approval and provenance must still pass the existing governance implementation.

## Additional evidence required before model development

1. Inspect the retained request-history MHT and record exact CDS parameters; pin the selected product version and retain applicable license-acceptance evidence before any further project use. The inventory classification does not authorize use of the archives.
2. Define task-specific temporal, spatial, missingness, label-quality, and provenance acceptance criteria before acquiring or approving data.
3. Obtain adequate continuous weather observations and validate coverage within Kerala rather than relying on global-grid intersection.
4. Complete crop profiles, varieties, and district suitability associations using attributable evidence and explicit verification status.
5. Require the existing signed approval/provenance gate to pass before any training or inference workflow is enabled.

No datasets were downloaded, no external data-acquisition requests were made, no model was trained, and no live database data was modified for this stage.
