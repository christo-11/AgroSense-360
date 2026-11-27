# ERA5-Land Dataset Quality Assessment

Audit time (UTC): 2026-11-20T05:02:38.746050+00:00

## Decisions

| Dataset result | Decision | Training gate | Reason |
|---|---|---|---|
| Request 1 (Supplied ERA5-Land NetCDF result) | **NEEDS_MORE_DATA** | **REJECT_FOR_TRAINING** | The main data_0.nc has only two instants, 2024-01-03 03:00 and 06:00 UTC. Static ancillary fields do not extend the weather time series. It cannot support historical or seasonal weather features. |
| Request 2 (Supplied ERA5-Land GRIB result) | **NEEDS_MORE_DATA** | **REJECT_FOR_TRAINING** | Fifty variables have only 12 timestamps each on four days between 2011-01-11 and 2011-01-29, with observed gaps of 2, 7, 15, 63 and 327 hours. Nine singleton ancillary records do not make a continuous series. Two ancillary GRIB1 members also have internal message-length discrepancies. |

**Overall: NEEDS_MORE_DATA. Do not train on either current archive.**

## Evidence and method

Inspected `DATASET_ACQUISITION_REPORT.md`, `data/metadata/era5_land_download_manifest.json`, `backend/scripts/download_era5_requests.py`, both original ZIPs, and `LOCAL_DEVELOPMENT_GUIDE.md`. Both ZIP CRC checks passed again. SHA-256 values were recomputed after the read-only scans and match the acquisition manifest. No archive member was extracted to disk and no source file was modified.

NetCDF data variables were scanned using bounded HDF5 chunks; the single 12,990,436-byte classic NetCDF member was buffered in memory for its value count. GRIB messages were parsed one at a time with ecCodes. Full per-variable details and timestamps are in the JSON report.

## Dataset geometry and missingness

Both grids span latitude -90 to 90 and longitude 0 to 359.9, with observed 0.1-degree spacing. The coordinate extent intersects Kerala. No administrative boundary was applied, so valid-cell coverage inside Kerala itself is not claimed. Neither grid is a Kerala-only sample.

In request 1, each of the 37 main NetCDF fields contains 8,541,474 missing values of 12,967,200 global grid-time values (65.87%). The fields share the same NaN count, consistent with a shared ocean/land mask; that global percentage is not a Kerala-specific quality rate. Static ancillary fields were also scanned; their declared -32767 fill values were not present in the scanned fields.

In request 2, each time-varying GRIB field reports 4,270,737 missing points of 6,483,600 global points per message (65.87%); the singleton ancillary messages report zero missing points. This is a global-grid count, not a Kerala-only count.

## Request 1: NetCDF

The main `data_0.nc` file has exactly two `valid_time` coordinates: 2024-01-03 03:00 and 06:00 UTC (3-hour separation). All data fields below share this two-time sample; it is not a continuous hourly or historical series. Ancillary fields have singleton coordinate timestamps and do not extend the weather series.

| Variable | Description | Units | Time coverage / count | Missing marker; count | Agricultural assessment |
|---|---|---|---|---|---|
| asn | Snow albedo | (0 - 1) | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| e | Evaporation | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| es | Snow evaporation | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| evabs | Evaporation from bare soil | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evaow | Evaporation from open water surfaces excluding oceans | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evatc | Evaporation from the top of canopy | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evavt | Evaporation from vegetation transpiration | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| lai_hv | Leaf area index, high vegetation | m**2 m**-2 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| lai_lv | Leaf area index, low vegetation | m**2 m**-2 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| lblt | Lake bottom temperature | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| licd | Lake ice total depth | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lict | Lake ice surface temperature | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lmld | Lake mix-layer depth | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lmlt | Lake mix-layer temperature | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lshf | Lake shape factor | dimensionless | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| ltlt | Lake total layer temperature | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| pev | Potential evaporation | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ro | Runoff | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| rsn | Snow density | kg m**-3 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sd | Snow depth | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sde | Snow depth | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sf | Snowfall | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| smlt | Snowmelt | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| snowc | Snow cover | % | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sp | Surface pressure | Pa | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| src | Skin reservoir content | m of water equivalent | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| sro | Surface runoff | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ssro | Sub-surface runoff | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl1 | Volumetric soil water layer 1 | m**3 m**-3 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl2 | Volumetric soil water layer 2 | m**3 m**-3 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl3 | Volumetric soil water layer 3 | m**3 m**-3 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl4 | Volumetric soil water layer 4 | m**3 m**-3 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| t2m | 2 metre temperature | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| tp | Total precipitation | m | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| tsn | Temperature of snow layer | K | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| u10 | 10 metre U wind component | m s**-1 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| v10 | 10 metre V wind component | m s**-1 | 2024-01-03T03:00:00+00:00 to 2024-01-03T06:00:00+00:00 / 2 | NaN; 8,541,474/12,967,200 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| glm | Glacier mask | fraction | 2013-01-25T00:00:00+00:00 to 2013-01-25T00:00:00+00:00 / 1 | -32767; 0/6,483,600 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| cl | Lake cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| cvh | High vegetation cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| cvl | Low vegetation cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| dl | Lake total depth | m | 1995-01-01T00:00:00+00:00 to 1995-01-01T00:00:00+00:00 / 1 | -32767; 0/6,483,600 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| z | Geopotential | m**2 s**-2 | unavailable (1 coordinate point(s) recorded) | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| lsm | Land-sea mask | (0 - 1) | unavailable (1 coordinate point(s) recorded) | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| slt | Soil type | ~ | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| tvh | Type of high vegetation | ~ | 1996-01-01T00:00:00+00:00 to 1996-01-01T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| tvl | Type of low vegetation | ~ | 1996-01-01T00:00:00+00:00 to 1996-01-01T00:00:00+00:00 / 1 | -32767.0; 0/6,483,600 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |

Coordinate/metadata variables (for example `latitude`, `longitude`, `valid_time`, `time`, `number`, and `expver`) are retained with counts and raw coordinate evidence in the JSON.

## Request 2: GRIB

ecCodes parsed 609 messages across 10 members (editions 1 and 2). The 50 multi-time variables have 12 timestamps each; the timestamps are on four days between 2011-01-11 and 2011-01-29. Observed gaps within each series are 2, 7, 15, 63 and 327 hours. The nine singleton ancillary variables are not a time series.

The `tp` variable is marked `accum`, with GRIB step ranges 12-13, 14-15, and 21-22; values must not be summed as if they were uniform hourly observations. Temperature (`2t`) is marked `instant`.

| Variable | Description | Units | Time coverage / count | Missing marker; aggregate count | Agricultural assessment |
|---|---|---|---|---|---|
| 10u | 10 metre U wind component | m s**-1 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| 10v | 10 metre V wind component | m s**-1 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| 2d | 2 metre dewpoint temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| 2t | 2 metre temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| asn | Snow albedo | (0 - 1) | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| cl | Lake cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| cvh | High vegetation cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| cvl | Low vegetation cover | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| dl | Lake total depth | m | 1995-01-01T00:00:00+00:00 to 1995-01-01T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| e | Evaporation | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| es | Snow evaporation | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| evabs | Evaporation from bare soil | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evaow | Evaporation from open water surfaces excluding oceans | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evatc | Evaporation from the top of canopy | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| evavt | Evaporation from vegetation transpiration | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| fal | Forecast albedo | (0 - 1) | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| glm | Glacier mask | Proportion | 2025-10-06T00:00:00+00:00 to 2025-10-06T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lai_hv | Leaf area index, high vegetation | m**2 m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| lai_lv | Leaf area index, low vegetation | m**2 m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| lblt | Lake bottom temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| licd | Lake ice total depth | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lict | Lake ice surface temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lmld | Lake mix-layer depth | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lmlt | Lake mix-layer temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lshf | Lake shape factor | dimensionless | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| lsm | Land-sea mask | (0 - 1) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| ltlt | Lake total layer temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| pev | Potential evaporation | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ro | Runoff | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| rsn | Snow density | kg m**-3 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sd | Snow depth | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sde | Snow depth | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sf | Snowfall | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| skt | Skin temperature | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| slhf | Time-integrated surface latent heat net flux | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| slt | Soil type | (Code table 4.213) | 2013-11-29T00:00:00+00:00 to 2013-11-29T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| smlt | Snowmelt | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| snowc | Snow cover | % | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| sp | Surface pressure | Pa | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| src | Skin reservoir content | m of water equivalent | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | SECONDARY_CANDIDATE_REQUIRES_DOMAIN_REVIEW |
| sro | Surface runoff | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| sshf | Time-integrated surface sensible heat net flux | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ssr | Surface net short-wave (solar) radiation | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ssrd | Surface short-wave (solar) radiation downwards | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| ssro | Sub-surface runoff | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| stl1 | Soil temperature level 1 | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| stl2 | Soil temperature level 2 | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| stl3 | Soil temperature level 3 | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| stl4 | Soil temperature level 4 | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| str | Surface net long-wave (thermal) radiation | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| strd | Surface long-wave (thermal) radiation downwards | J m**-2 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl1 | Volumetric soil water layer 1 | m**3 m**-3 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl2 | Volumetric soil water layer 2 | m**3 m**-3 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl3 | Volumetric soil water layer 3 | m**3 m**-3 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| swvl4 | Volumetric soil water layer 4 | m**3 m**-3 | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| tp | Total precipitation | m | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | POTENTIAL_FEATURE_BUT_CURRENT_SAMPLE_INADEQUATE |
| tsn | Temperature of snow layer | K | 2011-01-11T13:00:00+00:00 to 2011-01-29T22:00:00+00:00 / 12 | 9999; 51,248,844/77,803,200; per msg 4,270,737-4,270,737 | LOW_DIRECT_KERALA_RELEVANCE_OR_SECONDARY |
| tvh | Type of high vegetation | (Code table 4.234) | 1996-01-01T00:00:00+00:00 to 1996-01-01T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |
| tvl | Type of low vegetation | (Code table 4.234) | 1996-01-01T00:00:00+00:00 to 1996-01-01T00:00:00+00:00 / 1 | 9999; 0/6,483,600; per msg 0-0 | ANCILLARY_ONLY_PENDING_ENCODING_AND_LOCAL_QC |

## GRIB framing and ecCodes findings

All 609 messages were parsed by ecCodes and had a `7777` end marker at the parsed boundary. `clake.grib`, `lsm.grib`, and `slt.grib` each have 44 zero bytes after a valid message end; this is ordinary trailing zero padding.

**`tvh.grib` and `tvl.grib` are different:** each is one GRIB1 member with one `GRIB` signature at byte 0. Its header declares 8,496,669 bytes, but the member is 12,967,284 bytes; there is no `7777` at the declared offset. The `7777` marker is at the member end, and ecCodes accepts the complete member. There is no second GRIB signature, so this is not concatenated messages; it is not harmless padding because the declared boundary itself is wrong. Treat this as a genuine structural concern of uncertain cause and do not rely on these two fields until Copernicus confirms or supplies corrected files.

## Suitability conclusions

- **Historical weather features:** not supported by either current request result. Request 1 has two instants; request 2 has sparse timestamps on four days.
- **Rainfall:** `tp` exists, but only sparse accumulated samples are present. These files cannot support reliable continuous daily totals, seasonal rainfall, or drought indices.
- **Temperature:** `t2m`/`2t` exist, but the dates are far too sparse for historical feature engineering or training.
- **Soil:** `swvl1`-`swvl4` and `stl1`-`stl4` are reanalysis soil water/temperature estimates, not soil chemistry/fertility. `slt` is a categorical code requiring its code table.
- **Kerala crop recommendation:** not supported. These archives provide no crop outcome labels, yield targets, management records, or validated Kerala-only samples. Weather covariates alone do not establish crop recommendation suitability.
- ERA5-Land values are reanalysis/model estimates, not direct local observations. No station comparison was performed.

## Next actions

1. Keep both archives unchanged and do not use them for training.
2. Before another acquisition, define a Kerala-focused area and uninterrupted historical period suited to the planned feature; then submit a targeted request only after approval.
3. Validate temporal completeness and precipitation accumulation intervals in any replacement request.
4. In a later approved stage, check valid land cells against an authoritative Kerala boundary and combine weather with verified crop/yield labels and soil sources.
5. Ask Copernicus to confirm or correct the two anomalous vegetation-type GRIB members before relying on them.

## Artifacts and integrity

- `data/raw/weather/era5_land/era5_land_request_1.zip` - 647003080 bytes; SHA-256 `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441`; ZIP CRC PASS; hash matches acquisition manifest.
- `data/raw/weather/era5_land/era5_land_request_2.zip` - 2026384498 bytes; SHA-256 `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0`; ZIP CRC PASS; hash matches acquisition manifest.
- Full variable metrics, exact timestamps, message counts, step metadata and member-level boundary results: `data/metadata/era5_land_quality_report.json`.
- No dataset downloaded, extracted to disk, preprocessed or used to train a model. No application, database, schema, migration, `.env`, or `.cdsapirc` file was accessed or changed.
