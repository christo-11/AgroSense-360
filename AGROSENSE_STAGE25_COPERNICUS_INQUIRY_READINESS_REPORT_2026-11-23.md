# AgroSense-360 Stage 25 Copernicus Inquiry Readiness Report

**Review date:** 23 November 2026  
**Decision:** **READY FOR OWNER REVIEW**

This decision means only that the unsent technical inquiry is sufficiently accurate and professionally worded for project-owner review. It does not authorize sending it, contact Copernicus, or grant any research, pilot, commercial, redistribution or ML-training permission.

## Files reviewed

Only the five specified evidence files were inspected:

1. `AGROSENSE_COPERNICUS_GRIB1_TECHNICAL_EVIDENCE_2026-11-23.md`
2. `AGROSENSE_COPERNICUS_SUPPORT_INQUIRY_DRAFT_2026-11-23.md`
3. `AGROSENSE_ERA5_LAND_GRIB1_HEADER_DIAGNOSTIC_ADDENDUM_2026-11-23.md`
4. `data/metadata/era5_land_download_manifest.json`
5. `data/metadata/era5_land_quality_report.json`

## Technical accuracy and consistency

The inquiry accurately identifies the request 2 archive and the two affected members, `tvh.grib` and `tvl.grib`. Its key statements agree with the diagnostic addendum and the recorded manifest/quality evidence:

- GRIB edition 1; raw header starts `47 52 49 42 81 A6 1D 01`.
- Header declares 8,496,669 bytes; each uncompressed member is 12,967,284 bytes, a difference of 4,470,615 bytes.
- Bytes at the declared boundary are `00 00 98 00` for `tvh.grib` and `08 00 08 00` for `tvl.grib`.
- Both members end in `7777`; the diagnostic records one signature and one end marker per member.
- ecCodes parsed one message per member and reported 12,967,284 bytes.
- The ZIP's recorded integrity checks passed; this does not resolve internal GRIB1 header consistency.

The inquiry's request reference `7aa7a686527d3e900aa7b8dce4709fa6` agrees with the manifest. The related receipt UUID `4e1e2a12-1800-4983-80ea-4ab38a1fd5f4` is presented as separately recorded evidence; the technical evidence file correctly cautions that a direct identifier-level mapping to the manifest reference is not established.

Both archive checksums in the technical evidence file agree with the respective manifest records, and the quality report marks each checksum as matching the manifest:

| Archive | Request reference | Manifest SHA-256 | Recorded match |
|---|---|---|---|
| `era5_land_request_1.zip` | `24a5f33e75200171321741639baf695f` | `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441` | Yes |
| `era5_land_request_2.zip` | `7aa7a686527d3e900aa7b8dce4709fa6` | `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0` | Yes |

These are manifest/quality-report and evidence-document consistency checks; no new archive processing was performed for Stage 25.

## Inquiry coverage and wording

The draft is professional, states that it is seeking clarification, and does not claim that the files are definitely corrupt or that Copernicus has acknowledged the issue. It asks Copernicus to:

1. Confirm whether the discrepancy is expected.
2. Confirm GRIB1 validity and conformance.
3. Identify a known encoding, packaging or processing explanation.
4. Provide corrected versions if available.
5. Advise whether users should avoid relying on the members pending clarification.

It also requests a technical response and corrected files or the official procedure for obtaining them, if applicable.

## Evidence gaps / attachment guidance

The inquiry body does not include the archive SHA-256 or attach supporting files. This is not a technical blocker for owner review; include the existing evidence package when the owner later submits the inquiry.

### Submission evidence checklist

- [ ] Project-owner review and separate explicit authorization to send this exact inquiry to Copernicus CDS support.
- [ ] Final reviewed copy of `AGROSENSE_COPERNICUS_SUPPORT_INQUIRY_DRAFT_2026-11-23.md`.
- [ ] `AGROSENSE_COPERNICUS_GRIB1_TECHNICAL_EVIDENCE_2026-11-23.md`.
- [ ] `AGROSENSE_ERA5_LAND_GRIB1_HEADER_DIAGNOSTIC_ADDENDUM_2026-11-23.md`.
- [ ] Relevant manifest excerpt showing the request 2 reference, archive size, member names/sizes and recorded checksum.
- [ ] Relevant quality-report excerpt showing checksum/CRC status and the GRIB1/ecCodes findings.
- [ ] Preserve the distinction between manifest object-store reference `7aa7a686527d3e900aa7b8dce4709fa6` and receipt UUID `4e1e2a12-1800-4983-80ea-4ab38a1fd5f4`; the direct identifier-level mapping is not established.
- [ ] Do not attach the full archive by default; provide it only if the owner authorizes sharing and Copernicus requests it through an approved channel.

No recipient email address or contact endpoint was verified in these five files. The draft's team addressee is suitable for owner review, but the owner must verify the official support channel before any separately authorized submission.

## Outstanding controls

- The cause of the header-length discrepancy remains unknown.
- No Copernicus response or corrected file is available in the reviewed evidence.
- The inquiry has not been sent and no external party has been contacted.
- Existing source permissions and Stage 23 governance statuses remain unchanged.
- The members remain subject to the existing quality caution; this report does not authorize reliance on them or change any training decision.

## Final decision

**READY FOR OWNER REVIEW** as an unsent technical clarification draft. Before any submission, the project owner must review and separately authorize sending, and the official support contact channel must be verified. No acquisition or data-use authorization is granted by this report.
