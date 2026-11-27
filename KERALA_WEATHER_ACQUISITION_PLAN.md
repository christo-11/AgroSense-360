# Kerala Weather Acquisition Plan

**Status:** Planning only. No CDS request has been submitted and no data has been downloaded.  
**Research checked:** 2026-11-20  
**Target period:** 2015-01-01 through 2024-12-31, inclusive.

## Executive decision

Use the official ERA5-Land post-processed daily-statistics process for daily temperature summaries, dewpoint, and 10 m wind. Use the hourly ERA5-Land process for total precipitation and downward surface solar radiation because the daily-statistics product omits accumulated parameters. Keep the two previously acquired archives unchanged as audit evidence; the [quality assessment](./ERA5_LAND_QUALITY_ASSESSMENT.md) rejects them for training.

The recommended request pattern is monthly, with valid calendar days only. It is conservative and easy to resume, but entails many request jobs. Before full acquisition, a later approved stage must confirm the current CDS schema, boundary geometry, daily-statistic semantics, and accumulation handling with a small approved sample.

## Verified facts from official Copernicus/ECMWF documentation

1. The exact CDS process identifiers are `derived-era5-land-daily-statistics` and `reanalysis-era5-land`. Their public process definitions currently report version `1.0.0`. Process/API version is not a substitute for recording the source-data version and retrieval time.
2. ERA5-Land is a land-model reanalysis forced by ERA5 atmospheric fields. It is an estimate, not a local station observation. The official catalogue describes a global regular latitude-longitude grid at 0.1 degrees, nominally about 9 km, with hourly source data from January 1950 onward.
3. Daily statistics are calculated when requested; they are not a permanently archived daily dataset. The catalogue says the product is updated daily with an approximately six-day delay and is delivered as NetCDF in a ZIP archive. The current daily process exposes `daily_mean`, `daily_maximum`, and `daily_minimum`; `frequency` values `1_hourly`, `3_hourly`, and `6_hourly`; and timezone choices in whole-hour UTC offsets.
4. The daily process does **not** expose `total_precipitation` or solar-radiation variables in its `variable` enum. The catalogue explicitly says accumulated variables (including precipitation and runoff) are omitted. `surface_solar_radiation_downwards` is an hourly accumulated parameter, so it also belongs in the hourly request.
5. The hourly process schema exposes `variable`, `year`, `month`, `day`, `time`, `area`, `data_format` (`grib` or `netcdf`), and `download_format` (`zip` or `unarchived`). Its `area` input is four numbers; the proposed order below follows the CDS area convention `[north, west, south, east]`.
6. ERA5-Land forecast accumulations are from the 00 UTC forecast start through the forecast step. A value at validity time 00 UTC represents the preceding day's 24-hour accumulation (step 24). Accumulations must be differenced within the same forecast cycle, not summed as if every value were a one-hour increment.
7. The repository records an internal `APPROVED_PORTFOLIO_RESEARCH_ONLY` licence/terms classification for ERA5-Land based on cited publisher terms. This historical classification is not evidence of source-owner permission or project-owner authorization. Publisher terms may support specified uses subject to exact request terms, attribution, disclaimers, and third-party rights; each proposed activity separately requires valid, activity-specific project-owner authorization and any required source-owner permission. Commercial review remains conditional, and the current archives remain rejected for training. See [dataset licensing strategy](./DATASET_LICENSING_STRATEGY.md) and [dataset inventory](./DATASET_INVENTORY.md).

## Proposed geography

**Provisional CDS envelope:** `[13.0, 74.5, 8.0, 78.0]` in `[north, west, south, east]` order. It is a padded planning envelope, not a legally authoritative Kerala boundary. The exact envelope and grid cells must be checked against licensed, authoritative polygons for all 14 districts before request approval. Do not treat the box itself as a Kerala mask.

After retrieval, preserve the original rectangular grid and create a separate, versioned district overlay:

- Confirm every district polygon intersects the requested grid.
- Count valid grid cells by district and calculate the land-cell coverage fraction.
- Report coastal/very small districts with sparse or no representative cell coverage rather than fabricating a district value.
- Use a documented cell-center or polygon-area rule, and area-weighted aggregation where appropriate.
- Do not publish district summaries until an agronomist approves a minimum coverage rule. No threshold is asserted here.

The existing archive audit found only two principal time-varying timestamps in request 1 and 12 irregular timestamps per principal variable in request 2. Both archives use a global 0.1-degree grid, but Kerala-specific missingness and district coverage were not established. The declared GRIB message-length discrepancies in `tvh.grib` and `tvl.grib` remain unresolved. Both archives are marked `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`; preserve the originals as audit evidence. The audit established only that their global grids geometrically include Kerala, not that they provide representative district-level coverage.

## Proposed request specifications

### A. Daily temperature, dewpoint, and wind

**Process:** `derived-era5-land-daily-statistics`  
**Output:** NetCDF in ZIP, as currently described by the catalogue. The current process schema does not expose a `data_format` or `download_format` input; do not add those fields to the daily request.

| Purpose | Exact `variable` identifiers | Reported units | `daily_statistic` |
|---|---|---|---|
| Daily means | `2m_temperature`, `2m_dewpoint_temperature`, `10m_u_component_of_wind`, `10m_v_component_of_wind` | K; K; m s-1; m s-1 | `daily_mean` |
| Temperature extremes | `2m_temperature` | K | `daily_maximum` and `daily_minimum`, as separate requests |

Use `frequency: "1_hourly"` to calculate daily statistics from the hourly source. Use `time_zone: "utc+00:00"` for reproducible UTC-day statistics.

India Standard Time is UTC+05:30, which is not an allowed timezone value in the current daily process schema. Do not label UTC daily statistics as local-day statistics. If the product requires IST-day maxima/minima/means, retrieve the needed hourly variables and compute the half-hour-offset day windows in a separately approved processing stage.

Example request shape for January 2015 daily means (illustrative only; **not submitted**):

```json
{
  "variable": [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind"
  ],
  "year": "2015",
  "month": "01",
  "day": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
          "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
          "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"],
  "daily_statistic": "daily_mean",
  "frequency": "1_hourly",
  "time_zone": "utc+00:00",
  "area": [13.0, 74.5, 8.0, 78.0]
}
```

For each year-month, construct `day` from the actual calendar (including February 29 only in leap years). The request plan is 120 monthly mean jobs, plus 120 monthly maximum-temperature jobs and 120 monthly minimum-temperature jobs: **360 daily-statistics jobs**. If CDS confirms a safe multi-month request form later, the count can be reduced without using invalid dates.

### B. Hourly precipitation and solar radiation

**Process:** `reanalysis-era5-land`  
**Variables and units:** `total_precipitation` (m) and `surface_solar_radiation_downwards` (J m-2). Both are accumulated forecast parameters in the official parameter listing.

Request all 24 hourly validity times (`00:00` through `23:00`) for each valid day and month. Proposed format is GRIB in a ZIP archive to preserve forecast-step metadata (`stepType`, start/end step, forecast reference time, and validity time) for accumulation QA. NetCDF is an official alternative, but it must be shown to preserve equivalent step metadata before it is used for de-accumulation.

Request fields for a monthly chunk:

```text
variable       = ["total_precipitation", "surface_solar_radiation_downwards"]
year           = "YYYY"
month          = "MM"
day            = valid zero-padded calendar-day strings for that month
time           = "00:00" ... "23:00"
area           = [13.0, 74.5, 8.0, 78.0]
data_format    = "grib"
download_format= "zip"
```

Plan for 120 monthly requests plus a small final boundary request containing **2025-01-01 00:00 UTC**, needed for the forecast-step-24 accumulation corresponding to 2024-12-31. For each calendar-day total, retain the native accumulation and its forecast-reference/step metadata. If deriving hourly increments, difference only successive steps in the same 00 UTC forecast cycle; treat the 00 UTC step-24 value as the previous day, not the current hour. Verify behavior against the official documentation and decoded metadata before producing any rainfall or radiation totals.

**Do not sum the accumulated values directly.** Preserve the original GRIB members unchanged; derived increments or daily totals belong in a separate versioned output.

### Date and chunk rules

- Period: 2015-01-01 through 2024-12-31 inclusive; 3 leap years in this interval.
- Chunk by one calendar month (`year`, `month` scalar and the valid days for that month). This avoids relying on unverified behavior for invalid dates in multi-year/month selections.
- Persist the exact submitted request JSON and its canonical SHA-256 fingerprint before execution.
- Submit sequentially at first. Honor current CDS account/service limits; the present public process schema does not establish a safe concurrency quota.
- Do not repeat a request if its fingerprint already has an active or validated result. Store the CDS task/job reference, status transitions, attempt count, and output checksum.
- Retries must resume the same job when possible; a failed/expired job must not be recorded as a successful dataset.

## Storage estimate (estimate, not a CDS size promise)

For planning only, the provisional box aligns to about 51 latitude by 36 longitude coordinates (1,836 cells). Assuming 4-byte values, excluding coordinates, compression, ZIP overhead, metadata and any boundary overlap:

| Product arrays | Calculation | Uncompressed values |
|---|---|---:|
| Four daily-mean fields plus temperature daily max/min | 3,653 days x 6 fields x 1,836 cells x 4 bytes | 160,965,792 bytes (153.51 MiB) |
| Hourly precipitation and solar radiation | 87,672 hours x 2 fields x 1,836 cells x 4 bytes | 1,287,726,336 bytes (1.199 GiB) |
| Combined | Approximate scalar values only | 1.349 GiB |

These are not compressed sizes or a verified output shape. Actual output can differ due to CDS grid selection, encoding, metadata, forecast boundaries and ZIP compression. Reserve **5 GB** for original request archives, validation/staging and small derived products, then replace the estimate with measured sizes from an approved pilot. This is about 1.4% of the 352 GB free-space figure supplied for the laptop, not a guarantee of download size.

## Acquisition, provenance, and validation gates

1. **Before any request:** obtain explicit acquisition approval, confirm the applicable license and intended use, review the live CDS form/schema, and approve the district geometry and UTC-versus-IST semantics.
2. **Request manifest:** record process ID/schema version, complete parameters, request fingerprint, dataset/source URL, license evidence, submit/retrieval timestamps in UTC, task ID, status, output filename/size, SHA-256, archive/member inventory and validation results.
3. **Immutable raw layer:** retain original ZIP/GRIB/NetCDF bytes unchanged in access-controlled object storage or authorized local storage. Keep raw grids outside Git. Store checksummed metadata and DVC pointers/manifests in Git only if approved.
4. **Integrity:** validate HTTP/job completion, expected content size when provided, ZIP CRC, member listing, file signatures, GRIB/NetCDF readability, and SHA-256. Write to a `.part` path and atomically rename only after validation; never overwrite a prior artifact.
5. **Temporal QA:** verify exact expected dates/times, uniqueness, ordering, missing periods, leap days, day boundary handling and per-variable availability. Expected core daily count is 3,653 days; expected hourly count is 87,672 validity hours plus the final boundary record.
6. **Units and accumulations:** check units against the official variable list, confirm `total_precipitation` and radiation forecast-step metadata, and test de-accumulation around ordinary hours, 00 UTC resets, month ends, leap days and the 2024/2025 boundary.
7. **Spatial QA:** verify coordinates, 0.1-degree increments, bounding-box coverage, Kerala polygon intersection and district-by-district valid cell counts/coverage. Keep the global missing percentage separate from Kerala-only missingness.
8. **Missing/outlier policy:** record fill-value markers and missing counts by time and district. Preserve missing values in raw data; do not globally impute. Flag physical outliers for review rather than silently clipping. Any feature-stage imputation must be explicit, fit on training folds only, and emit an imputation mask.
9. **Acceptance report:** stop and mark the chunk `BLOCKED`/`FAILED` if checksum, dates, units, CRS/grid, district coverage, license or accumulation checks fail. A small pilot must pass before scheduling the remaining period.

## Hardware fit and operational risks

The user-reported laptop has 8 GB RAM, AMD Ryzen 3 7320U and integrated Radeon graphics; no CUDA is assumed. The spatially clipped estimate is small enough to plan for local, chunked retrieval and QA, but not for loading a decade of hourly arrays into RAM at once. Use bounded monthly files and streaming/chunked readers. Avoid retaining duplicate decompressed copies. A cloud notebook is not required for this acquisition estimate; use cloud compute only if later approved processing, image training or measured resource use requires it.

Key risks: provisional box misses a district edge; daily UTC summaries are mistaken for IST days; accumulated values are misread as increments; recent data are provisional ERA5-Land-T rather than consolidated; daily request results can change with the input data/processing at retrieval time; CRS/boundary licensing is unresolved; request service limits and actual compressed output sizes are not established here.

## Unresolved decisions

- Which authoritative, licensed district-boundary source and district version will be used?
- Is UTC-day aggregation acceptable, or are IST-day statistics required?
- Are 10 m wind and dewpoint daily means sufficient, or are additional statistics needed?
- Is hourly solar radiation needed for the feature, given its accumulation processing and added volume?
- What is the proposed activity—portfolio/demo, pilot research, or commercial use? Published terms or an internal licence/terms classification do not authorize activity; each use requires applicable source-owner rights and separate valid purpose-specific project-owner authorization.
- What missing-cell coverage threshold is acceptable per district, and who approves it?
- What CDS account-level request limits and actual monthly output sizes apply?

## Official sources (checked 2026-11-20)

- [ERA5-Land daily-statistics catalogue](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics)
- [Live daily-statistics process schema and exact option enums](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics)
- [ERA5-Land hourly catalogue](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land)
- [Live hourly process schema and exact variable/format enums](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land)
- [ECMWF ERA5-Land data documentation: grid, formats, parameter names and accumulations](https://confluence.ecmwf.int/spaces/CKB/pages/140385202/ERA5-Land+data+documentation)
- Project evidence: [quality assessment](./ERA5_LAND_QUALITY_ASSESSMENT.md), [acquisition report](./DATASET_ACQUISITION_REPORT.md), [inventory](./DATASET_INVENTORY.md), [licensing strategy](./DATASET_LICENSING_STRATEGY.md), [download manifest](./data/metadata/era5_land_download_manifest.json).
