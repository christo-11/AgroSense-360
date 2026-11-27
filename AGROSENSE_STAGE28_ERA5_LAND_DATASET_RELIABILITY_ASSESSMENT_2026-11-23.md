# AgroSense-360 Stage 28 — ERA5-Land Dataset Reliability and Production-Use Assessment

**Assessment date:** 23 November 2026  
**Scope:** Existing ERA5-Land archives only; assessment from the six specified records. No archive was read, downloaded, reprocessed, or modified for this stage.

## Executive decision

| Archive | Technical status | Production weather input | Local agricultural decision support | Model training |
|---|---|---|---|---|
| `era5_land_request_1.zip` | **ACCEPTABLE WITH LIMITATIONS** | Not suitable as a production input | Not suitable as a stand-alone/local decision input | Not suitable |
| `era5_land_request_2.zip` | **REJECTED** | Not suitable | Not suitable | Not suitable |

These are technical reliability assessments, not dataset-use approvals. Neither archive is approved for production, research, pilot, commercial, redistribution, or ML-training use. Stage 23 restrictions remain unchanged.

## Evidence basis and interpretation

The manifest and quality report record valid ZIP structure/CRC and matching archive SHA-256 values for both archives. These establish archive-level integrity, not the validity or scientific suitability of every internal data message.

ERA5-Land is a land-surface reanalysis product. Its values are reanalysis estimates, not direct ground observations at the grid cells. No local station validation is documented in the inspected records.

The global grid is recorded as regular latitude/longitude at 0.1-degree spacing, with bounds from -90 to 90 degrees latitude and 0 to 359.9 degrees longitude. It intersects Kerala, but no Kerala administrative polygon or per-cell Kerala-only mask was applied. Reported global missing fractions therefore cannot be treated as Kerala-specific missingness.

Historical retrieval timestamps, successful receipts, matching content, and checksums document acquisition provenance only. They do not establish authorization to use the archives. The receipt-to-archive association is content-based; a direct mapping from receipt UUID to manifest object-store reference is not established. The exact product version is unpinned, and the original request-history MHT was not independently inspected.

## Archive 1 — `era5_land_request_1.zip`

### Recorded technical evidence

- **Format:** ZIP containing NetCDF-4/HDF5 files and one NetCDF classic 64-bit-offset member.
- **Archive integrity:** ZIP format valid; CRC passed; recorded SHA-256 matches the manifest: `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441`.
- **Temporal coverage:** Two dynamic timestamps only, 2024-01-03 03:00 and 06:00 UTC. This is a three-hour span, not a continuous weather series.
- **Variables:** The quality report identifies 37 main data variables. Recorded examples include 2 m temperature (`t2m`), total precipitation (`tp`), 10 m wind components (`u10`, `v10`), surface/soil-water and other land-surface variables. The archive also contains ancillary/static fields.
- **Missing values:** The complete-scan summary reports 8,541,474 missing values of 12,967,200 per main variable (fraction 0.6586984), with a shared global NaN pattern consistent with an ocean/land mask. No Kerala-cell-specific validity count is recorded.
- **Spatial coverage:** Global 0.1-degree grid intersecting Kerala; no Kerala-only mask or local cell validation.
- **Format limitations:** No internal NetCDF error is reported in the quality assessment, but mixed NetCDF variants and the single CDF2 member should be handled according to the recorded per-file metadata.
- **Provenance:** Manifest request metadata and receipt are recorded, but the exact product version is unpinned and the original MHT was not independently inspected. Retrieval predates Stage 23 records; this chronology does not establish prior authorization.

### Status rationale

**ACCEPTABLE WITH LIMITATIONS** means the available records support archive-level integrity and do not identify an internal NetCDF defect for this archive. It does not mean the data are complete, locally validated, continuous, authorized, or production-ready. Two timestamps cannot characterize weather over a growing season or support ongoing operational inputs.

### Use assessment

- **Production weather inputs:** No. Coverage is too sparse, and no operational or local validation is documented.
- **Local agricultural decision support:** No, not as a decision-making input. It could only be considered for limited retrospective technical inspection after separate authorization and local validation; this assessment does not authorize that use.
- **Model training:** No. The quality report marks training `REJECT_FOR_TRAINING`; the sample is sparse, missingness is global rather than Kerala-qualified, and no authorized target labels or training permission are established.

### Evidence needed to reconsider

- A sufficiently continuous, purpose-appropriate time series with exact request parameters and a pinned product version.
- Kerala-specific spatial selection and per-cell missingness/validity assessment.
- Independent comparison against suitable local observations and documented variable/unit checks.
- Separate documented project-owner approval and review of applicable source terms for each proposed use.
- For any training proposal, adequate authorized labels, training permission, and a fit-for-purpose validation design.

## Archive 2 — `era5_land_request_2.zip`

### Recorded technical evidence

- **Format:** ZIP containing GRIB editions 1 and 2; 609 messages were parsed by ecCodes according to the quality report.
- **Archive integrity:** ZIP format valid; CRC passed; recorded SHA-256 matches the manifest: `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0`.
- **Temporal coverage:** Fifty dynamic variables have 12 timestamps each between 2011-01-11 13:00 and 2011-01-29 22:00 UTC, on four days, with irregular observed gaps. Nine singleton ancillary records do not make a continuous series. The broader metadata span of 1995–2025 includes ancillary/static records and is not the dynamic time-series coverage.
- **Variables:** The recorded dynamic inventory includes 2 m temperature (`2t`), 2 m dewpoint (`2d`), 10 m wind components (`10u`, `10v`), precipitation (`tp`), soil temperatures (`stl1`–`stl4`), soil-water fields (`swvl1`–`swvl4`), and other surface variables. Variable presence does not establish continuity or local validity.
- **Missing values:** The quality report records marker `9999` and a global dynamic missing fraction of approximately 0.6586984 per message. Counts vary; the report attributes the shared global pattern as likely ocean/land masking, not a Kerala-specific result.
- **Spatial coverage:** Same global 0.1-degree grid and Kerala intersection limitation described above; no Kerala-specific mask or per-cell validation.
- **GRIB parsing and message boundaries:** ecCodes parsed all 609 messages and reported end markers. Most members have no declared-length mismatch; `clake.grib`, `lsm.grib`, and `slt.grib` each have 44 trailing zero-padding bytes after a valid message end, recorded separately from the affected inconsistency.
- **Unresolved GRIB1 inconsistency:** `tvh.grib` and `tvl.grib` each have an actual uncompressed member size of 12,967,284 bytes, while the GRIB1 header declares 8,496,669 bytes (difference 4,470,615 bytes). Both end in `7777`. ecCodes accepts each when given the actual member bytes, but this parser success does not resolve or demonstrate conformance of the raw GRIB1 length field. The cause remains unknown.
- **Provenance:** The request reference and receipt UUID are recorded as content-correlated, not directly identifier-mapped. Exact product version is unpinned; the original request-history MHT was not independently inspected. Retrieval evidence does not establish authorization.

### Status rationale

**REJECTED** for reliability-dependent use pending resolution of the raw GRIB1 header-length inconsistency. This is not a claim that the ZIP is corrupt or that every contained field is invalid: ZIP integrity passed and ecCodes parsed the messages. It is a fail-closed technical disposition because two internal messages have a confirmed, unexplained header-length mismatch and the dynamic coverage is also sparse and discontinuous.

### Use assessment

- **Production weather inputs:** No. The unresolved internal GRIB1 inconsistency and sparse, irregular temporal sampling make the archive unsuitable as a trusted production input.
- **Local agricultural decision support:** No. The affected members are not reliable production inputs; global coverage, missingness, temporal gaps, and absence of local validation also preclude treating the archive as local advice.
- **Model training:** No. The quality report marks training `REJECT_FOR_TRAINING`; the internal message-length issue is unresolved, temporal coverage is inadequate for a continuous series, and no use or training permission is established.

### Evidence needed to reconsider

- A publisher technical clarification that addresses the `tvh.grib`/`tvl.grib` header-length discrepancy, or corrected files supplied through an authorized process.
- If replacement files are supplied, new checksum/provenance records and a repeat of raw header, message-boundary, parsing, and archive-integrity checks before reconsideration.
- Exact pinned product version and verified request parameters; clarify the dynamic period and variable selection.
- Kerala-specific spatial and missingness checks, and independent comparison with suitable local observations.
- Separate documented project-owner and applicable source/licence approvals for any proposed use.

The Stage 27 tracker records the inquiry as **NOT SUBMITTED**, owner approval as **NOT RECORDED**, and technical clarification as **PENDING**. No publisher response or corrected file is available in the evidence reviewed for this assessment.

## Cross-cutting limitations and non-authorization

1. **ZIP integrity is not GRIB conformance.** ZIP CRC and SHA-256 matching establish archive integrity relative to recorded bytes; they do not prove each internal message is valid.
2. **ecCodes parsing is not raw-header conformance.** Parser acceptance of the actual member bytes does not make the `tvh.grib`/`tvl.grib` declared lengths consistent.
3. **Reanalysis is not ground truth.** ERA5-Land values are reanalysis estimates, not direct measurements at a farm, district, or grid cell.
4. **Coverage is not authorization.** Historical acquisition evidence, receipts, and CC-BY references do not themselves grant project-owner approval or permission for research, pilot, production, commercial, redistribution, or ML-training use.
5. **No production approval is made.** The classifications above are technical reliability statuses only. Stage 23 authorization and dataset-use statuses are unchanged.

## Overall conclusion

Neither archive is suitable for production weather inputs, local agricultural decision support, or model training on the evidence currently recorded. Request 1 is **ACCEPTABLE WITH LIMITATIONS** as an intact but extremely sparse NetCDF acquisition; request 2 is **REJECTED** pending publisher clarification or correction of its unresolved GRIB1 header-length inconsistency. Neither classification authorizes use.
