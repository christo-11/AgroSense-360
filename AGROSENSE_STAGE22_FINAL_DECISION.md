# AgroSense-360 Stage 22 Final Decision

## Executive decision

**Acquisition permission gate:** NOT PASSED  
**Acquisition readiness:** NOT READY  
**Data pipeline implementation:** ARCHITECTURE ONLY  
**ML-training readiness:** NOT READY

Stage 22 prepared exact requirements, draft permission requests, an acquisition matrix and a future pipeline architecture. It did not acquire, download, request, ingest or approve any source.

## Data required

1. Idukki/black-pepper cultivation and administrative evidence.
2. District-level area, production and yield records.
3. Exact varieties and cultivation practices.
4. Measured soil observations with depth, method and lab/QC metadata.
5. Historical Idukki temperature and rainfall station observations.
6. Humidity and additional weather variables required by the approved scientific question.
7. Expert-confirmed crop disease/pest observations.
8. Versioned Idukki district boundaries and a stable spatial reference.

The final target variables and observation period remain unresolved until the project owner and scientific reviewer approve the research question.

## Organizations and data owners

Prepared request drafts address:

- Kerala Agricultural University.
- ICAR-Indian Institute of Spices Research.
- Kerala Department of Agriculture.
- Kerala Directorate of Economics and Statistics.
- India Meteorological Department.
- ISRIC/WoSIS.
- Government of India/data.gov.in and the relevant statistics owner.
- Kerala Soil Health Card/lab authorities.
- Idukki district administration or agricultural office, if exact records exist.

No organization was contacted and no draft was sent.

## Permissions missing

- Exact Idukki/black-pepper evidence and licence.
- District crop-production resource ID, schema, licence and API terms.
- Idukki soil sample owner and record-level reuse permission.
- IMD station export terms and exact release.
- ISRIC/WoSIS provider-specific terms for selected profiles.
- Commercial-use decisions for candidate sources.
- ML-training permission for every source.
- Signed governance approval and allowlisted reviewer.

Public or policy-level access is not permission for acquisition or ML training.

## Potentially usable sources

Potential but not currently acquisition-ready:

- ERA5-Land, if exact request/release, Kerala spatial validation and independent observations are supplied.
- GPM IMERG, if exact V07B asset, unit/scale metadata and gauge validation are retained.
- IMD station records, if an exact authorized export is identified.
- SoilGrids, only as a modeled covariate.
- WoSIS, only after provider-by-provider record terms and Idukki coverage are verified.
- Official crop-production data, if the exact crop/district/schema/licence is verified.

## Blocked or unresolved datasets

- FAOSTAT QCL: existing project status is blocked.
- Open-Meteo free API: existing commercial project status is blocked.
- Existing ERA5-Land archives: archive integrity exists but temporal/quality/training gates fail.
- PlantVillage/PlantDoc: rights and Kerala field relevance remain unresolved.
- KAU, data.gov.in, Soil Health Card and IMD exact exports: resource terms and records remain unresolved.

## Acquisition decision

**Acquisition cannot begin.**

Before any download or API request:

1. Project owner approves source-owner inquiries.
2. The exact source and use are documented.
3. Idukki/black-pepper evidence is retained or Idukki is replaced by an evidence-backed district.
4. Licence, attribution, redistribution, commercial and training decisions are explicit.
5. Resource version, schema and data quality criteria are approved.
6. A retrieval/provenance manifest is prepared.
7. The repository governance gate is ready to reject any unapproved source.

## Pipeline consistency

The Stage 22 pipeline architecture follows:

- Stage 19 normalized data contract and canonical units.
- Stage 20 source authorization boundaries.
- Stage 21 official/licence findings.
- Existing dataset-governance fail-closed behavior.
- Existing weather quality acceptance thresholds.

No database schema, ingestion code, migration or source record was created or changed.

## Validation

The Stage 22 documents were checked against the Stage 19–21 reports and source inventory.

Relevant tests to run at completion:

- `backend/tests/test_black_pepper_pilot_contract.py`
- `backend/tests/test_dataset_governance.py`

No source approval or inventory record was modified during Stage 22.

## Recommended Stage 23

**Stage 23 — Owner inquiry approval and acquisition decision gate**

Stage 23 should obtain explicit project-owner approval to send or prepare source-owner inquiries. It should not send emails or acquire data unless authorization is later granted and a separate acquisition stage is approved.

The Stage 23 outcomes should be:

- Final source-owner contact list.
- Prioritized exact resource requests.
- Completed permission/response log.
- Idukki evidence decision.
- Exact release/version and schema evidence.
- Signed acquisition decision for any approved resource.
- Updated source inventory only through the repository's protected review process.
