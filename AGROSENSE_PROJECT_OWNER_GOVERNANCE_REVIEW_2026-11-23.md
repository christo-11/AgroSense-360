# AgroSense-360 — Project-Owner Governance Review

**Review date:** 2026-11-23  
**Purpose:** Summarize current authorization boundaries and decisions awaiting the project owner.  
**Status:** Review only. This document records no approval, permission, or status change.

## Current governance status

Stage 23 records project-owner authorization as **PENDING**. Each permission PO-01 through PO-08 is **NOT AUTHORIZED**; no decision owner signature or equivalent approval evidence is recorded. The source-owner response log has no received permissions. Creating this review does not grant authorization. See [Stage 23 project-owner approval](./AGROSENSE_STAGE23_PROJECT_OWNER_APPROVAL.md), [authorization matrix](./AGROSENSE_STAGE23_AUTHORIZATION_MATRIX.md), [permission-response log](./AGROSENSE_STAGE23_PERMISSION_RESPONSE_LOG.md), and [final decision](./AGROSENSE_STAGE23_FINAL_DECISION.md).

## Outstanding authorization and external permissions

Project-owner decisions must be made separately for:

1. Preparing/revising draft inquiries (PO-01).
2. Sending an inquiry to a named, verified source owner (PO-02).
3. Receiving, storing and reviewing responses (PO-03).
4. Downloading an exact publicly accessible dataset (PO-04).
5. Acquiring restricted data after written source-owner authorization (PO-05).
6. Using a specified acquired dataset for pilot research (PO-06).
7. Using a specified dataset for ML training (PO-07).
8. Commercial use or redistribution (PO-08).

None is currently permitted. A licence or public access does not substitute for project-owner authorization; research approval would not by itself authorize training, commercial use, or redistribution. Exact-resource terms and third-party rights remain unresolved for multiple source candidates. See the [Stage 30 licensing and provenance matrix](./AGROSENSE_STAGE30_DATASET_LICENSING_AND_PROVENANCE_MATRIX.md) and [Stage 29 alternative weather-source assessment](./AGROSENSE_STAGE29_ALTERNATIVE_WEATHER_SOURCE_ASSESSMENT.md).

No source-owner permission response is recorded. The Copernicus technical inquiry is **NOT SUBMITTED**; owner approval is **NOT RECORDED**; no response, ticket/reference, corrected file, or technical clarification has been received. Sending an inquiry, if later separately authorized, would not itself grant data-use permission. See the [Stage 27 response tracker](./AGROSENSE_STAGE27_COPERNICUS_INQUIRY_RESPONSE_TRACKER_2026-11-23.md).

## ERA5-Land restrictions and unresolved technical clarification

| Archive | Existing technical finding | Current use boundary |
|---|---|---|
| `era5_land_request_1.zip` | **ACCEPTABLE WITH LIMITATIONS**; two dynamic timestamps (2024-01-03 03:00 and 06:00 UTC), approximately 65.87% global missingness as reported, and no Kerala-specific mask or local station validation. | Not suitable for production weather, local agricultural decision support, or training; not approved for use. |
| `era5_land_request_2.zip` | **REJECTED** pending clarification. `tvh.grib` and `tvl.grib` each have a 12,967,284-byte member while the GRIB1 header declares 8,496,669 bytes (difference 4,470,615 bytes). ecCodes parsing and ZIP integrity do not resolve raw header conformance. | Not suitable for production, local decision support, or training; not approved for use. Do not treat parser success as publisher confirmation. |

These are technical reliability dispositions, not use permissions. The unresolved request 2 question is whether the publisher can explain the GRIB1 length discrepancy, confirm conformance, identify any known encoding/processing issue, or supply corrected files. No explanation or correction is in evidence. See [Stage 28 reliability assessment](./AGROSENSE_STAGE28_ERA5_LAND_DATASET_RELIABILITY_ASSESSMENT_2026-11-23.md), [Stage 31 weather architecture](./AGROSENSE_STAGE31_WEATHER_DATA_ARCHITECTURE.md), and the [Stage 27 tracker](./AGROSENSE_STAGE27_COPERNICUS_INQUIRY_RESPONSE_TRACKER_2026-11-23.md).

## Black-pepper evidence, Idukki, and ML readiness

No verified black-pepper yield, disease, soil laboratory, expert suitability, crop-stage, or weather-impact target labels are established. Weather reanalysis/satellite estimates are not crop outcome labels or direct ground observations. Idukki remains **PROVISIONAL**: verified cultivation/variety/season evidence, representative local observations, authoritative spatial validation, and applicable source rights are still needed.

ML readiness is **NOT READY / BLOCKED**. There is no authorized training source, validated target dataset, assessable class balance, locked test set, model evaluation, or deployed validated model. Candidate features and validation methods remain designs; no training is authorized. See [Stage 33 feature design](./AGROSENSE_STAGE33_AGRICULTURAL_FEATURE_ENGINEERING.md), [Stage 35 ML readiness assessment](./AGROSENSE_STAGE35_ML_READINESS_ASSESSMENT.md), and [Stage 38 production readiness report](./AGROSENSE_STAGE38_PRODUCTION_READINESS_REPORT.md).

## Prioritized decisions for the project owner

These are decisions to consider and record with scope, date, conditions, reviewer, and evidence. They are **not approvals or recommendations to proceed automatically**.

1. **Set governance scope:** decide each of PO-01 to PO-08 individually. Record any denied, deferred, or approved scope explicitly; do not use blanket authorization.
2. **Decide whether an inquiry may be submitted:** specifically decide PO-02 for the existing Copernicus technical inquiry, including the verified official recipient/channel, exact wording/attachments, and named submitter. Separately decide PO-03 for receipt, secure storage, and review of any response. Until then, the inquiry remains unsubmitted.
3. **Decide whether to pursue any acquisition:** for each exact resource, decide PO-04 (public data) or PO-05 (restricted data) separately after verifying resource/version, terms, source-owner permission where needed, geography, period, and purpose. No source is currently acquisition-ready.
4. **Decide any pilot-research use:** if proposed, identify the exact data and purpose under PO-06 and require source terms, quality evidence, and black-pepper/Idukki relevance before changing status.
5. **Decide any ML-training use:** PO-07 requires explicit training scope and source-owner rights plus verified targets, quality/relevance, provenance, and signed governance review. No training can proceed on current evidence.
6. **Decide commercial use/redistribution separately:** PO-08 requires resource-specific commercial/redistribution and third-party-rights review; it does not follow from research or ML authorization.
7. **Set the evidence threshold for Idukki:** decide what authoritative cultivation/variety/season, district-boundary, weather-validation, and target-label evidence would be required before Idukki can leave provisional status or another geography is considered.
8. **Set the technical path for request 2:** after any inquiry is separately authorized and a real publisher response or corrected files exist, decide whether to commission a new technical review or exclude the archive. A response or replacement does not itself authorize use.

## Evidence references

- Authorization boundaries and decision record: [Stage 23 project-owner approval](./AGROSENSE_STAGE23_PROJECT_OWNER_APPROVAL.md), [Stage 23 authorization matrix](./AGROSENSE_STAGE23_AUTHORIZATION_MATRIX.md), [Stage 23 permission-response log](./AGROSENSE_STAGE23_PERMISSION_RESPONSE_LOG.md), [Stage 23 final decision](./AGROSENSE_STAGE23_FINAL_DECISION.md).
- Source terms and candidate limits: [Stage 29 alternative weather assessment](./AGROSENSE_STAGE29_ALTERNATIVE_WEATHER_SOURCE_ASSESSMENT.md), [Stage 30 licensing/provenance matrix](./AGROSENSE_STAGE30_DATASET_LICENSING_AND_PROVENANCE_MATRIX.md).
- Proposed controls, not approvals: [Stage 31 weather architecture](./AGROSENSE_STAGE31_WEATHER_DATA_ARCHITECTURE.md), [Stage 32 quality framework](./AGROSENSE_STAGE32_DATA_QUALITY_FRAMEWORK.md), [Stage 33 feature design](./AGROSENSE_STAGE33_AGRICULTURAL_FEATURE_ENGINEERING.md), [Stage 34 governance architecture](./AGROSENSE_STAGE34_DATA_GOVERNANCE_ARCHITECTURE.md), [Stage 36 integration plan](./AGROSENSE_STAGE36_SYSTEM_INTEGRATION_PLAN.md), [Stage 37 testing strategy](./AGROSENSE_STAGE37_TESTING_AND_VALIDATION_PLAN.md).
- Current data, ML and deployment findings: [Stage 27 Copernicus tracker](./AGROSENSE_STAGE27_COPERNICUS_INQUIRY_RESPONSE_TRACKER_2026-11-23.md), [Stage 28 ERA5-Land assessment](./AGROSENSE_STAGE28_ERA5_LAND_DATASET_RELIABILITY_ASSESSMENT_2026-11-23.md), [Stage 35 ML readiness assessment](./AGROSENSE_STAGE35_ML_READINESS_ASSESSMENT.md), [Stage 38 production readiness report](./AGROSENSE_STAGE38_PRODUCTION_READINESS_REPORT.md).

All referenced records describe the evidence available as of this review. Missing evidence remains missing; this document does not change any Stage 23 or Stage 29–38 status.
