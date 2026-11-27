# AgroSense-360 Stage 33 — Agricultural Feature Engineering

**Status:** Feature design only. No source data was acquired, transformed, or used for training.  
**Pilot:** Black pepper in Kerala; Idukki remains provisional.

## 1. Evidence and design boundary

The Stage 19/21 records do not establish an Idukki black-pepper season, phenology calendar, site, variety, yield target, or measured soil/weather observations. No crop-specific threshold or stage date is assigned here. Feature formulas below are candidate engineering definitions, not verified black-pepper requirements or agronomic findings.

Available candidate inputs include IMD weather, ERA5/ERA5-Land reanalysis, NASA POWER, GPM IMERG, and CHIRPS. Their evidence types and limitations are distinct: station measurements, gridded observations, reanalysis estimates, satellite retrievals, blended products, and forecast values must not be conflated. The Stage 28 dispositions for the existing ERA5-Land archives remain unchanged. No source is authorized for research, pilot, commercial, redistribution, or ML use by this design.

## 2. Temporal and spatial contract

Before any feature is computed, declare:

- Source product/version, variable definitions, units and QC flags.
- Spatial support (station, native grid cell, district aggregate, plot measurement) and boundary version.
- Timezone and interval semantics. Store source intervals in UTC; use `Asia/Kolkata` for a separately defined local-day/crop-window view.
- Feature window, required coverage, missing-data policy and intended prediction cutoff.
- Whether values are measured, estimated, forecast, or derived.

For rainfall and other accumulated quantities, preserve source accumulation periods and reset semantics before aggregation. Do not mix instantaneous rates with totals. A grid value remains a grid estimate; it is not a farm observation.

## 3. Candidate feature definitions

Let \(P_t\) be nonnegative rainfall total for the approved day/window \(t\), and \(T_t\), \(T^{min}_t\), \(T^{max}_t\) be quality-checked temperature summaries for the same defined time basis. Any required threshold is a parameter requiring a documented scientific source and reviewer approval.

| Feature | Candidate definition | Output unit | Required inputs / source | Limits and safeguards |
|---|---|---|---|---|
| Rain accumulation, window \(k\) | \(R_k(t)=\sum_{i=0}^{k-1} P_{t-i}\), with \(k\) explicitly versioned (candidate windows: 3, 7, 30 days). | mm per window | IMD gauge/grid, IMERG, CHIRPS, ERA5/ERA5-Land or POWER precipitation; preserve product type and accumulation interval. | Candidate windows are not crop-stage facts. Require complete valid periods; missing days stay missing, not zero. Avoid double-summing forecast accumulations. |
| Rainfall intensity summary | For complete window, total \(R_k\), valid wet-day count \(N_w\), and \(R_k/N_w\) when \(N_w>0\). | mm; days; mm/wet day | Same rainfall source, with an approved wet-day threshold \(r_w\). | Do not assume a universal wet-day cutoff. Publish denominator and missingness; undefined when no valid wet days. |
| Dry spell length | Consecutive valid days with \(P_t < r_{dry}\); report current and longest run in a declared window. | days | Daily precipitation on a consistent day boundary. | \(r_{dry}\) must be selected by an agronomic/meteorological reviewer; missing days break/unknown the run and must not extend or terminate it as if measured. |
| Wet spell length | Consecutive valid days with \(P_t \ge r_{wet}\); report current and longest run. | days | Daily precipitation with verified accumulation semantics. | \(r_{wet}\) is unresolved and must be approved; do not infer soil saturation or disease from the spell alone. |
| Temperature mean/range | \(T_{mean,k}=\operatorname{mean}(T_t)\); \(T_{range,k}=\operatorname{mean}(T^{max}_t-T^{min}_t)\), plus daily min/max summaries. | °C | IMD station/grid or weather/reanalysis source with explicit statistic. | Do not calculate daily range from values with inconsistent UTC/local-day windows. Convert K to °C only through a recorded transformation. |
| Temperature threshold exposure | Count and proportion of valid periods with \(T_t > T_{high}\) or \(T_t < T_{low}\); optionally longest run. | periods; %; days | Temperature series and verified thresholds. | No black-pepper-specific \(T_{high}\)/\(T_{low}\) verified; leave thresholds unset until sourced. Do not call generic extremes “crop stress” without crop evidence. |
| Relative humidity | Prefer provider’s quality-controlled RH. Candidate derived value: \(RH=100\,e_s(T_d)/e_s(T)\), where \(e_s(x)=6.112\exp(17.67x/(x+243.5))\), \(x\) in °C, using co-temporal air temperature and dewpoint. | % | IMD or other RH source; or verified co-temporal temperature and dewpoint from an authorized source. | Derived Magnus-formula approximation requires method/source review and metadata. Enforce 0–100%, retain inputs and derivation version; no substitution for leaf-wetness measurements. |
| High-humidity duration | Number of valid hours or fraction of valid hours with \(RH_t \ge RH_{threshold}\) in a declared window. | hours; % | Hourly RH, preferably station data or authorized model estimate. | Threshold unresolved; missing hours excluded from denominator and coverage reported. Not a disease label. |
| Soil-moisture state/change | Mean/median and change over window: \(\Delta SM_k=SM_t-SM_{t-k}\); optional layer-specific statistic. | source-dependent (e.g., volumetric fraction) | Measured soil sensor/lab context or labeled reanalysis/model layer (e.g., `swvl*`). | Do not equate modeled soil-water content with measured plot moisture. Depth, model, layer, units and uncertainty required; no authorized black-pepper soil records currently exist. |
| Seasonal phase | \(sin(2\pi d/Y)\), \(cos(2\pi d/Y)\), with day-of-year \(d\) and year length \(Y\in\{365,366\}\); alternatively month indicators. | dimensionless | Timestamp and declared calendar. | Encodes calendar timing only; does not establish a pepper growing season or phenology. |
| Seasonal rainfall/temperature summary | Aggregate the above features over a named crop phase only after sourced stage boundaries are available. | Variable-specific | Authorized weather plus verified `SeasonDefinition` and phase dates. | No phase dates currently verified. Do not use monsoon/planting/harvest labels as black-pepper stages without an authoritative source. |
| Extreme precipitation indicator | Flag \(P_t > q_p\) or \(P_t > P_{absolute}\) using a predefined climatology or approved threshold; report count, maximum and duration. | events; mm | Quality-controlled precipitation; fixed baseline/version or cited absolute threshold. | Define \(p\), reference period, location and estimator before evaluation. Fit thresholds within training folds only for ML; no source observations are available. |
| Extreme temperature indicator | Count valid periods above/below a cited absolute threshold or training-fold-derived percentile. | events; periods | Temperature data with consistent temporal support. | No black-pepper threshold established. Percentiles must not leak test/future data. |
| Wind exposure | Mean/max wind speed from components \(u,v\): \(WS=\sqrt{u^2+v^2}\); optional count over approved \(WS_{threshold}\). | m s⁻¹; periods | Co-temporal wind components with matching height and conventions. | Height/source metadata required; no crop damage threshold is assigned. |

Candidate window lengths and formulas are transparent data transformations, not approved crop rules. Feature definitions must be versioned and reviewed with the source period, aggregation, missingness, and units.

## 4. Crop-growth-stage alignment

Stage-aligned weather features should be computed only after an authoritative, licensed crop-specific source establishes:

1. Cultivar/variety and production context to which the timing applies.
2. Named growth stages and observable start/end criteria.
3. Geography/elevation applicability and publication/revision date.
4. Whether boundaries are calendar dates, thermal-time estimates, or field observations.

Then a stage rainfall feature could be \(\sum_{t\in[s_{start},s_{end}]}P_t\), and stage temperature features could be mean/min/max/threshold exposures over the same documented interval. Store stage source, version, crop/variety context and boundary method with each feature.

If stage boundaries are unknown, store calendar-window summaries only, with no crop-stage label. The current evidence does not justify black-pepper stage dates or thermal-time base temperatures for Idukki. A growing-degree-day feature \(GDD=\sum_t\max(0,T_{mean,t}-T_{base})\) is therefore **blocked pending a cited, applicable \(T_{base}\)** and stage definition.

## 5. Source mapping and evidence type

| Candidate source | Potential features | Evidence type | Principal limitations |
|---|---|---|---|
| Authorized IMD station series | Rainfall, temperature, RH, wind | Station observations, if the selected record confirms measurement and QC | Exact Idukki station, period, permission, and metadata unverified |
| IMD 0.25° gridded rainfall | Rain accumulation, wet/dry indicators | Gauge-informed gridded field | No exact licence/use permission; grid is not a local gauge; 1901–2024 page coverage does not establish completeness for a chosen location |
| ERA5 / ERA5-Land | Temperature, dewpoint, precipitation, wind, soil water and other model fields | Reanalysis estimates | Not ground observations; exact version/source request needed; current ERA5-Land archives are sparse and request 2 remains rejected |
| NASA POWER | Daily meteorological/solar summaries | Processed gridded/model product | Parameter-specific native resolution and upstream source; daily summaries may not retain event timing |
| NASA GPM IMERG | Rainfall rate/accumulation and wet/extreme indicators | Satellite precipitation retrieval/estimate | Precipitation-focused, not a local gauge; run/version, units and terrain validation matter |
| CHIRPS v3 | Precipitation totals and dry spells | Satellite/station-blended estimates; daily products are disaggregated | Daily `rnl` uses ERA5 and `sat` uses IMERG Late; not independent of those sources; daily date is a label, not a uniform station observation window |

No evidence category may be rewritten from estimated/derived to measured. If a feature combines multiple sources, retain each source’s contribution and alignment rule.

## 6. Missingness, leakage and validation controls

- Compute coverage and longest gap before feature aggregation; require a feature-specific valid denominator.
- Do not zero-fill missing rainfall/soil moisture or treat unobserved values as dry days.
- Keep current/history and forecast features separate. A forecast feature must retain issue time and be available before the prediction cutoff.
- Calculate climatological percentiles, imputation parameters, normalizers and learned thresholds using training data only inside each validation fold.
- Use temporal and geographic grouping for future splits; prevent adjacent grid cells/duplicate reports from leaking across train/test sets.
- Validate weather estimates against independent station/gauge observations where suitable data and permissions exist. Report per-district metrics and limitations.
- Do not interpret correlation as causation, feature importance as agronomic mechanism, or a weather feature as a disease/yield label.

## 7. Implementation and approval gate

Before implementation or feature computation, separately approve the target question, sources/versions, intended use, crop-stage evidence, thresholds, spatial support, quality rules, licence/attribution, and training eligibility if applicable. Retain raw inputs, formula/code version, parameters, input record IDs, output units and quality report.

No features were generated, no model was trained, and no data-use or project-owner authorization is granted by this design.
