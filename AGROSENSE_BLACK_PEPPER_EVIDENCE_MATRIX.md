# AgroSense-360 Black Pepper Evidence Matrix

**Scope:** Idukki provisional pilot location; crop, district, observation period and variables remain unverified where not stated otherwise.

## Evidence matrix

| Crop | District | Observation period | Variable/claim | Source | Evidence type | Verification status | Confidence/limitations |
|---|---|---|---|---|---|---|---|
| Black pepper | Idukki | None | Crop catalogue identity | Repository migration | Catalogue seed | Verified only for catalogue entry | Confirms a name row, not cultivation or suitability |
| Black pepper | Idukki | None | Scientific name `Piper nigrum` | Stage 19 user-supplied request | Unsupported claim in catalogue | Requires validation | Migration leaves `scientific_name` null; no authority citation found |
| Black pepper | Idukki | None | District/crop relationship | Migration/repository audit | Catalogue relationship check | Not established | No seeded suitability, source or profile evidence |
| Black pepper | Idukki | None | Variety | Repository catalogue | Catalogue model only | Missing | No variety rows or varieties in seed |
| Black pepper | Idukki | None | Growing season | No source identified | Unsupported assumption | Missing | Season not established |
| Black pepper | Idukki | None | Cultivation practices | No exact source identified | Unsupported assumption | Missing | KAU publication/export not identified |
| Black pepper | Idukki | None | Soil pH/N/P/K/texture/organic carbon | Repository soil source inventory | No observation; candidate sources only | Missing | No authorized, georeferenced lab samples |
| Black pepper | Idukki | No approved period | Soil pH | SoilGrids 2.0 candidate | Modeled estimate | Pending review | 250 m global model estimate, not lab ground truth |
| Black pepper | Idukki | Profile sampling dates unknown | Soil properties | WoSIS candidate | Measured profile data candidate | Pending/provider-specific | No Kerala/Idukki profiles or rights selected |
| Black pepper | Idukki | Unknown | Soil properties | Soil Health Card/lab candidate | Potential measured laboratory data | Missing/permission unresolved | No bulk export or record-level authorization |
| Black pepper | Idukki | 1997 to latest, not verified | Production/area/yield | India district crop-production candidate | Candidate administrative statistics | Missing/rights and schema unverified | No confirmed Kerala/Idukki/black-pepper rows or units |
| Black pepper | Idukki | 1961 to latest varies | Production/area/yield | FAOSTAT QCL | Country-level published statistics | Rejected for district pilot | Country aggregates cannot establish Idukki evidence; terms blocked |
| Black pepper | Idukki | 2024-01-03 03:00–06:00 UTC | ERA5-Land weather variables | Existing archive request 1 | Reanalysis estimate | Rejected for training; sparse | Two timestamps only; no Idukki mask or independent validation |
| Black pepper | Idukki | 2011-01-11 to 2011-01-29 UTC, irregular | ERA5-Land weather/land variables | Existing archive request 2 | Reanalysis estimate | Rejected for training; sparse | 12 irregular timestamps; no continuous Kerala series |
| Black pepper | Idukki | No approved period | Precipitation | NASA GPM IMERG V07B candidate | Satellite/reanalysis estimate | Pending exact asset | No Kerala gauge validation or downloaded asset |
| Black pepper | Idukki | No approved period | Weather variables | Open-Meteo candidate | Modeled API estimate | Blocked by free-tier commercial scope | No model/request provenance or independent validation |
| Black pepper | Idukki | No approved period | Surface reflectance/derived indices | Sentinel-2 candidate | Satellite estimate | Pending | No pinned scenes, seasons, masks or field labels |
| Black pepper | Idukki | No approved period | Mandi prices/arrivals | AGMARKNET candidate | Administrative market data | Missing/permission unresolved | Not a growing-condition or disease target; commodity/grade/market coverage unknown |
| Black pepper | Idukki | None | Disease presence/severity | PlantVillage candidate | Controlled image labels | Not verified/poor locality fit | No Kerala field provenance or selected black-pepper disease labels |
| Black pepper | Idukki | None | Disease presence/severity | PlantDoc candidate | Scraped image labels | Not verified/rights and geography unresolved | Not confirmed as expert-validated Kerala field data |
| Black pepper | Idukki | Not available | District boundary/area | Repository district catalogue | Catalogue names only | Not established for geospatial use | No boundary geometry, CRS, publisher, release or checksum |

## Evidence definitions

- **Measured:** instrument, station, gauge or laboratory observation with retained method and provenance.
- **Estimated:** reanalysis, model, raster or satellite output. Estimated values are never laboratory labels or observed crop outcomes.
- **Published research finding:** peer-reviewed or authoritative publication claim that identifies crop, geography, method and publication provenance.
- **Administrative statistic:** official production, price or market data with an exact resource schema and unit.
- **Unsupported assumption:** an expected, planted or inferred relationship without source evidence.

## Evidence gaps blocking acquisition or claims

1. Exact Idukki/black-pepper source record.
2. Pinned crop taxonomy authority.
3. Approved variety and observation period.
4. District boundary version and area mask.
5. Authorized measured soil samples.
6. Continuous, independently validated Kerala weather.
7. Black-pepper-specific production or disease labels.
8. Exact source licences and versioned acquisition manifests.

No observations, crop statistics or soil values are invented in this matrix.
