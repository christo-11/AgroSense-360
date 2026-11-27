# AgroSense-360 Stage 32 — Dataset Quality Framework

**Status:** Framework design only. No dataset was evaluated, acquired, or modified in this stage. No quality result authorizes data use.

## 1. Purpose and governing rules

Define repeatable, automated checks for source files, normalized records, and versioned datasets before any research, feature generation, training, or serving gate.

- Quality is evaluated for a declared use, geography, period, variable set, and product version; no universal “good dataset” score replaces this context.
- Preserve raw values, source flags, and evidence. A failed parse/check must quarantine the affected artifact or partition, not silently coerce it.
- Missing is never zero. No automatic imputation, clipping, or interpolation in the ingestion-quality stage.
- Quality status is separate from rights, project-owner authorization, and training eligibility.
- Reuse the existing `PilotObservation`, `PilotSourceProvenance`, and `BlackPepperPilotDataset` contract where applicable; extend only through reviewed schema/version changes, not duplicate validations with inconsistent behavior.
- Existing ERA5-Land assessments remain unchanged: request 1 `ACCEPTABLE WITH LIMITATIONS`, request 2 `REJECTED`; neither is production-, decision-support-, or training-approved.

## 2. Quality result model

Every evaluation result should include:

| Field | Requirement |
|---|---|
| `dataset_id`, `dataset_version`, `raw_artifact_id` | Exact immutable release and raw inputs |
| `quality_run_id`, `check_suite_version`, `schema_version` | Reproducible evaluator identity |
| `intended_use`, `geography`, `time_window`, `variables` | Explicit evaluation scope |
| `started_at_utc`, `completed_at_utc`, `software_version` | Audit timestamps and implementation |
| `check_id`, `severity`, `status` | `PASS`, `WARN`, `FAIL`, or `NOT_ASSESSED` |
| `observed`, `expected`, `denominator`, `threshold` | Measurable evidence; no unsupported pass |
| `affected_partitions`, `evidence_refs`, `details` | Traceable failure/warning evidence |
| `quality_disposition` | `QUALITY_ACCEPTABLE_WITH_LIMITATIONS`, `QUALITY_INCOMPLETE`, `QUALITY_REJECTED`, or `NOT_ASSESSED` |

Unknown values, missing denominators, or unverified inputs produce `NOT_ASSESSED` or `QUALITY_INCOMPLETE`, not `PASS`.

## 3. Check catalogue

| Check family | Automated checks | Failure/warning behavior |
|---|---|---|
| **Completeness** | Compare expected and observed records by source/version/variable/time/spatial unit; compute coverage numerator, denominator, missing periods, and longest gap. Verify required columns and partitions exist. | Fail if required partitions/fields are absent. Warn or mark incomplete when coverage cannot be calculated. Thresholds are task-specific and approved before evaluation. |
| **Missing values** | Detect null, NaN, infinity, provider fill values/sentinels, sentinel collisions, and absent records. Preserve raw marker, mapped missing reason, and source QC flags. Report counts/fractions per variable, time, spatial partition and overall. | Fail non-finite numeric payloads; flag missingness beyond the approved threshold. Never fill missing rainfall, labels, or event extremes by zero. No Kerala-specific rate may be inferred from global-grid missingness. |
| **Duplicate records** | Test exact raw duplicates; canonical natural-key uniqueness; repeated timestamps/intervals and conflicting values; repeated source file/member identities. | Exact duplicates remain reported and may be removed only by a versioned rule. Conflicting duplicates are quarantined. No silent averaging or last-write-wins. |
| **Timestamp continuity** | Parse timezone-aware UTC instants/intervals; validate calendar/time encoding, monotonicity, uniqueness, expected cadence, interval ordering, start/end bounds, leap days, missing gaps, and forecast issue/valid/lead relationships. | Reject ambiguous or timezone-naive timestamps unless source semantics define them. Mark irregular periods explicitly; do not bridge gaps. Distinguish UTC day from Kerala local day and precipitation accumulation windows. |
| **Spatial coverage** | Validate CRS/axis order, coordinate bounds, grid regularity/resolution, station geometry, boundary version/checksum, coverage and valid-cell denominator by district. Compare native support to requested use scale. | Unknown CRS, boundary, or spatial reference blocks spatial acceptance. No plot-level claim from grid/district support. Emit `NO_STATION_COVERAGE` or `SPATIAL_VALIDATION_INCOMPLETE`; do not infer local quality from global extent. |
| **Unit consistency** | Validate source variable ID/name, canonical variable, unit, quantity type, scale/offset, accumulation/rate/statistic semantics, and approved conversion formula. Check converted values against source values and conversion version. | Reject unknown/contradictory units and guessed conversions. Keep original values/units. Unit mismatch is a hard failure for that field/partition. |
| **Outlier and physical checks** | Apply source-defined QC flags and approved physical bounds; detect negative precipitation, impossible relative humidity/pH, non-finite values, repeated constants, abrupt discontinuities, and robust distributional outliers (median/MAD) by variable/season/station or cell. | Hard-fail only documented physical/schema violations. Statistical outliers are flagged for scientific review, not automatically dropped or clipped. Thresholds require agronomic/meteorological approval; do not invent black-pepper-specific limits. |
| **Schema validation** | Validate required/optional fields, types, enumerations, units, nested structure, unique IDs, reference catalogs, provenance objects, and extra fields according to a pinned schema. Validate NetCDF/GRIB/CSV/Excel/GeoJSON/raster-specific structure before mapping. | Unknown schema or incompatible source version fails closed. Preserve unrecognized metadata; quarantine data records that cannot be mapped losslessly. |
| **Source integrity** | Verify original artifact SHA-256, byte size, transfer status, container CRC/member inventory, file signatures, parser readability, and internal message boundaries/format-specific checks. Compare request/response references with manifest. | Distinguish ZIP CRC from internal file/message conformance. Parser success does not override raw-format warnings. Any checksum mismatch or incomplete transfer blocks release. |
| **Dataset version verification** | Require exact publisher product/version/run/release, schema/process version, retrieval date, request parameters, terms snapshot and source lineage. Check that all partitions match the declared release. | Missing/unpinned version yields `NOT_ASSESSED` or blocked release; never substitute “latest” or mix versions silently. |
| **Provenance and permissions** | Validate non-empty publisher/product/version/licence/attribution, retrieval/request evidence, source checksum, and signed intended-use decision references. Compare record-level source version to dataset provenance. | Missing evidence blocks release. This check verifies evidence presence, not legal interpretation or authorization; no quality pass grants acquisition, research, commercial, redistribution, or training permission. |

## 4. Threshold policy

Thresholds must be declared per use before examining model outcomes. The existing [Kerala Weather Quality Specification](AGROSENSE_WEATHER_QUALITY_SPECIFICATION.md) contains **provisional project gates**, including daily completeness, gap, spatial-coverage, and validation examples. Its numbers are not universal scientific laws and must be approved by a meteorologist/agronomist and data owner for the task before they become release criteria.

Default behavior where no approved threshold exists:

- Record metrics and denominators.
- Mark the decision `NOT_ASSESSED`/`QUALITY_INCOMPLETE`.
- Do not pass the source by using a broad aggregate or silently ignoring missing data.

Thresholds must be versioned and include reviewer, rationale, variables, seasons, geography, and intended use.

## 5. Evaluation pipeline

1. **Authorization pre-check:** verify a documented, exact resource/version and purpose-specific project authorization; if absent, do not fetch or ingest.
2. **Artifact preflight:** compare expected request and manifest; verify complete transfer and SHA-256 before parsing.
3. **Container/parser checks:** validate archive contents and source format; retain parser diagnostics and raw member offsets/boundaries where applicable.
4. **Schema/provenance checks:** validate dataset-level metadata, source version, licence evidence, attribution, and schema.
5. **Record-level checks:** validate required fields, units, timestamps, coordinates, flags, natural keys, missing values and physical rules.
6. **Dataset-level checks:** compute completeness, time continuity, missingness, duplicate/conflict rates, grid/station coverage and version consistency by partition.
7. **Independent validation:** where required, compare with independent observations; record station/gauge independence, timing, elevation/distance, sample counts, bias/MAE and per-district results.
8. **Disposition:** publish a signed quality report with failed/warned checks, limitations, affected rows/files and next evidence needed. Data with blocking failures stay quarantined.

## 6. Status and release gates

Use separate statuses:

- **Quality:** `NOT_ASSESSED`, `QUALITY_INCOMPLETE`, `QUALITY_REJECTED`, `QUALITY_ACCEPTABLE_WITH_LIMITATIONS`, or `QUALITY_ACCEPTED_FOR_REVIEW`.
- **Authorization:** `NOT_AUTHORIZED`, `PENDING`, or the existing governance-system states backed by signed evidence.
- **Training eligibility:** remains a separate governance decision and must pass the existing `require_training_eligible` gate, including explicit ML permission, verified quality/relevance, and non-missing verified observations.

Only the designated reviewer process may change source inventory approvals. Automated quality checks must not update approval records or elevate training status.

## 7. Existing-contract alignment

The inspected black-pepper contract already enforces:

- Exact source version, licence and attribution fields, with unknown placeholders rejected.
- Timezone-aware UTC observations and intervals.
- Canonical variable units, explicit missing-value flags, and basic physical constraints.
- Soil depth and measured/estimated/derived provenance rules.
- Crop/district/source references, source-version match and natural-key duplicate rejection.
- Explicit training permission, quality status, training relevance and observation verification.

The contract does not by itself assess whole-dataset temporal coverage, independent station validation, gridded district coverage, file integrity, product-version pinning, or legal meaning of a licence. Those checks belong to this framework and must be linked to the same provenance record.

## 8. Required output artifacts per future evaluation

- Immutable raw-artifact manifest with checksums and source request/asset metadata.
- Machine-readable check results with `observed`, `expected`, `denominator`, thresholds and evidence references.
- Human-readable quality report with limitations and disposition.
- Quarantine manifest for rejected payloads/partitions, retaining original bytes.
- Reviewer sign-off and separate use/permission decision reference.
- Quality suite/schema/code version, reproducible environment reference, and report checksum.

## 9. Current project application

No new dataset was evaluated in Stage 32. The existing ERA5-Land findings remain: request 1 is acceptable with limitations as an intact but extremely sparse archive; request 2 is rejected pending resolution of the GRIB1 length discrepancy. Both remain unusable for production inputs, local agricultural decision support and training on current evidence. No approval or permission status changed.
