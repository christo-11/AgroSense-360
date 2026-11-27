# AgroSense-360 Data Governance Status

**Status date:** 2026-11-20  
**Decision scope:** Existing source approvals, ERA5-Land acquisition provenance, archive integrity, data quality, and training eligibility.

## Current source review

There are 13 registered data sources. Stage 17 changed no source permission, license, or commercial approval decision.

| Governance dimension | Current count / status |
| --- | --- |
| Commercially approved | 0 |
| Commercially conditional | 11 |
| Commercially blocked | 2 |
| Internal portfolio/research licence/terms classification | 3 |
| Portfolio conditional | 2 |
| Portfolio blocked | 1 |
| Portfolio unverified | 7 |
| Training-eligible sources | 0 |

Three sources—Open-Meteo historical data, Copernicus ERA5-Land, and NASA GPM IMERG—carry the internal `APPROVED_PORTFOLIO_RESEARCH_ONLY` inventory classification. It records an assessment that cited publisher licence/terms may appear compatible with a limited, non-commercial portfolio/research category. It is not source-owner permission, project-owner authorization, or effective permission to acquire data or conduct portfolio display, research, ML training, commercial use, redistribution, or deployment. Each project activity requires separate, valid, purpose-specific authorization and applicable source-owner rights. No source was promoted to commercial `APPROVED`.

## ERA5-Land governance decisions

| Decision layer | Status | What it means |
| --- | --- | --- |
| Internal portfolio licence/terms classification | `APPROVED_PORTFOLIO_RESEARCH_ONLY` | Internal assessment of apparent publisher-term compatibility only; not source-owner permission, project-owner authorization, or effective permission for project use. |
| Commercial permission | `CONDITIONAL` | The existing review has unresolved commercial/acquisition conditions. |
| Acquisition | `ACQUIRED_VERIFIED` | Two archive files exist and correspond to the recorded manifest requests. |
| Archive integrity | `VERIFIED` | Actual sizes match; SHA-256 evidence agrees across the files, manifest, and quality report; recorded ZIP CRC checks pass. |
| Data quality | `QUALITY_REJECTED` | The quality report classifies both archives as `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`. |
| Product version | `ACQUIRED_VERSION_UNPINNED` | No exact product version is recorded; `dataset_version` remains null. |
| Training eligibility | `INELIGIBLE` | The existing governance gate continues to reject this source. |

The `ACQUIRED_VERIFIED` row records the existence and integrity of historical archive files. It does not establish that their acquisition was authorized or grant permission for subsequent project activity.

The source inventory now records ERA5-Land as acquired and integrity verified, rather than `not_downloaded`. Its prior inventory state (checked 2026-11-19) and original request records are retained in the provenance audit trail. The two observed archive sizes total 2,673,387,578 bytes. A single source-level checksum remains null because each archive has a separate SHA-256 digest.

The original user-reported approximate sizes remain unchanged even though their request mapping is reversed relative to the measured file sizes. The exact request-history MHT was not inspected; exact variables, dates, and geographic bounds remain unconfirmed.

## Why training remains blocked

The acquisition and archive-integrity results do not authorize training. Eligibility remains zero because:

1. ERA5-Land's commercial approval is `CONDITIONAL`, not `APPROVED`.
2. Its product version is not pinned.
3. The dataset-specific review does not mark training quality and relevance as verified.
4. Both actual archive quality assessments reject the data for training due to sparse/irregular temporal coverage and unresolved quality concerns.
5. The existing signed-review and provenance gate must pass independently; this stage does not grant or create approval.

The dashboard reports availability and blockers only. It does not generate ML predictions or agricultural recommendations from these archives.

## Required evidence before training can be considered

- Inspect the retained CDS request-history MHT and verify exact request variables, dates, and geographic bounds.
- Record the exact ERA5-Land product/version and applicable license/terms acceptance evidence.
- Acquire adequate, continuous temporal coverage only after a separately approved acquisition decision; validate data quality and missingness within Kerala rather than treating global-grid statistics as local rates.
- Resolve the quality report's ancillary GRIB member-length concerns and document any exclusions.
- Provide task-relevant, provenance-backed agricultural labels and leakage-safe temporal/spatial/group splits.
- Obtain signed source approval and pass every check in `backend/scripts/dataset_governance.py` before training.

## Ongoing validation

The versioned read-only API reports source permission, acquisition, archive integrity, quality, training eligibility, and unresolved validation warnings separately. It checks archive existence and byte size within the project data boundary, validates checksum format and agreement between manifest and quality-report metadata, and does not return filesystem paths or archive URLs. It does not recompute archive hashes or apply migrations.

Backend tests and the read-only governance check pass. The test gate still rejects ERA5-Land as `CONDITIONAL`; training eligibility remains zero. No datasets were downloaded, no external acquisition calls were made, no model was trained, no database writes/migrations were made, and no credentials were accessed.

## Recommended next stage

**Stage 18 — Close remaining data-evidence gaps.** Verify the MHT request parameters, pin product/version and terms evidence, and set acceptance criteria for weather coverage and Kerala-specific quality. Continue sourcing verified crop profiles, varieties, and district suitability records. Do not start training until data quality and the signed governance gate are satisfied.
