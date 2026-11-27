# AgroSense-360 Copernicus CDS GRIB1 Technical Evidence

**Investigation date:** 23 November 2026  
**Purpose:** Technical clarification package for unresolved ERA5-Land ancillary-member header lengths

## Scope and provenance

- **Archive:** `data/raw/weather/era5_land/era5_land_request_2.zip`
- **Affected ZIP members:** `tvh.grib` and `tvl.grib`
- **GRIB edition:** 1
- **Manifest request reference:** `7aa7a686527d3e900aa7b8dce4709fa6`
- **Related Copernicus receipt UUID:** `4e1e2a12-1800-4983-80ea-4ab38a1fd5f4`

The existing historical reconciliation maps that receipt to request 2 by matching the collection, dates/times and GRIB/ZIP formats. It explicitly does not establish a direct identifier-level link between the receipt UUID and the manifest object-store reference. The identifiers above are therefore reported as separately recorded, content-correlated references, not as identical IDs.

Both local ERA5-Land archives were hashed for this check and compared with their respective existing manifest records:

| Archive | Manifest request reference | Manifest SHA-256 | Local verification |
|---|---|---|---|
| `era5_land_request_1.zip` | `24a5f33e75200171321741639baf695f` | `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441` | MATCH |
| `era5_land_request_2.zip` | `7aa7a686527d3e900aa7b8dce4709fa6` | `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0` | MATCH |

The request 2 archive size is 2,026,384,498 bytes. Request 1 is included only to document the requested two-archive checksum cross-check; the affected members are in request 2.

## Raw GRIB1 evidence

Both members begin with these raw bytes:

`47 52 49 42 81 A6 1D 01`

This identifies the `GRIB` signature and edition 1. The three-byte GRIB1 length field is `81 A6 1D`, which declares **8,496,669 bytes**.

| Measurement | `tvh.grib` | `tvl.grib` |
|---|---:|---:|
| Actual uncompressed ZIP-member size | 12,967,284 bytes | 12,967,284 bytes |
| Header-declared message length | 8,496,669 bytes | 8,496,669 bytes |
| Actual size minus declared length | 4,470,615 bytes | 4,470,615 bytes |
| Four bytes at declared boundary | `00 00 98 00` | `08 00 08 00` |
| Final four bytes | `7777` | `7777` |
| GRIB signatures in member | 1 | 1 |
| `7777` end markers in member | 1 | 1 |

The recorded diagnostics report one GRIB message per member. ecCodes parsed one message for each member and reported a message length of **12,967,284 bytes**, equal to each actual uncompressed member size.

Successful ecCodes parsing does not resolve or validate the raw GRIB1 header-length discrepancy: the header field still declares 8,496,669 bytes, while the member and parser-reported message length are 12,967,284 bytes. The bytes at the declared boundary are not the end marker; both members end with `7777`.

The ZIP archive passed its recorded archive-integrity checks. Archive-level integrity and the internal GRIB1 message-length consistency are separate checks; passing the former does not settle the latter.

## Assessment and limits

The internal discrepancy is confirmed by the existing raw-byte diagnostic and manifest metadata. **Its cause remains unknown.** This report does not claim the members are definitely corrupt, does not identify a publisher-side defect, and does not infer a repair.

Publisher clarification is required. Until clarified, preserve the original archive and do not silently repair or rely on these members as trusted production inputs.

## Related existing records

- `AGROSENSE_ERA5_LAND_GRIB1_HEADER_DIAGNOSTIC_ADDENDUM_2026-11-23.md`
- `AGROSENSE_ERA5_LAND_HISTORICAL_ACQUISITION_RECONCILIATION.md`
- `data/metadata/era5_land_download_manifest.json`
- `data/metadata/era5_land_quality_report.json`

This is a technical evidence report only. It grants or implies no project-owner authorization, external permission, research or pilot approval, commercial-use approval, redistribution right, or ML-training eligibility.
