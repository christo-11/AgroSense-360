# AgroSense-360 — Project-Owner Decision Record

**Record date:** 2026-11-23  
**Record status:** PENDING — for completion by the project owner  
**Purpose:** Capture the project owner's explicit, scoped decisions identified in [Stage 39](./AGROSENSE_PROJECT_OWNER_GOVERNANCE_REVIEW_2026-11-23.md).  
**Important:** This record captures the project-owner instruction supplied for this update: PO-01 through PO-08 remain **NO AUTHORIZATION**. The instruction is recorded as provided and has not been independently verified. Formal record status remains PENDING until the required attestation and review fields are completed. Previous discussions, licences, public access, and technical findings do not grant authorization.

## 1. Outstanding decision register

The decision-record status remains **PENDING** for every entry. The supplied owner instruction is recorded as **NO AUTHORIZATION** for each permission; this does not complete the formal attestation or independent review. No positive authorization is inferred.

### Decision 1 — Set governance scope: PO-01 through PO-08

| Permission | Existing authorization status | Decision-record status | Project-owner instruction (not independently verified) | Scope / conditions / evidence reference |
|---|---|---|---|---|
| PO-01 — Prepare or revise draft inquiries | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-02 — Send inquiry to named source owner | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-03 — Receive, store, and review responses | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-04 — Download/retrieve exact public dataset | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-05 — Acquire restricted dataset after written permission | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-06 — Use acquired data for pilot research | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-07 — Use acquired data for ML training | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |
| PO-08 — Commercial use or redistribution | NOT AUTHORIZED | PENDING | **NO AUTHORIZATION** | ____________________ |

### Prioritized decisions from Stage 39

| # | Decision requiring owner review | Current decision status | Project-owner instruction / decision state | Scope, conditions, evidence, and reviewer |
|---|---|---|---|---|
| 1 | Set governance scope by deciding PO-01 to PO-08 individually. | **PENDING** | **NO AUTHORIZATION** for PO-01 through PO-08 | Instruction recorded; formal attestation remains pending. |
| 2 | Decide whether to authorize submission of the existing Copernicus inquiry (PO-02), and separately decide whether to receive/store/review a response (PO-03). | **PENDING** | **NO AUTHORIZATION**; inquiry remains NOT SUBMITTED | Named submitter, verified channel, exact message/attachments, response location: ____________________ |
| 3 | Decide whether to pursue any exact public resource (PO-04) or restricted resource (PO-05), only after terms, permissions, version, geography, time period, and purpose are identified. | **PENDING** | **NO AUTHORIZATION** to download or acquire | Resource/version/purpose/scope: ____________________ |
| 4 | Decide whether to authorize any specified acquired dataset for pilot research (PO-06), subject to terms, quality, provenance, and crop/geographic relevance. | **PENDING** | **NO AUTHORIZATION** for pilot research | Dataset, purpose, geography, period, conditions: ____________________ |
| 5 | Decide whether to authorize any specified dataset for ML training (PO-07), subject to explicit training rights, verified targets, quality/relevance, and governance review. | **PENDING** | **NO AUTHORIZATION** for ML training | Dataset, task, labels, population, conditions: ____________________ |
| 6 | Decide commercial use and redistribution separately (PO-08), based on exact-resource rights and third-party restrictions. | **PENDING** | **NO AUTHORIZATION** for commercial use or redistribution | Resource, use, recipients, outputs, conditions: ____________________ |
| 7 | Set the evidence threshold for Idukki, including cultivation/variety/season, district-boundary, weather-validation, and target-label evidence. | **PENDING** | No threshold decision supplied; remains pending | Required evidence and reviewer: ____________________ |
| 8 | Decide the technical path for ERA5-Land request 2 after any authorized inquiry yields a real response/corrected files, or decide to exclude the archive. | **PENDING** | No technical disposition supplied; inquiry submission has **NO AUTHORIZATION** | No response/correction is currently recorded. Proposed technical review scope: ____________________ |

## 2. Scope of any proposed authorization

The supplied instruction is **NOT AUTHORIZED** for each use scope. The formal decision-record status remains **PENDING**. No proposed scope is approved. Dataset permission from an external owner is tracked separately below.

| Use scope | Current project authorization | Decision-record status | Proposed resource/version, purpose, geography, and time period | Conditions / attribution / restrictions | Project-owner instruction (not independently verified) |
|---|---|---|---|---|---|
| Portfolio/demo use | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |
| Pilot research | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |
| ML training | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |
| Commercial use | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |
| Redistribution | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |
| Production and deployment | **NOT AUTHORIZED** | PENDING | ____________________ | ____________________ | **NOT AUTHORIZED** |

No use scope inherits approval from another. In particular, portfolio/demo or pilot-research status does not authorize ML training, commercial use, redistribution, production, or deployment.

## 3. External dataset permission record

**Overall source-owner permission status:** **NOT RECEIVED / NOT RECORDED**.  
**Project-owner authorization status:** **PENDING**; supplied instruction is **NO AUTHORIZATION** for PO-01 through PO-08.  
**External inquiry status:** Copernicus inquiry **NOT SUBMITTED**; owner instruction is **NO AUTHORIZATION** to submit; formal attestation remains pending.  
**External technical response/corrected files:** **NOT RECEIVED**.

Record each source-owner response separately only after it is actually received and reviewed:

| Source owner / exact resource | Official channel and evidence reference | Permission scope and applicable terms | Response date / reviewer | Permission status |
|---|---|---|---|---|
| ____________________ | ____________________ | ____________________ | ____________________ | NOT RECEIVED |

A publisher's technical clarification is not legal permission. A licence statement or publicly accessible resource does not, by itself, record project-owner authorization or establish all dataset-specific rights.

## 4. ERA5-Land restrictions and Copernicus clarification

| Archive | Existing technical status and limitations | Current use status |
|---|---|---|
| `era5_land_request_1.zip` | **ACCEPTABLE WITH LIMITATIONS**; two dynamic timestamps (2024-01-03 03:00 and 06:00 UTC); approximately 65.87% global missingness as reported; no Kerala-specific mask or local station validation. | Not approved for production weather, local agricultural decision support, or ML training. No use authorization recorded. |
| `era5_land_request_2.zip` | **REJECTED** pending clarification. `tvh.grib` and `tvl.grib` each have an actual member size of 12,967,284 bytes versus the GRIB1 declared length of 8,496,669 bytes (difference 4,470,615 bytes). ecCodes parsing and ZIP integrity do not resolve raw header conformance. | Not approved for production weather, local agricultural decision support, or ML training. No use authorization recorded. |

**Copernicus GRIB1 clarification:** **PENDING**. The inquiry remains **NOT SUBMITTED**; no publisher explanation, conformance confirmation, known-issue finding, or corrected file is recorded. Any inquiry submission requires explicit project-owner authorization first. A response or corrected file would require separate technical review and would not grant data-use permission.

## 5. Black-pepper labels, ML, and Idukki evidence requirements

**Verified black-pepper target labels:** None established in the reviewed evidence. No verified Idukki yield, disease, soil laboratory, expert suitability, crop-stage, or weather-impact target set is recorded. No class balance or model performance can therefore be assessed. Weather reanalysis/satellite estimates are not crop outcome labels or direct ground observations.

**ML status:** **NOT READY / BLOCKED**. No source is approved for training; there is no authorized training dataset, validated target dataset, locked test set, model evaluation, or deployed validated model. Training remains unauthorized.

**Idukki status:** **PROVISIONAL**. Evidence to resolve includes authoritative black-pepper cultivation, variety and season records; suitable district-boundary and spatial validation; representative local weather observations and independent validation; and verified crop-specific outcomes/labels with source rights and provenance.

## 6. Project-owner attestation fields

Complete only when the project owner makes a decision. These fields are intentionally blank.

- **Project-owner name:** ______________________________________________
- **Decision date (include timezone if relevant):** ________________________
- **Signature or approved equivalent:** __________________________________
- **Decision IDs / permission scopes addressed:** _________________________
- **Conditions and limitations:** ________________________________________
- **Evidence location/reference:** _______________________________________
- **Independent reviewer and review date:** ______________________________

**Instruction source:** Project-owner instruction supplied for this update. No owner name, signature, independent reviewer, or attestation date was supplied; those fields remain blank. No independent verification is claimed.

Until attestation and review are completed through the applicable governance process, this record remains **PENDING**. The recorded owner instruction is **NO AUTHORIZATION** for PO-01 through PO-08 and the six use scopes above.

## Evidence references

- [Stage 39 Project-Owner Governance Review](./AGROSENSE_PROJECT_OWNER_GOVERNANCE_REVIEW_2026-11-23.md)
- [Stage 23 Project-Owner Approval](./AGROSENSE_STAGE23_PROJECT_OWNER_APPROVAL.md)
- [Stage 23 Authorization Matrix](./AGROSENSE_STAGE23_AUTHORIZATION_MATRIX.md)
- [Stage 23 Permission-Response Log](./AGROSENSE_STAGE23_PERMISSION_RESPONSE_LOG.md)
- [Stage 23 Final Decision](./AGROSENSE_STAGE23_FINAL_DECISION.md)
- [Stage 27 Copernicus Inquiry Response Tracker](./AGROSENSE_STAGE27_COPERNICUS_INQUIRY_RESPONSE_TRACKER_2026-11-23.md)
- [Stage 28 ERA5-Land Reliability Assessment](./AGROSENSE_STAGE28_ERA5_LAND_DATASET_RELIABILITY_ASSESSMENT_2026-11-23.md)
- [Stage 30 Dataset Licensing and Provenance Matrix](./AGROSENSE_STAGE30_DATASET_LICENSING_AND_PROVENANCE_MATRIX.md)
- [Stage 33 Agricultural Feature Engineering](./AGROSENSE_STAGE33_AGRICULTURAL_FEATURE_ENGINEERING.md)
- [Stage 35 ML Readiness Assessment](./AGROSENSE_STAGE35_ML_READINESS_ASSESSMENT.md)
- [Stage 38 Production Readiness Report](./AGROSENSE_STAGE38_PRODUCTION_READINESS_REPORT.md)
