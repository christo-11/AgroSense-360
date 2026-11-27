# AgroSense-360 Stage 20 Decision Report

## Decision

**Acquisition readiness: NOT READY**

AgroSense-360 should not acquire, request or integrate a new dataset for the Idukki/black-pepper pilot. Source authorization remains unresolved for the required crop, district, soil and label evidence. Existing public availability or portfolio/research approval is not sufficient.

## Sources assessed

The Stage 20 review assessed 13 inventory entries:

- India district crop production statistics
- FAOSTAT QCL
- Kerala Agricultural University crop/weather information
- AGMARKNET daily mandi prices
- SoilGrids 2.0
- WoSIS profiles
- India Soil Health Card
- Sentinel-2 L2A
- ERA5-Land
- NASA GPM IMERG
- Open-Meteo historical weather
- PlantVillage
- PlantDoc

## Source decisions

### Requires user approval

- KAU crop/weather and publication evidence
- India district crop-production resource
- Soil Health Card/lab records
- AGMARKNET market data

### Conditional

- WoSIS profiles
- SoilGrids 2.0
- ERA5-Land
- NASA GPM IMERG
- Open-Meteo Historical Weather API
- Sentinel-2 L2A
- PlantVillage
- PlantDoc

### Blocked

- FAOSTAT QCL

### Approved for training

- **None**

The repository retains three sources classified as `APPROVED_PORTFOLIO_RESEARCH_ONLY`: ERA5-Land, NASA GPM IMERG and Open-Meteo. These classifications cover only the reviewed non-commercial portfolio scope and do not imply data quality, exact asset provenance, commercial permission or ML-training permission.

## Evidence gaps

1. No published or authoritative source establishes black-pepper cultivation or suitability for Idukki.
2. No source-backed scientific-name, variety, season or agronomic requirement record is available.
3. No authorized, georeferenced, depth/method-documented soil observations exist.
4. No continuous, Kerala-validated weather or rainfall series exists for the pilot.
5. No crop-specific local production labels or expert-confirmed black-pepper disease labels exist.
6. No exact source versions, licences or acquisition manifests support a training dataset.
7. The district catalogue has names but no versioned boundary geometry or CRS.

## Licence and training restrictions

- No commercial source is approved; the commercial inventory has 11 conditional and 2 blocked entries.
- No source is approved for training.
- Portfolio/research permission and commercial permission are separate.
- Public availability is not authority to acquire or train.
- ERA5-Land's existing archives are integrity-verified but quality-rejected for training.
- SoilGrids and WoSIS estimates/profiles cannot substitute for authorized measured soil targets.
- Disease image datasets require independent rights review and local expert validation.

## Acquisition readiness

Actual acquisition should wait for:

1. Owner approval to identify and contact exact data owners.
2. Source owner confirmation of exact publication/dataset, release and licence.
3. An Idukki/black-pepper evidence source sufficient to establish district/crop relevance.
4. Exact record schema and approved sample/observation fields.
5. Spatial and temporal coverage sufficient for the intended question.
6. Quality thresholds reviewed by an agricultural scientist and data owner.
7. A separate acquisition approval after the above evidence is documented.

## Validation performed

No external source was queried and no data was downloaded. The following repository evidence was inspected:

- Stage 19 black-pepper pilot, dictionary, source assessment and readiness documents
- Source inventory and acquisition/quality manifests
- ERA5-Land quality and provenance reports
- Weather quality specification
- Kerala crop audit
- Dataset licensing/governance status
- Data governance and pilot contract scripts
- Existing Stage 20 deliverable planning baseline

Standalone Stage 19 contract tests were re-run with application conftest disabled:

- `10 passed`
- No packages were downloaded or installed

The normal application-conftest test path could not load because GeoAlchemy 2 is unavailable in the current environment. This is a dependency/environment limitation, not a contract failure.

Python compilation of the standalone pilot contract and test module passed.

No database writes, migrations, credentials, API calls, downloads, ML training, commits or pushes were performed.

## Recommended Stage 21

**Stage 21 — User-authorized evidence inquiry and source-specific permission review**

Stage 21 may begin only after the project owner approves the intended data owners and intended uses. The first tasks should be to identify exact authoritative publications/resources, obtain written or resource-specific reuse terms, confirm Idukki/black-pepper evidence, pin weather/soil/disease data releases, and document acquisition manifests. No data should be requested or downloaded until those permissions and evidence gates are satisfied.
