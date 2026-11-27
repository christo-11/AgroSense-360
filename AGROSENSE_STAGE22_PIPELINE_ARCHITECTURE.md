# AgroSense-360 Stage 22 Pipeline Architecture

**Implementation status:** Architecture only  
**Restriction:** No code, download, database write or migration is required or authorized in Stage 22

## Architecture goals

The future acquisition pipeline must preserve source authority, provenance, units, timestamps, spatial support and evidence type. It must fail closed on missing permission or provenance and must never turn missing data or estimates into measured observations.

## Logical flow

```text
Permission and acquisition decision
  -> immutable raw landing zone
  -> format-specific parser
  -> source schema mapping
  -> Pydantic and record-level validation
  -> missing/duplicate/quality/quarantine layer
  -> canonical observation or claim model
  -> provenance and version manifest
  -> geographic/time/unit validation
  -> quality report
  -> governance/training gate
  -> optional future processed layer
```

No database or ML step may occur before a signed source permission and provenance gate.

## Source formats

### CSV ingestion

Future responsibilities:

- Detect delimiter and encoding.
- Require an explicit schema manifest.
- Preserve original column names and values.
- Validate required natural-key fields.
- Reject timezone-naive or unparseable timestamps.
- Normalize line endings and duplicate headers.
- Quarantine malformed or conflicting rows.

### Excel ingestion

Future responsibilities:

- Read only explicitly named sheets and cell ranges.
- Preserve sheet name, workbook revision and file checksum.
- Reject merged-header ambiguity and hidden-formula assumptions.
- Retain original cell values and units.
- Convert only through an approved workbook mapping.
- Quarantine formula-calculated fields that lack source provenance.

### GeoJSON ingestion

Future responsibilities:

- Validate GeoJSON object type and CRS.
- Preserve source geometry and geometry collection structure.
- Require a boundary or site source and version.
- Reject unknown CRS or silently assumed CRS.
- Clip or join only against a versioned Kerala/Idukki boundary.
- Retain positional accuracy and spatial support.

### NetCDF weather ingestion

Future responsibilities:

- Read CF metadata and variable IDs.
- Retain product, source unit and coordinate convention.
- Parse time units and UTC intervals.
- Preserve fill values as missing plus quality flags.
- Validate dimensions and duplicate timestamps.
- Reject precipitation accumulation/reset ambiguity.
- Store grid-cell IDs, native resolution and CRS.

### Raster soil ingestion

Future responsibilities:

- Verify CRS, raster resolution, depth, band semantics and nodata.
- Preserve source model and snapshot.
- Distinguish modeled estimate from measured soil observation.
- Preserve raster footprint and uncertainty when supplied.
- Prohibit point interpolation that claims plot-level measurement.
- Require spatial masking and versioned boundary support.

## Canonical processing stages

### 1. Permission gate

Before ingestion:

- Resource and licence are exact.
- Acquisition purpose is approved.
- Portfolio/research/commercial/training scope is explicit.
- Redistribution requirements are retained.
- Source record exists in the inventory.

### 2. Immutable raw landing

- One release per file or export.
- Write-protected immutable raw artifacts.
- SHA-256 checksum.
- Retrieval or API request parameters.
- Source URL and terms snapshot.
- Dataset/product version.
- No silent overwriting.

### 3. Format parsing

- Format-specific parser emits typed records.
- Original fields are retained.
- No source value is silently dropped.
- Parse errors go to quarantine.

### 4. Mapping and normalization

- Source variable to canonical variable.
- Source unit to canonical unit.
- Timestamp to timezone-aware UTC.
- Native spatial support to stable spatial ID.
- Crop/district references to catalogue/boundary versions.
- Measured/estimated/derived/unverified type.

### 5. Pydantic validation

The existing `PilotObservation` contract should remain a shared gate for:

- UTC timestamps.
- Canonical units.
- Missing-value agreement.
- Soil depth requirements.
- Measured/estimated/derived provenance.
- Duplicate natural-key rejection.
- Soil target evidence eligibility.

Future pipeline integration should reuse this contract or an extracted shared package, not duplicate rules.

### 6. Missing-value detection

For every variable:

- Expected record count.
- Observed record count.
- Null count.
- Provider missing code count.
- Local quarantine count.
- Longest gap.
- Coverage by district/site/season/version.

Missing must remain null plus flags. Missing precipitation or targets must not be zero-filled or imputed by default.

### 7. Geographic validation

- Require a versioned district boundary.
- Preserve CRS and native spatial support.
- Validate point-in-district using that boundary.
- Calculate gridded native-cell coverage.
- Mark `NO_STATION_COVERAGE` or `VALIDATION_INCOMPLETE` rather than extrapolating.
- Reject farm/plot claims from district- or grid-level support.

### 8. Timestamp validation

- Require explicit timezone or source timezone definition.
- Preserve interval start and end.
- Convert reporting to UTC before canonical storage.
- Derive Kerala local dates using `Asia/Kolkata` only for reporting.
- Detect duplicates, monotonicity failures and irregular cadence.
- Reject ambiguous precipitation accumulation reset semantics.

### 9. Unit normalization

- Normalize through a formula and code-version manifest.
- Preserve source unit and original value.
- Reject guessed conversions.
- Apply variable-specific canonical units from the Stage 19 dictionary.
- Retain unit and analyte fraction as separate provenance.

### 10. Provenance tracking

The provenance record should include:

- Dataset ID and exact version.
- Publisher and source URL.
- Retrieval method/date.
- Licence and attribution snapshot.
- SHA-256 checksum.
- Raw and processed data references.
- Parser/code version.
- Mapping and unit conversion formulas.
- Reviewer and decision.

### 11. Duplicate detection

Default natural key:

```text
(source_id, product_version, crop_ref, district_ref,
 spatial_reference_id, variable, observed_at, interval_end,
 measurement_depth_top_cm, measurement_depth_bottom_cm)
```

Exact duplicates are reported and deduplicated only by a documented rule. Conflicting duplicates are quarantined.

### 12. Quarantine and quality reports

Quarantine:

- Unknown source or licence.
- Invalid timestamps or units.
- Missing spatial reference.
- Unknown crop/district.
- Conflicting duplicates.
- Invalid measured soil target.
- Rejected provider flags.
- Training-ineligible observations.

Reports must retain counts and file/row identifiers.

## Dataset versioning

Every release receives:

- Dataset ID.
- Source release ID.
- Schema version.
- Ingestion code/version.
- Immutable raw manifest.
- Canonical mapping version.
- Quality report.
- Permission decision.
- Processing status.

Versioning must not overwrite prior results.

## Governance and ML gate

Before training:

- Source is `APPROVED` in the signed governance inventory.
- Commercial/research training purpose is explicit.
- Raw file and provenance checksum match.
- Quality and relevance are verified.
- Labels are measured or scientifically approved and leakage-safe.
- Temporal, spatial and crop splits are documented.
- Existing data-governance `require_training_dataset` gate passes.

The architecture does not create training eligibility.
