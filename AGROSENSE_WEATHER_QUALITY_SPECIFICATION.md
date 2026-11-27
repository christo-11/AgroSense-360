# AgroSense-360 Kerala Weather Data Quality Specification

## Purpose and current status

This is a proposed, measurable acceptance specification for future Kerala weather datasets. Its thresholds are project engineering gates, not established agricultural facts or a claim that any current dataset passes. A meteorologist/agronomist and data owner should approve the thresholds for the intended crop, variable, and decision horizon before operational use.

The two existing ERA5-Land archive quality records remain `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`. They contain only two valid main timestamps in one archive and 12 irregular timestamps in the other, and the existing assessment reports missing-data concerns. Their global-grid missingness figures are not Kerala-specific. Neither archive meets this specification or supports prediction, training, or recommendation.

## Acceptance status vocabulary

Keep the following statuses separate:

1. `METADATA_VALIDATED`: source, product/version, variables, units, timestamps, CRS/grid, license, attribution, and retrieval provenance are complete.
2. `TEMPORAL_COVERAGE_ACCEPTED`: the target period meets the completeness and gap limits below.
3. `KERALA_SPATIAL_COVERAGE_ACCEPTED`: all 14 districts are spatially represented at a declared native resolution without silent extrapolation.
4. `INDEPENDENTLY_VALIDATED`: comparison against independent, quality-controlled observations meets the provisional metrics below.
5. `TRAINING_ELIGIBLE`: all preceding gates pass, labels and intended use are approved, and dataset-governance approval is recorded. None of the preceding statuses alone grants training permission.

If evidence is absent, use `UNKNOWN`, `NOT_ASSESSED`, or `BLOCKED`; do not convert it to a pass or fill missing data with zero.

## Required data and provenance contract

Every ingested observation or grid value must retain:

- Stable source ID, publisher, product/dataset title, exact version/release and retrieval date.
- Original variable name, standardized variable name, original units, converted units, conversion formula, and provider quality flags.
- UTC timestamp with explicit interval/accumulation semantics; local season labels must retain the rule used to derive them.
- Station ID and station metadata, or grid cell identifier, native resolution, CRS, coordinates, and relevant boundary version.
- Original value, missingness state, transformation/imputation flag, and provenance back to immutable raw data.
- License/terms snapshot, attribution text, intended-use review, and checksum for retained files where available.

Do not silently merge different model versions, forecast/reanalysis products, station networks, temporal supports, or measurement methods.

## Measurable acceptance criteria

The numeric thresholds below are initial project gates. Record the observed metric and denominator for every check. A missing metric is a failed/incomplete gate, not a pass.

### 1. Temporal coverage and gaps

- Declare the target question, crop/season window, temporal resolution, and forecast cutoff before inspecting model results.
- For a daily weather-feature dataset intended for model research: require at least **10 consecutive complete crop-years** for each target crop-season. Each crop-year and required variable must have at least **98% of expected daily observations**.
- No target crop-season may contain a gap longer than **3 consecutive days** in a required variable. If this fails, mark that season/year unavailable rather than bridging the gap.
- For a climatological-normal comparison, require at least **30 complete years** with at least **98% monthly coverage** for each required variable. This is a separate use case from crop-season prediction.
- For hourly source data aggregated to daily values, document the aggregation and require at least **22 valid hourly values per daily value** for temperature/humidity and the correct provider-defined accumulation window for precipitation. Do not mix instantaneous rates and accumulations.
- Do not extrapolate or silently fill the start/end of a series. Report expected records, observed records, completeness, longest gap, and excluded periods per variable, district, and season.

### 2. Kerala spatial coverage

- Use a versioned Kerala district boundary source and retain its publisher, release, CRS, and checksum. The current district table contains names only; it is not a spatial boundary dataset.
- A gridded product must intersect every one of the 14 districts. For each district and target date/variable, valid native cells must cover at least **90% of the district's land area**; document coastal masking and the area-weighting method.
- Do not interpret a coarse grid cell as a farm measurement or create plot-level resolution by interpolation. Report the native pixel size, effective support, and district aggregation method.
- A station product must document station coordinates, elevation, ownership/source, instrument or quality-control metadata, operating dates, relocation history where known, and district assignment under the pinned boundary version. At minimum, every district in the intended evaluation must have one valid station or an explicit `NO_STATION_COVERAGE` limitation.
- A claim at farm/plot scale requires farm-scale validation; district coverage alone is insufficient.

### 3. Missing values and aggregation

- Preserve raw missing values as null plus a reason/quality flag. Missing is never zero.
- Do not impute precipitation, extreme events, or missing target labels. For a derived temperature covariate only, an approved method may interpolate at most **2 consecutive missing daily values**; retain the raw gap, imputed value, method, and flag. Interpolated values do not count as observed coverage.
- Compute coverage before and after any transformation. Do not let aggregation hide gaps or duplicate records.
- A daily precipitation total must use the source's declared accumulation period, including reset/forecast-step semantics. A daily temperature mean must use a documented local-day or UTC-day boundary consistently.

### 4. Variables, units, timestamps, and duplicates

- Require variable metadata, standard name/definition, units, valid range/source flags, and aggregation semantics. Preserve the source representation before conversion.
- Convert units only through explicit, tested transformations. Examples such as Kelvin-to-Celsius or metres-to-millimetres must be driven by product metadata, not guessed from value ranges.
- Store timestamps as timezone-aware UTC. Derive Kerala-local dates using `Asia/Kolkata` only for reporting/season assignment and preserve the UTC source timestamp. Reject unparseable or timezone-naive timestamps unless source documentation defines them unambiguously.
- Enforce uniqueness on `(source_id, product_version, variable, spatial_id, interval_start, interval_end)` after canonicalization. Exact duplicates are reported and handled by a documented rule; conflicting duplicates are quarantined, not averaged silently.
- Check monotonicity and expected cadence within each station/grid-cell-variable series. Report all missing, duplicate, and irregular intervals.

### 5. Outliers and physical checks

- Apply documented product-specific hard bounds and quality flags. For precipitation, negative values are invalid. Do not create Kerala-specific temperature limits without an approved scientific source.
- Flag, do not automatically discard, observations more than **6 robust standard deviations** from a local calendar-month distribution (median/MAD), unless a source-defined quality flag marks them invalid. Retain the flagged value and investigation result.
- Check discontinuities, repeated constant values, impossible unit conversions, precipitation accumulation resets, and station relocation effects. Keep event extremes for review instead of winsorizing them away.
- Publish outlier counts and decisions by variable, station/grid cell, season, and source version.

### 6. Independent validation

Use independent, quality-controlled station observations or gauges not used to create the gridded/reanalysis product. Record observation authority, calibration/quality procedures, time alignment, distance/elevation mismatch, and missingness.

Provisional minimum evaluation design:

- Hold out at least **20% of stations** from any calibration/tuning, with at least one held-out station in every district where independent observations exist.
- Accumulate at least **365 paired daily observations over at least 2 years per evaluated district**. If that cannot be met, report the district as `VALIDATION_INCOMPLETE`; do not imply statewide validation.
- For daily temperature, target absolute mean bias no greater than **1.0 °C** and MAE no greater than **2.0 °C** per evaluated district.
- For precipitation, evaluate daily occurrence and amount separately. Target absolute monthly-total bias no greater than **15%** per evaluated district and publish wet-day detection metrics; define the wet-day threshold from the gauge/product conventions before comparison.
- Publish per-district metrics, sample counts, confidence intervals, and seasonal breakdowns. Do not allow good statewide averages to conceal a failing district.

These are provisional release gates, not claims about expected product performance. The responsible scientific reviewer must approve variable-specific thresholds and the wet-day definition before validation begins. If independent observations are unavailable, the dataset remains `INDEPENDENTLY_VALIDATED = false`.

## Release decision

A weather dataset can be used as a research feature only when metadata, rights, spatial/temporal coverage, and missingness are reviewed for its intended task. Training additionally requires independent validation, a versioned immutable snapshot, label/feature leakage review, and documented approval. Acquisition or file integrity does not imply weather quality; weather quality does not imply license permission; either does not imply training eligibility.

## Current ERA5-Land decision

| Dimension | Current evidence | Decision |
| --- | --- | --- |
| Acquisition | Two archive requests are in the existing manifest and were reconciled in Stage 17 | Acquired evidence does not establish suitability |
| Temporal coverage | One archive has 2 valid main timestamps; the other 12 irregular timestamps | Fails the minimum consecutive crop-year requirement |
| Missingness | Existing quality reports identify substantial missing values and unresolved concerns | Fails completeness gate; global figures are not Kerala-specific |
| Kerala spatial coverage | The quality report did not calculate valid-area coverage against a Kerala district boundary version | Not assessed |
| Independent validation | No independent Kerala station/gauge comparison is documented | Not assessed |
| Product/request provenance | Exact CDS request parameters and pinned product version remain unresolved | Metadata gate incomplete |
| Training | Both archives are marked `REJECT_FOR_TRAINING` | Not eligible |

No additional weather data was acquired, no external API was called, and no model was trained for this specification.
