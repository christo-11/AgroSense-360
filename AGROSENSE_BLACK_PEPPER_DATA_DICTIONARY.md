# AgroSense-360 Black Pepper Pilot Data Dictionary

## Scope and implementation status

This is a normalized logical data contract for a future, evidence-backed portfolio/research pilot. It is not a report of available records. No black-pepper field observations or soil measurements were found in the repository, and no table, migration, API endpoint, or production record was created in Stage 19.

The companion `backend/scripts/black_pepper_pilot_contract.py` validates in-memory candidate records only. It is not connected to application routes, persistence, acquisition, or model training.

## Data principles

- Preserve original source values and units; store converted/normalized values separately with an explicit transformation.
- Keep measured, estimated, derived, and unverified values distinguishable in every view and export.
- Weather measurements or reanalysis estimates are not soil measurements.
- A value is unknown when it is absent. Do not encode unknown as zero or as a negative agronomic claim.
- Source permission, acquisition, quality, verification, and ML training authorization are separate fields/gates.
- A database row or catalogue label is not evidence that a crop is present or suitable at a location.

## Proposed normalized entities

| Entity | Purpose | Important relationships |
| --- | --- | --- |
| `Crop` | Stable catalogue identity: common name, scientific name, taxonomy reference, identity-verification status | Existing crop identity; a source-backed crop claim should record its evidence |
| `DistrictBoundaryVersion` | Versioned Kerala district boundary geometry, CRS, publisher, release, and checksum | District key plus boundary version; do not infer geometry from a district name |
| `PilotSite` | Station, farm, plot, or soil-sampling location with spatial identifier, coordinates/geometry, positional accuracy, and permission | References district-boundary version and source evidence |
| `SourceDatasetRelease` | Publisher, exact dataset/release, license/terms and attribution evidence, scope, acquisition/retrieval metadata, and independent permissions | Referenced by observations, claims, and derived features |
| `SeasonDefinition` | Named observation window and the source/rule used to define it | Linked to a crop/district study; season labels must not be inferred without a rule |
| `WeatherObservation` | Time-bounded weather station reading or gridded estimate | References source release, spatial support, variable, unit, quality, and temporal interval |
| `SoilObservation` | Soil lab measurement or modeled soil estimate | References source release, sample/site, analyte, depth, unit, method/model, and uncertainty |
| `AgronomicClaim` | Sourced crop/variety/district/practice or requirement claim | Field-level evidence links, status, reviewer, effective period, method, and uncertainty |
| `DerivedFeature` | A reproducible calculation from immutable input observations | Input observation IDs, formula/code version, output units, and time window |
| `UseApproval` | Permission for portfolio display, research training, or commercial use | Source release + purpose + reviewer/evidence; never inherited across purposes |

This proposal does not require immediate schema changes. The current model lacks field-level evidence, dataset-release provenance, soil sample depth/method, and versioned district geometries; add persistence only after the pilot scope and ingestion owner are approved.

## Common provenance and quality fields

| Field | Type / allowed values | Meaning and validation |
| --- | --- | --- |
| `source_id` | Non-empty stable identifier | Must reference one source registry entry |
| `dataset_name` | Non-empty text | Exact resource/dataset name, not merely a portal or publisher |
| `publisher` | Non-empty text | Data owner/publisher as recorded by the source |
| `dataset_version` | Non-empty pinned release/snapshot | Reject placeholder values such as “unknown” or “not pinned” for an observation release |
| `license_name` | Exact resource license/terms | Preserve license name and evidence/version; unknown terms block approval |
| `attribution` | Required citation/attribution text | Keep required credit and modifications notices |
| `portfolio_permission` | `APPROVED_PORTFOLIO_RESEARCH_ONLY`, `CONDITIONAL`, `BLOCKED`, `UNVERIFIED` | Portfolio display/research permission only |
| `commercial_use_status` | `APPROVED`, `CONDITIONAL`, `BLOCKED`, `UNVERIFIED` | Commercial rights are independent of portfolio permission |
| `ml_training_permission` | `APPROVED_RESEARCH_ONLY`, `APPROVED_COMMERCIAL`, `NOT_ASSESSED`, `BLOCKED` | Training purpose must be explicitly permitted |
| `data_quality_status` | `VERIFIED`, `NOT_ASSESSED`, `REJECTED` | Quality gate; not the same as source permission |
| `training_relevance_status` | `VERIFIED`, `NOT_ASSESSED`, `REJECTED` | Task, crop, geography, and target relevance gate |
| `quality_status` | `VERIFIED`, `FLAGGED`, `REJECTED`, `UNKNOWN` | Record-level quality outcome and flags |
| `verification_status` | `VERIFIED`, `PENDING`, `REJECTED` | Evidence review status, not a completeness percentage |
| `observation_kind` | `MEASURED`, `ESTIMATED`, `DERIVED`, `UNVERIFIED` | Required distinction between data origins |
| `missing_value` | Boolean plus nullable `value` | `true` requires null value; a numeric value cannot be marked missing |
| `observed_at` | Timezone-aware UTC datetime | Required timestamp; no timezone-naive or absent timestamps |
| `interval_end` | Optional timezone-aware UTC datetime | If present, must be later than `observed_at` |

Training requires an eligible source and non-missing, quality-verified observations. Soil target records specifically require measured, method-documented, depth-specific, quality-verified evidence. Estimated soil values may be stored as estimates/covariates after review, but must never be relabeled as lab measurements.

## Observation fields

| Field | Type / example shape | Validation |
| --- | --- | --- |
| `observation_id` | Stable unique ID | Required; never use crop/district name alone as an ID |
| `crop_ref` | Crop catalogue slug/ID | Must resolve to a crop identity; current black-pepper scientific name is not populated in the seed |
| `district_ref` | District ID | Must resolve to the selected, versioned district boundary when spatially aggregated |
| `spatial_reference_id` | Station/grid-cell/site ID | Must identify the support scale; do not present coarse-grid output as farm measurement |
| `season` | Nullable season code | Populate only from an approved documented season definition |
| `variable` | Controlled field name | Examples: `air_temperature`, `precipitation`, `relative_humidity`, `soil_ph`, `soil_nitrogen`, `soil_phosphorus`, `soil_potassium`, `soil_organic_carbon` |
| `value` | Nullable numeric value | Must be finite; unit and missing flag must agree |
| `unit` | Canonical unit | Enforce by variable; retain original/source unit separately |
| `source_unit` | Original unit string | Required for non-identity conversion; never infer unit from a numeric range |
| `conversion_method` | Nullable transform reference | Formula, code version, and input unit for any conversion |
| `collection_method` | Nullable text | Required for `MEASURED` values; includes instrument/lab/analysis method where applicable |
| `estimator_name`, `estimator_version` | Nullable text | Required for `ESTIMATED` values, e.g. a pinned reanalysis/model product |
| `derivation_method` | Nullable formula/code version | Required for `DERIVED` values; keep input record references |
| `measurement_depth_top_cm`, `measurement_depth_bottom_cm` | Nullable numeric depth interval | Required for soil observations; bottom must be greater than top |
| `use_role` | `FEATURE`, `TARGET`, `CONTEXT` | Soil target cannot be modeled SoilGrids/weather estimate; require measured verified evidence |
| `quality_flags` | Structured list/map | Preserve provider and local QA flags; do not silently delete flagged values |
| `uncertainty` | Nullable numeric/structured metric | Preserve only where supplied/defined; identify its meaning and units |
| `source_record_id` | Source-specific row/message/sample ID | Required for traceability to retained source evidence |

## Canonical units for the validation contract

The following are normalized storage units for the pilot contract, not claims that the current files contain all variables:

| Variable | Canonical unit | Additional requirement |
| --- | --- | --- |
| Air temperature | `degC` | Preserve source unit (ERA5-Land temperature is reported in `K`) and explicit conversion |
| Precipitation | `mm` | Preserve source unit and accumulation interval (ERA5-Land `tp` is reported in `m`) |
| Relative humidity | `%` | Retain source flags and aggregation method |
| Soil pH | `1` (dimensionless) | Record water/extraction method and depth |
| Soil nitrogen | `mg/kg` | Record measured fraction, lab method, and depth |
| Soil phosphorus | `mg/kg` | Record available/total fraction, extraction method, and depth |
| Soil potassium | `mg/kg` | Record available/total fraction, extraction method, and depth |
| Soil organic carbon | `g/kg` | Record analytical method and depth; do not substitute a modeled map as measured label |

Do not assume that equal units make soil results comparable: the analyte fraction, extraction/analysis method, depth, date, and laboratory must also be retained. SoilGrids documentation in the repository does not list phosphorus or potassium layers.

## Uniqueness and completeness rules

- Observation natural key: `(source_id, source_version, crop_ref, district_ref, spatial_reference_id, variable, observed_at, interval_end, measurement_depth_top_cm, measurement_depth_bottom_cm)`. Duplicate keys are rejected or quarantined; conflicting values must not be averaged silently.
- Source IDs must be unique within a dataset manifest; every observation source and version must resolve.
- Crop and district references must resolve against the selected catalogue/boundary version.
- Timestamps are explicit UTC and missing timestamps are rejected. A missing value is represented by null plus a `missing_value` indicator and reason/quality flag.
- Soil observations require a valid depth interval. A measured soil record requires a documented method and verification; an estimated soil value requires estimator identity/version and remains `ESTIMATED`.
- An observation marked `DERIVED` must identify its formula/code version and inputs; it is not raw measurement.
- No complete/verified dataset is inferred from populated row counts.

## Current records

No black-pepper weather/soil observation rows, soil samples, site coordinates, seasons, or derived features were created in Stage 19. The only test records are ephemeral, explicitly `test-*` validation fixtures with null/missing values; they are not stored or exposed as agricultural data.
