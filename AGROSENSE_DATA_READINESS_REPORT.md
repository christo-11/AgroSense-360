# AgroSense-360 Kerala Agricultural Data Readiness Report

## Executive decision

**Kerala crop suitability and ML training are not ready.** The repository contains useful catalogue identifiers, data-governance metadata, and a read-only data-intelligence implementation, but it does not contain evidence-backed crop requirements, verified district/crop relationships, sufficient Kerala weather observations, or a dataset cleared for training.

This assessment uses the migration seed and existing repository documentation. The local API was unavailable, so live database values were not rechecked. The repository migration head is `5d3cbf283629`; the previously recorded Stage 16 database/API snapshot is historical evidence, not a fresh Stage 18 connectivity result.

## Readiness by dimension

| Dimension | Status | Evidence and explanation | Next evidence/action |
| --- | --- | --- | --- |
| Catalogue completeness | **PARTIAL — identifiers only** | Migration seeds 14 district names, 4 crop categories, 31 crops, and 31 empty `pending` profiles. The previous live snapshot recorded 0 verified profiles, 0 varieties, and 0 district/crop suitability rows. Live counts were not re-read now. | Recheck the live catalogue when the local backend/database is available; distinguish row existence from field completeness and verification. |
| Agricultural evidence quality | **NOT READY** | Seeded profiles have no soil, temperature, rainfall, season, yield, or source claims. No verified variety or district/crop evidence is present in the seed. Current source inventory records candidate data sources, not claim-level references. | Collect attributable crop/variety evidence; store source/version/method at claim level; review each field independently. |
| Geographic coverage | **PARTIAL / NOT SUITABILITY-READY** | District catalogue names exist, but the migration defines no district boundary geometries or boundary version, and seeds no district/crop associations. Many candidate sources do not establish Kerala district coverage. | Obtain a licensed, versioned Kerala boundary source; verify source coverage and spatial support; do not infer relationships from names or state-level coverage. |
| Weather-data quality | **REJECTED FOR TRAINING / INCOMPLETE FOR USE** | Two existing ERA5-Land archives have sparse, irregular temporal evidence and are marked `NEEDS_MORE_DATA` / `REJECT_FOR_TRAINING`. No Kerala-specific district coverage validation or independent gauge/station comparison is documented. | Keep these archives excluded from training; resolve request/product provenance and acquire adequate data only after quality criteria and permissions are approved. |
| License eligibility | **MIXED / NOT READY** | Inventory: 13 candidates; 3 carry the internal `APPROVED_PORTFOLIO_RESEARCH_ONLY` licence/terms classification, 2 are conditional, 1 blocked, and 7 unverified at portfolio level. Commercial review: 11 conditional, 2 blocked, 0 approved. The internal classification is not project-owner authorization or source-owner permission and does not authorize access, acquisition, research, demonstration, ML training, redistribution, or deployment. | Resolve exact resource terms, attribution, intended use, redistribution, and any commercial restrictions; obtain separate project authorization and applicable source-owner rights before activity. |
| Training eligibility | **NOT ELIGIBLE — 0 sources** | Existing governance snapshot and Stage 17 report record zero eligible sources; current weather archives are explicitly rejected for training. No reviewed evidence supports changing this gate. | Require licensed/versioned data, complete provenance, task-specific quality checks, independent evaluation, and recorded approval before reconsidering. |

## Available evidence versus missing evidence

### Available in the repository

- A seeded catalogue of Kerala district names and crop/category names.
- Relational models and endpoints for crop profiles, varieties, source records, and district/crop relationships.
- Source inventory metadata and prior licensing/governance assessments.
- Two ERA5-Land acquisition records with quality reports that reject both archives for training.
- Read-only data-intelligence endpoints and dashboard documentation from prior stages.

### Not established by current evidence

- That every catalogue crop is grown in every district, or any particular district/crop suitability relationship.
- Any verified crop variety, crop soil/climate requirement, season, pest/disease prevalence, or yield value.
- A Kerala geospatial boundary dataset or validated district-level weather-cell coverage.
- Continuous, quality-controlled, independent Kerala weather observations.
- Kerala district/year production/yield labels with verified schema, units, and license.
- Local plot-linked soil lab data or disease images with verified labels and rights.
- Any source currently approved for ML training or commercial use.

The detailed crop matrix and source assessment are in [AGROSENSE_KERALA_CROP_DATA_AUDIT.md](./AGROSENSE_KERALA_CROP_DATA_AUDIT.md). Weather acceptance gates are in [AGROSENSE_WEATHER_QUALITY_SPECIFICATION.md](./AGROSENSE_WEATHER_QUALITY_SPECIFICATION.md).

## Validation and architecture findings

### Existing safeguards

- Crop profile ranges are checked; status fields use constrained values.
- A profile/variety/district-crop record marked verified requires a source reference.
- Verified district/crop links cannot remain `under_review`.
- Variety-to-crop and district/crop/variety relationships are constrained.
- The Stage 17 data-intelligence training gate remains fail-closed for current evidence.

### Gaps to resolve before the catalogue can support agricultural claims

1. Profile verification requires at least one sourced claim, not a complete profile. Verification and completeness are different dimensions; the dashboard/report must not interpret `verified` as “all agronomic fields complete.”
2. Sources are linked to a whole profile or relationship, not individual assertions. Contradictions, methods, scope, validity dates, and confidence cannot be traced to a particular value.
3. The current source model does not capture a full versioned dataset manifest, immutable file checksum, terms snapshot, attribution text, method, or rights-decision history.
4. District records do not include boundary geometry/version; district-name joins cannot establish spatial suitability.
5. A pending or absent district/crop association must remain unknown, not be rendered as unsuitable or suitable.

The current model is adequate for empty/pending catalogue records and conservative data display. No migration is justified for this readiness audit. A future schema proposal is documented in the crop data audit; introduce changes only when evidence ingestion requirements and claim-level verification policy are agreed.

## Potential technical demonstration boundary (not authorization)

The technically supportable product concept, if separately authorized, is a **catalogue and evidence-readiness dashboard**. Technical readiness does not grant permission to access or acquire data, conduct research, demonstrate publicly, train, redistribute, or deploy. Publisher-term compatibility and source availability do not replace project-owner authorization or applicable source-owner permission. Current project use scopes remain **NOT AUTHORIZED**.

1. Load district and crop names from the existing API.
2. Show that crop profiles are pending/incomplete and no verified district/crop suitability is recorded.
3. Present the ERA5-Land acquisition and quality state with the explicit training rejection.
4. Explain missing evidence and source/license gates.
5. Avoid crop recommendations, yield forecasts, disease predictions, or synthetic agricultural facts.

This is useful and honest, but it is not an agricultural intelligence prediction workflow. No fallback prediction should be fabricated to make a demonstration appear complete.

## Priority next actions

### Critical

1. **Keep ML training and recommendation outputs disabled** for the current weather archives and catalogue records. Dependency: none. Effort: immediate.
2. **Verify live catalogue/database state** once the local API/database is available; record actual counts and whether profile fields/source relationships differ from the migration seed. Dependency: backend/database availability. Effort: 0.5–1 hour.
3. **Approve a claim-level verification and completeness policy** so a sourced partial profile is not mistaken for a complete one. Dependency: agricultural domain reviewer. Effort: 2–4 hours for policy and acceptance cases.

### High

4. **Select one pilot crop, district, season, and question** before sourcing data. Dependency: product/domain owner. Effort: 1–2 hours.
5. **Resolve source rights and provenance for that pilot** (version, license, attribution, intended-use permission, geographic and temporal coverage). Dependency: selected source and rights review. Effort: 0.5–2 days.
6. **Obtain independently validated, continuous weather evidence** and apply the acceptance specification; keep the two existing archives rejected. Dependency: pilot scope, lawful source, station/gauge evidence. Effort: several days or longer depending on access.
7. **Obtain attributable crop guidance and local production/soil evidence** with units, methods, dates, and geography. Dependency: authorized publisher/lab or government resource access. Effort: several days to weeks.

### Medium

8. **Version district boundary geometry and build auditable spatial joins.** Dependency: licensed boundary source and chosen source resolution. Effort: 1–3 days.
9. **Implement normalized claim-level evidence and completeness tracking only after policy approval.** Dependency: approved schema and review workflow. Effort: 2–5 days, including tests and migration planning.
10. **Add ingestion validation and immutable manifests for the selected pilot source.** Dependency: rights and data contract. Effort: 1–3 days.

### Future

11. **Evaluate a baseline model only after data gates pass**, using spatial and temporal holdouts and a documented independent test set. Dependency: approved dataset, sufficient observations/labels, reviewer sign-off. Effort: estimate after data volume and task are known.
12. **Enable inference or recommendations only after external/domain validation and operational monitoring**; retain provenance and user-facing uncertainty. Dependency: validated model and product safety review. Effort: estimate after model evaluation.

## Verification scope and limitations

- Inspected the seeded migration, ORM models, crop schemas/routes/tests, source inventory, and existing data-intelligence/licensing reports.
- Expanded catalogue tests to assert that empty profiles remain pending with agronomic values unknown, invalid source IDs are rejected, and an unverified district/crop relationship remains explicitly pending/under review.
- Backend suite: project virtual environment, pytest `-q` from `backend/` (invoked through an inline launcher to disable Pydantic `.env` loading) — **52 passed**. Tests used the fixture's in-memory SQLite database. A system-Python attempt could not import `geoalchemy2`; rerunning with the project environment passed.
- A read-only local API GET probe failed because the backend was unavailable; live database/API connectivity was not verified. Historical Stage 16 catalogue counts are labeled as historical throughout.
- No query, write, or migration was performed against the configured project database; the backend tests used only their ephemeral in-memory SQLite fixture. The local API probe did not return a response. No source approval, license, or historical acquisition record was changed.
- No datasets were downloaded, no external API requests were made, no model was trained, and no credentials or secret files were accessed.

## Recommended next stage

**Stage 19 — Evidence-backed pilot dataset curation.** Select one crop/district/season and define the intended question. Secure the required rights, collect or access a small authorized sample, preserve source/version/method/unit provenance, and validate it against the weather and crop-evidence acceptance gates before any model training is proposed.
