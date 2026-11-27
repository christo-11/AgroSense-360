# ERA5-Land GRIB1 Header-Length Diagnostic Addendum

**Record date:** 23 November 2026  
**Project:** AgroSense-360  
**Related records:**
- `data/metadata/era5_land_download_manifest.json`
- `data/metadata/era5_land_quality_report.json`
- `AGROSENSE_ERA5_LAND_HISTORICAL_ACQUISITION_RECONCILIATION.md`

## 1. Purpose

This addendum records an independent follow-up investigation of the GRIB1 message-length discrepancy previously identified in the ERA5-Land request 2 archive.

It supplements the existing historical records. It does not replace, overwrite, or retrospectively alter them.

## 2. Files examined

Archive:

`data/raw/weather/era5_land/era5_land_request_2.zip`

ZIP members:

- `tvh.grib`
- `tvl.grib`

Both members were read directly from the ZIP archive without modifying the original archive.

## 3. Independent raw-header findings

The first eight bytes of both members begin with:

`47 52 49 42 81 a6 1d 01`

Interpretation:

- GRIB signature: `GRIB`
- GRIB edition: 1
- Three-byte GRIB1 length field: `81 A6 1D` (hexadecimal), representing 8,496,669 bytes.

Observed measurements:

| Measurement | tvh.grib | tvl.grib |
|---|---:|---:|
| ZIP uncompressed member size | 12,967,284 | 12,967,284 |
| GRIB1 header-declared length | 8,496,669 | 8,496,669 |
| Difference | 4,470,615 | 4,470,615 |
| Bytes at declared boundary | `00 00 98 00` | `08 00 08 00` |
| Final four bytes | `7777` | `7777` |
| GRIB signatures in member | 1 | 1 |
| `7777` markers in member | 1 | 1 |

The declared boundary does not contain the end marker. The end marker is present at the actual end of each member.

## 4. ecCodes parsing result

A separate diagnostic extracted each member to a temporary location and parsed it using ecCodes.

For each member:

- ecCodes parsed one GRIB message.
- ecCodes reported `totalLength = 12,967,284` bytes.
- The reported length matched the uncompressed ZIP member size.

This successful parser result does not make the raw GRIB1 header length field consistent. The direct byte inspection independently confirms that the three-byte length field declares 8,496,669 bytes.

The temporary-file cleanup generated a Windows permission error after both parsing results had been printed. This cleanup issue does not change the observed header bytes or ZIP member measurements.

## 5. Technical assessment

The original quality report's declared-length discrepancy is independently confirmed.

The evidence establishes an internal inconsistency between the GRIB1 header-declared length and the actual member length.

The evidence does not establish the cause. No conclusion is made that the publisher intentionally produced the discrepancy, that all data values are invalid, or that the entire ZIP archive is corrupt.

The archive-level integrity checks and the internal GRIB format checks remain separate assessments.

## 6. Data-quality disposition

Until the publisher explains the discrepancy or supplies corrected files:

- Do not treat `tvh.grib` or `tvl.grib` as trusted production inputs.
- Do not silently repair or rewrite the original GRIB members.
- Preserve the original ZIP archive and its previously recorded SHA-256 checksum.
- Preserve the original manifest and quality report.
- Retain the existing quality-rejected assessment.

## 7. Governance boundary

This addendum is a technical diagnostic record only.

It does not grant project-owner authorization, external source-owner permission, research approval, pilot approval, commercial-use approval, redistribution rights, or ML-training eligibility.

All existing Stage 23 governance restrictions remain in force.

## 8. Final statement

Independent raw-byte inspection confirms that both `tvh.grib` and `tvl.grib` contain a GRIB1 header length of 8,496,669 bytes while each actual uncompressed member is 12,967,284 bytes.

The discrepancy remains unresolved. Publisher clarification or corrected source files are required before these members can be considered reliable production inputs.

