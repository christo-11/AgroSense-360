# AgroSense-360 Stage 31 — Weather Data Architecture

**Status:** Design only; implementation requires separate approval.  
**Scope:** Future weather ingestion and serving for Kerala agriculture; no source is approved or acquired by this design.

## 1. Design principles

- Enforce project-owner authorization, exact source terms and the intended-use decision before ingestion or external API calls.
- Keep original source payloads immutable and separate from normalized observations, features, forecasts and user-facing responses.
- Preserve whether a value is a station measurement, reanalysis estimate, satellite retrieval, blended product, forecast, or derived feature.
- Keep historical reanalysis/observation data distinct from forecasts. Never use later observations or revisions as a historical forecast feature.
- Fail closed on unknown source versions, missing permissions, invalid metadata, incomplete requests or quality failures. Do not silently substitute another provider.
- Do not infer plot-level precision from a grid cell or district-level value.

The existing Stage 22 pipeline, weather quality specification, acquisition plan, and Stage 28 archive assessment remain applicable. In particular, the existing ERA5-Land archive dispositions are not changed by this architecture.

## 2. Logical architecture

```text
Project-owner authorization + source licence/use gate
    -> source registry + approved product/request definition
    -> provider-specific adapter / authorized API client
    -> immutable raw landing + request/response evidence
    -> format parser and source schema validator
    -> canonical observation/forecast model
    -> unit, time, spatial, missingness and integrity checks
    -> quarantine or versioned normalized dataset
    -> versioned feature computation (separate approval)
    -> authorized persistence / read API
    -> UI or downstream service with provenance and quality status
```

Quality and permission failures must stop the pipeline before normalized values are exposed as usable inputs. Every transition emits an auditable status and references the source release, code/config version, raw checksum, and decision evidence.

## 3. Source adapters and API ingestion

Each adapter implements a provider-neutral interface while retaining provider-specific semantics:

```text
describe_source()
validate_request(request_spec)
fetch_authorized(request_spec, cursor)
verify_response(response_metadata, payload)
parse(payload, schema_version)
map_to_canonical(parsed_record)
```

`fetch_authorized` is unavailable unless the project-owner/source permission gate is satisfied. Adapters must not embed tokens, keys, or credentials. Credentials, if later approved, belong in an external secret manager or protected runtime configuration and must never be logged.

Candidate adapter families:

- **Copernicus CDS:** explicit dataset/process ID, process schema version, request JSON, task ID, status transitions, archive/member checks and returned product version. Existing request 2 GRIB1 ambiguity requires a blocking source-quality flag for affected members.
- **IMD:** separate adapters per exact gridded product, station export, or operational forecast; do not treat portal pages or unrelated product terms as a data feed.
- **NASA POWER:** preserve parameter ID, source-provider lineage, spatial support, time standard, and point/regional request semantics.
- **NASA GPM IMERG:** preserve product/run/version, half-hourly or derived temporal product, scale/offset, rate versus accumulation, and archive/distributor.
- **CHIRPS:** preserve v3 product form, preliminary/final status, daily `rnl`/`sat` type or native pentad period, source components, and daily date-label semantics.

Adapters must not contact a source until the exact request and applicable permission record have been approved. API documentation access is not data-access authorization.

## 4. Historical data handling

- Use an immutable historical request specification containing source ID, exact product/version, variables, period, geographic extent, temporal support, output format and terms snapshot.
- Store the canonical request body and its fingerprint before submission. Record the provider task/reference ID and every state transition.
- Use bounded time/geography chunks, resumable cursors, idempotency keys and explicit rate limiting. A retry of the same request must not create duplicate canonical rows.
- Preserve the provider's original payload and metadata byte-for-byte; compute SHA-256 before parsing.
- Do not concatenate files from different product versions or processing baselines without an explicit harmonization plan.
- Record revisions and reprocessing as new dataset versions. Never silently replace a historical release.

## 5. Forecast data handling

Forecasts are stored as forecasts, never as observations:

- Required time keys: `issued_at`/forecast reference time, `valid_start`, `valid_end`, `lead_duration`, and provider cycle/run ID.
- Keep all forecast cycles and their source version; a selected forecast for a target must use only a cycle available before the prediction cutoff.
- Prevent leakage by prohibiting actual observations, reanalysis values, later forecast revisions, or features calculated after `issued_at` from entering historical forecast evaluation.
- Retain ensemble member/statistic and probability semantics. Do not treat deterministic and ensemble summaries as equivalent.
- Store each forecast response independently with retrieval time, source status, latency and expiration.
- On stale, missing, invalid or unavailable forecasts, return explicit `UNAVAILABLE`/`STALE` status; never silently fall back to reanalysis or another vendor.

No operational forecast feed has been approved or selected for AgroSense-360.

## 6. Canonical weather record

Minimum conceptual record fields:

| Group | Fields |
|---|---|
| Identity | `source_id`, `dataset_version`, `record_id`, stable `variable_id`, `schema_version` |
| Provenance | `raw_artifact_id`, `raw_sha256`, `source_product`, source URL, request/asset ID, retrieval timestamp, parser/mapping version |
| Value | raw value, raw unit, normalized value/unit, conversion identifier, quality flags |
| Time | `valid_start_utc`, `valid_end_utc`, source time convention, accumulation/statistic semantics |
| Spatial | support type (`station`, `grid_cell`, `area`), spatial reference ID, coordinates/geometry reference, CRS, native resolution, boundary version |
| Evidence | `evidence_type`, `measured/estimated/forecast/derived` provenance, missingness state, validation state |
| Governance | licence/terms snapshot ID, attribution text, approved purpose/status, reviewer decision reference |

Use typed records and schema validation before persistence. Raw fields remain available for audit; normalized values never overwrite source values.

## 7. Unit normalization

- Use a versioned variable catalogue containing definitions, canonical unit, allowed source units, conversion formula, temporal semantics, and physical QA rules.
- Convert only when the source unit and parameter meaning are verified. Preserve original unit/value and conversion code/version.
- Example conversions such as Kelvin-to-Celsius or metres-to-millimetres must be explicit, tested and attached to the record.
- Distinguish precipitation amount from rate; document forecast accumulation window, reset/cycle semantics and daily boundary before aggregation.
- Relative humidity should be used only when directly supplied with verified semantics or derived from suitable temperature/dewpoint using an approved method and documented assumptions.
- Reject unknown units, unknown parameter IDs, contradictory metadata, or unapproved conversions; quarantine rather than infer from numeric range.

## 8. Timestamp and timezone handling

- Store timestamps as timezone-aware UTC instants and intervals. Reject ambiguous local times or timezone-naive values unless the source specification defines them unambiguously.
- Preserve original time labels, time zone and calendar encoding (including CF time units/calendar) alongside normalized UTC values.
- Record interval start/end and whether an observation is instantaneous, averaged, accumulated, or a forecast valid interval.
- Derive Kerala-local reporting days with `Asia/Kolkata` only after retaining source UTC timestamps. A UTC daily total is not an IST-day total.
- Validate monotonicity, uniqueness, expected cadence, leap days, calendar boundaries and forecast issuance/lead times.
- Reject records whose date fields conflict with encoded time coordinates or product metadata.

## 9. Missing values and quality flags

- Map provider fill/sentinel codes, NaN and absent records to an explicit missing state with reason/source flag; preserve original code in raw provenance.
- Never convert missing precipitation or a missing target to zero. Do not impute in ingestion.
- Report expected versus observed values, missing fraction, longest gap and completeness by variable, source version, time period, grid cell/station, and district.
- Keep source QC flags and add project QA flags separately.
- Quarantine malformed or invalid records without discarding the original artifact. Do not report a partially parsed payload as a complete successful ingest.
- Any later imputation or aggregation belongs in a separately versioned feature step and must retain an imputation mask.

## 10. Spatial mapping

- Preserve native grid coordinates, CRS, resolution, geometry and support type.
- Validate coordinate axis order, longitude convention, coordinate bounds, cell spacing, CRS and spatial extent. Do not assume a CRS when absent.
- Use only a versioned, authorized district boundary source for Kerala/Idukki overlays. Keep boundary checksum and release in the spatial mapping.
- Link a grid estimate to the native cell (and its area/support); do not label it as a farm measurement.
- Assign station locations to districts only after validating coordinates and boundary version; preserve station elevation and metadata.
- For district aggregates, document cell-area weighting, coast/ocean masking, minimum coverage rule and missing-cell denominator. An incomplete overlay returns `SPATIAL_VALIDATION_INCOMPLETE`.
- Idukki remains provisional until authoritative crop/district evidence is established.

## 11. Provenance, versioning and immutable storage

Use separate version identifiers for source product, raw acquisition, parser/schema, normalization mapping, boundary set, feature definition and quality report. A processed version must point back to all inputs and configuration versions.

For each raw artifact, record source owner, product/version, licence and terms version, attribution, intended purpose, authorization evidence, request/asset ID, full parameters, retrieval time, file/member list, size, SHA-256, parser build and quality result. Keep raw artifacts in access-controlled storage outside Git. Store only approved metadata or protected object references in application storage.

On checksum mismatch, duplicate request conflict, version ambiguity, license change, retraction, or provider correction, quarantine the artifact and retain the prior record. Do not mutate historical lineage.

## 12. Quality checks and release states

Apply the Stage 32 quality framework when approved. Minimum pre-release checks include:

- Source/version and terms identity; request/asset completeness.
- Container integrity and payload parsing.
- Schema/variable/unit compatibility.
- Time range, cadence, duplicate, interval and accumulation validation.
- Missingness, provider flags and physical range anomalies.
- Spatial grid/station/boundary coverage and coordinate validation.
- Checksum and provenance lineage.
- Source-specific local validation for the intended geography and use.

Suggested states (not approvals): `RECEIVED`, `INTEGRITY_FAILED`, `PARSE_FAILED`, `QUARANTINED`, `QUALITY_INCOMPLETE`, `QUALITY_REJECTED`, `QUALITY_ACCEPTABLE_WITH_LIMITATIONS`, `QUALITY_ACCEPTED_FOR_REVIEW`, and `RELEASE_BLOCKED_BY_PERMISSION`. Quality acceptance never overrides a legal or project-owner gate.

## 13. Error handling, retries and audit logs

- Classify errors: authorization, authentication, rate limit, transient transport, provider job failure, malformed response, checksum mismatch, schema/version mismatch, temporal/spatial invalidity, parser defect, and storage failure.
- Retry only transient/rate-limited errors using bounded exponential backoff and provider `Retry-After` guidance. Do not retry authorization, licence, schema, or content-integrity failures automatically.
- Use idempotent request IDs; store attempt number, timestamps, status, response code, provider job ID, checksum and error category. Avoid logging payloads, secrets, personal identifiers, or sensitive farm coordinates.
- Emit structured audit events for request approval, submission, response, file landing, validation, quarantine, version release, access, transformation and permission changes.
- Monitoring alerts must identify stale sources, failed chunks, missing periods, unusual size shifts and repeated parser failures without exposing credentials.
- Surface failures to operators and dependent APIs. Return explicit `UNAVAILABLE`, `STALE`, `QUALITY_REJECTED`, or `PERMISSION_BLOCKED`; never success-shaped empty data.

## 14. Serving boundary and implementation gate

The current FastAPI application exposes general farm/plot and status routes; `/api/v1/insights/weather` currently returns `503` until verified data/model services are deployed. This design does not change application behavior or introduce a weather endpoint.

Before implementation, obtain separate approval for:

1. Exact source/product and permitted purpose.
2. Acquisition method and credentials handling, if needed.
3. Canonical schema, database ownership/retention and migration plan.
4. Boundary/version source, temporal semantics, unit catalogue and quality thresholds.
5. API contract and security review.
6. Tests, monitoring, operator ownership and rollback procedure.

**No ingestion, external API use, database write, migration, source approval, or model training is authorized by this architecture.**
