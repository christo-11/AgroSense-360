# AgroSense-360
# ERA5-Land Historical Acquisition Reconciliation

**Record date:** 2026-11-23  
**Record type:** Historical acquisition and evidence reconciliation  
**Dataset:** ERA5-Land  
**Dataset ID:** reanalysis-era5-land  
**Source:** Copernicus Climate Data Store (CDS)  
**Status:** HISTORICAL_ACQUISITION_RECONCILED_WITH_LIMITATIONS

---

## 1. Purpose and scope

This document records the historical acquisition evidence for two ERA5-Land archives held by the AgroSense-360 project.

It reconciles:
- The two existing archive files.
- Their SHA-256 checksums and ZIP integrity records.
- The local acquisition manifest.
- Two successful Copernicus CDS receipts.
- The observed archive formats and temporal coverage.
- The relationship between acquisition chronology and Stage 23 governance records.

This document is an evidence record only. It does not grant new authorization or change any existing governance decision.

## 2. Historical acquisition chronology

The local manifest records these retrieval timestamps:

| Archive | Retrieved at (UTC) | Retrieved at (IST) |
|---|---|---|
| era5_land_request_1.zip | 2026-11-20 02:22:48 UTC | 2026-11-20 07:52:48 IST |
| era5_land_request_2.zip | 2026-11-20 02:23:35 UTC | 2026-11-20 07:53:35 IST |

The manifest reconciliation timestamp is:

2026-11-20T18:53:34+05:30

The four Stage 23 governance documents were created in the project folder on 2026-11-23 at 10:03:27 (local filesystem time).

The permission-response log was subsequently modified at 10:59:55 on 2026-11-23.

These filesystem timestamps support the conclusion that the archive retrievals recorded in the manifest occurred before the Stage 23 documents were created in the project folder.

**Chronology limitation:** Filesystem creation and modification timestamps do not independently establish the exact time at which the Stage 23 decision was formally made. This record therefore does not claim an independently verified formal decision timestamp.

## 3. Archive 1 — NetCDF

**Local filename:** era5_land_request_1.zip  
**Local path:** data/raw/weather/era5_land/era5_land_request_1.zip  
**Manifest request number:** 1  
**Manifest object-store reference:** 24a5f33e75200171321741639baf695f  
**Actual size:** 647,003,080 bytes  
**SHA-256:** 337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441  
**Observed format:** NetCDF inside ZIP  
**Archive integrity:** ZIP format valid; CRC verified.

### Matching Copernicus receipt

**Request UUID:** 075dbe87-20f2-4e58-aed1-14ed9fdf6798  
**Collection:** reanalysis-era5-land  
**Requested date:** 2024-01-03  
**Requested times:** 03:00 and 06:00  
**Data format:** NetCDF  
**Download format:** ZIP  
**Receipt status:** successful  
**Receipt origin:** UI

The archive's observed dates and NetCDF format match the receipt parameters.

The archive metadata records observations at 03:00 and 06:00 UTC. This is a limited two-time-step acquisition, not a continuous hourly time series.

## 4. Archive 2 — GRIB

**Local filename:** era5_land_request_2.zip  
**Local path:** data/raw/weather/era5_land/era5_land_request_2.zip  
**Manifest request number:** 2  
**Manifest object-store reference:** 7aa7a686527d3e900aa7b8dce4709fa6  
**Actual size:** 2,026,384,498 bytes  
**SHA-256:** dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0  
**Observed format:** GRIB inside ZIP  
**GRIB message count:** 609  
**Archive integrity:** ZIP format valid; CRC verified.

### Matching Copernicus receipt

**Request UUID:** 4e1e2a12-1800-4983-80ea-4ab38a1fd5f4  
**Collection:** reanalysis-era5-land  
**Requested year:** 2011  
**Requested months:** January  
**Requested days:** 11, 25, 26 and 29  
**Requested times:** 13:00, 15:00 and 22:00  
**Data format:** GRIB  
**Download format:** ZIP  
**Receipt status:** successful  
**Receipt origin:** UI

The archive's observed GRIB format and temporal coverage correlate with the receipt parameters.

The archive contains 12 distinct timestamps between 2011-01-11 and 2011-01-29 UTC. The intervals are irregular. This must not be described as a continuous hourly time series.

## 5. Historical size discrepancy

The manifest preserves the following user-reported approximate sizes:

| Manifest request | User-reported approximate size | Actual archive size |
|---|---:|---:|
| 1 | 2.03 GB | 647,003,080 bytes |
| 2 | 647 MB | 2,026,384,498 bytes |

The reported approximate sizes are reversed relative to the observed archive sizes.

The original reported values are retained as historical information. The actual sizes and SHA-256 checksums are the independently verified archive measurements.

## 6. Relationship between receipt identifiers and manifest references

The manifest contains object-store reference identifiers:

- Request 1: 24a5f33e75200171321741639baf695f
- Request 2: 7aa7a686527d3e900aa7b8dce4709fa6

The Copernicus receipts contain different request UUIDs:

- Request 1 receipt: 075dbe87-20f2-4e58-aed1-14ed9fdf6798
- Request 2 receipt: 4e1e2a12-1800-4983-80ea-4ab38a1fd5f4

The receipt-to-archive mapping is supported by matching dataset identity, dates, times and formats.

The receipts do not explicitly establish a direct identifier-level relationship to the manifest's object-store references. The mapping is therefore recorded as a content-based correlation.

## 7. Licence evidence and limitations

The uploaded receipts list these licence or terms references:

- CC-BY licence (version 1)
- Terms of use of the Copernicus Climate Data Store (version 13)
- Data protection and privacy statement (version 24)

The presence of these references in the receipts is evidence of the terms associated with the recorded requests. It is not, by itself, a completed legal assessment of every proposed project use.

The applicable licence text, attribution requirements, product-specific conditions, third-party data terms and any commercial or redistribution conditions must be reviewed before the corresponding use is approved.

The Copernicus attribution wording recorded in the existing manifest must be preserved and applied where required.

## 8. Technical quality and provenance limitations

The existing quality report identifies the following limitations:

1. The 2024 NetCDF archive contains only two observed time steps.
2. The 2011 GRIB archive contains 12 distinct timestamps with irregular temporal gaps.
3. The GRIB archive includes multiple GRIB editions and earth-shape codes.
4. Missing-value marker 9999 is recorded.
5. Missing-value counts vary across GRIB messages.
6. Some ancillary/static fields have dates that differ from the main time-series period.
7. The observed grid is global, regular latitude-longitude, with approximately 0.1-degree spacing.
8. The GRIB members tvh.grib and tvl.grib have reported message-length mismatches:
   - Header-declared length: 8,496,669 bytes.
   - ecCodes input length: 12,967,284 bytes.
9. The exact ERA5-Land product version is not pinned.
10. The original request-history MHT was not independently inspected.

The GRIB length discrepancies remain unresolved technical warnings. ZIP CRC success does not, by itself, resolve these internal message-length discrepancies.

These archives must not be treated as validated local ground observations or as sufficient evidence for continuous local weather coverage.

The existing quality report's status remains QUALITY_REJECTED.

## 9. Stage 23 governance relationship

The Stage 23 documents record:

- Project-owner authorization: PENDING.
- Source-owner inquiry authorization: NOT AUTHORIZED.
- Source-owner permission received: NO.
- Dataset acquisition authorization: NO.
- Pilot research use authorization: NO.
- ML training authorization: NO.
- Commercial use and redistribution authorization: NO.

The archives and successful receipts establish historical retrieval evidence. They do not establish that the project owner had approved the acquisition at the time, nor do they retroactively authorize any use.

The Stage 23 decision concerning existing ERA5-Land archives remains unchanged.

No permission, research, training, commercial-use or redistribution status is upgraded by this reconciliation.

## 10. Current evidence-based status

| Item | Evidence-based status |
|---|---|
| Archive 1 exists | VERIFIED |
| Archive 2 exists | VERIFIED |
| SHA-256 checksums | VERIFIED |
| ZIP integrity | VERIFIED |
| Copernicus receipts | AVAILABLE |
| Receipt-to-archive mapping | CONTENT-BASED CORRELATION |
| Exact object-store-reference-to-receipt UUID mapping | NOT ESTABLISHED |
| Exact product version | UNPINNED |
| Data quality | QUALITY_REJECTED |
| Project-owner authorization | PENDING |
| Source-owner permission | NOT RECEIVED |
| Pilot research use | NOT AUTHORIZED |
| ML training | NOT AUTHORIZED |
| Commercial use / redistribution | NOT AUTHORIZED |

## 11. Required preservation rules

1. Preserve both original ZIP archives unchanged.
2. Preserve their original SHA-256 checksums.
3. Preserve both original Copernicus receipts.
4. Preserve the original download manifest and quality report.
5. Do not overwrite or rewrite Stage 23 governance records.
6. Do not change authorization fields based solely on successful retrieval receipts.
7. Do not use these archives for pilot research or ML training unless the required project-owner and applicable source/licence approvals are separately documented.
8. Record any future permission or quality decision in a new, dated evidence record.

## 12. Final reconciliation statement

The two ERA5-Land archives are present and their archive integrity and SHA-256 checksums have been verified.

Two successful Copernicus CDS receipts provide matching request-date and format evidence for the archives. The receipt-to-archive mapping is supported by content correlation, while the direct relationship between receipt UUIDs and manifest object-store references remains unestablished.

The archives were retrieved according to the timestamps recorded in the manifest before the Stage 23 governance files were created in the project folder. This chronology does not prove historical project-owner authorization.

The existing Stage 23 restrictions remain in force. This document records historical acquisition evidence only and does not grant authorization for research, training, commercial use or redistribution.
