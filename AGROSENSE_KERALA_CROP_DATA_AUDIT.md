# AgroSense-360 Kerala Crop Data Audit

## Scope and evidence

This audit examines the repository-seeded catalogue and its data model, the current dataset-governance inventory, and the existing data-intelligence and licensing documentation. No external sources were queried and no datasets were downloaded. The migration `backend/migrations/versions/5d3cbf283629_add_agricultural_master_catalog.py` seeds catalogue identifiers; those identifiers are not evidence of local cultivation, suitability, crop requirements, or ground truth.

The local API was unavailable during this audit, so the current live database could not be re-read. The counts below are confirmed by the migration and, where noted, are consistent with the previously recorded Stage 16 live snapshot. They are not represented as a fresh live-database check.

## Catalogue evidence

The migration seeds 14 Kerala district names, four crop categories, 31 crop names, and one empty `pending` profile for each crop. It seeds no varieties, agricultural-source records, district boundaries, or district/crop suitability records. Scientific names and agronomic claims are not supplied by these seed rows.

### District catalogue

| District | District/crop evidence status |
| --- | --- |
| Thiruvananthapuram | No district/crop relationship seeded; suitability unknown |
| Kollam | No district/crop relationship seeded; suitability unknown |
| Pathanamthitta | No district/crop relationship seeded; suitability unknown |
| Alappuzha | No district/crop relationship seeded; suitability unknown |
| Kottayam | No district/crop relationship seeded; suitability unknown |
| Idukki | No district/crop relationship seeded; suitability unknown |
| Ernakulam | No district/crop relationship seeded; suitability unknown |
| Thrissur | No district/crop relationship seeded; suitability unknown |
| Palakkad | No district/crop relationship seeded; suitability unknown |
| Malappuram | No district/crop relationship seeded; suitability unknown |
| Kozhikode | No district/crop relationship seeded; suitability unknown |
| Wayanad | No district/crop relationship seeded; suitability unknown |
| Kannur | No district/crop relationship seeded; suitability unknown |
| Kasaragod | No district/crop relationship seeded; suitability unknown |

### Crop intelligence matrix

This is a catalogue-evidence matrix, not a crop recommendation. The district column means the listed crop has **no verified association in any of the 14 districts above**. Consequently, every variety, soil, temperature, rainfall, and growing-season value is unknown. A source-inventory candidate is not a crop-specific source citation; no evidence is attached to these seeded profiles.

| District coverage | Crop | Crop category | Variety | Soil requirements | Temperature requirements | Rainfall requirements | Growing season | Source reference | Evidence quality | Verification status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All 14; no association recorded | Black pepper | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Cardamom | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Coffee | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Tea | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Clove | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Nutmeg | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Ginger | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Turmeric | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Cinnamon | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Vanilla | Plantation and spices | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Rice | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Tapioca | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Banana | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Yam | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Sweet potato | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Maize | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Pulses | Food and field crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Mango | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Jackfruit | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Pineapple | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Papaya | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Guava | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Rambutan | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Avocado | Fruits | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Coconut | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Arecanut | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Rubber | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Cashew | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Cocoa | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Vegetables | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |
| All 14; no association recorded | Flowers | Commercial and other crops | Unknown | Unknown | Unknown | Unknown | Unknown | None attached | No claim-level evidence | Pending |

The matrix deliberately does not convert the 14 × 31 catalogue cross-product into 434 suitability claims. For every possible pair, the relationship is **not established**, not “suitable,” “not suitable,” or evidence of cultivation.

## Agricultural data found and not found

| Subject | Repository evidence | Readiness interpretation |
| --- | --- | --- |
| Districts | Seeded district identifiers and names | Catalogue coverage only; no district polygons or crop associations in the seed migration |
| Crops and categories | 31 crop names across four categories | Catalogue labels only; not verified agricultural ground truth |
| Crop profiles | One profile row per seeded crop, status `pending`, no agronomic values set by the migration | Incomplete; no supported soil, temperature, rainfall, season, or yield facts |
| Varieties | `CropVariety` model exists; no variety rows are seeded and the prior live snapshot reported zero | No variety is evidenced by the current catalogue snapshot |
| District-crop suitability | Relationship model and API exist; no rows are seeded and the prior live snapshot reported zero | No district-level crop-suitability claim is available |
| Soil | SoilGrids and WoSIS are listed as possible sources; no local soil samples or acquired soil dataset are documented | No Kerala-specific, plot-linked soil labels |
| Weather/rainfall/temperature | Two ERA5-Land archive requests and their quality records exist; both are marked `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`. KAU's current summary is not a verified historical series. | Weather archives are not a continuous Kerala dataset; no independent station/gauge series is present |
| Production/yield | India district-production resource is a candidate with unverified schema/licence; FAOSTAT is country-level and blocked for the reviewed use | No verified Kerala district/crop/year training labels |
| Plant disease | PlantVillage and PlantDoc are candidate image sources with licensing and representativeness concerns | No verified Kerala field-image set or local expert-confirmed disease labels |

## Existing crop-data schema review

The current schema is sufficient to hold catalogue entities and simple sourced claims:

- `CropCategory`, `Crop`, and `District` provide catalogue keys. `District` has no geometry or boundary-version field.
- `CropProfile` stores a single set of optional crop-wide fields, including soil pH/type, temperature and annual rainfall ranges, season, cultivation information, and yield. It cannot represent different requirements by variety, district, season, or source without overloading a single profile.
- `CropVariety` is linked to a crop and has a verification status.
- `DistrictCropSuitability` links district, crop, and optional variety; it has suitability and verification statuses plus source references.
- `AgriculturalSource` stores title, publisher, URL, optional license, accessed date, and notes. The join tables link sources to whole profiles, varieties, or district/crop records.
- Existing constraints validate ranges, allowed status values, source existence through foreign keys, variety/crop consistency, and disallow a verified relationship that remains `under_review`.

### Material limitations

1. Evidence is associated with a whole profile or relationship, not with each individual agronomic assertion. A source attached to a profile cannot identify which soil, climate, or season field it supports.
2. The profile update path considers a profile verified when it has at least one sourced claim. That is not a completeness assessment; a partially populated profile can therefore be marked `verified`. This audit does not invent a universal required-field policy or change that behavior. A separate completeness status and claim-level evidence should be agreed before any profile is presented as complete.
3. There is no first-class evidence record for source version, dataset release, retrieval checksum, citation/attribution text, rights decision history, method, geography, effective period, uncertainty, or reviewer decision.
4. District identifiers have no versioned boundary geometry. District suitability should not imply field-level or spatially resolved suitability.
5. Current data expose no evidence confidence/quality scale, conflicting evidence resolution, or temporal validity for a claim.
6. `common_pests_diseases` is non-null and defaults to an empty list. In a pending seed profile, that empty list means no recorded items; it does not establish that a crop has no pests or diseases. The model currently lacks an explicit unknown-versus-reviewed-empty distinction for this field.

### Recommended normalized model (design only)

No schema or migration change is needed for this audit. Before populated evidence is accepted at scale, use a normalized design along these lines:

1. Keep `Crop`, `CropVariety`, and `District` as stable catalogue identities; add versioned district boundary evidence before spatial aggregation.
2. Represent soil/climate requirements as typed `AgronomicRequirement` claims: subject crop/variety, optional district/region, property, value/range, unit, method, applicable season/period, uncertainty, and verification state.
3. Store dataset/document provenance in a `SourceEvidence` record with publisher, stable source identifier/DOI, release/version, citation and attribution, license/terms snapshot, geographic and temporal scope, retrieval date, checksum where applicable, and rights decision.
4. Link each requirement and district/crop relationship to one or more evidence records at claim level. Preserve conflicting sources rather than silently overwriting one claim with another.
5. Record reviewer, decision, date, and rationale as an auditable verification event. Keep `evidence_quality`, `verification_status`, and `completeness_status` independent.
6. Define uniqueness and foreign-key constraints for crop, variety, district, boundary version, source, and claim; keep “unknown” distinct from zero or a negative suitability decision.

This is a future design recommendation, not an instruction to apply a migration now.

## Source and licensing assessment

The following is the existing inventory's assessment, not a new rights determination. “Training not cleared” means the current project has no documented approval and data-quality acceptance for model training; it does not assert that every publisher prohibits ML. Dataset candidates are not evidence attached to a crop profile.

| Source (ID) | Publisher; version | Geographic / temporal scope | License and attribution evidence | Portfolio / research | Commercial status | ML training status; missing evidence |
| --- | --- | --- | --- | --- | --- | --- |
| India district-wise crop production (`india_district_season_crop_production`) | Government of India, Ministry of Agriculture and Farmers Welfare / data.gov.in; version not pinned | India district candidate; Kerala coverage unverified. Resource title says from 1997; update/end date unknown. | Resource-specific license and attribution not verified; catalogue returned 403 in prior research. | Unverified | Conditional | Not assessed/cleared. Need authorized schema, Kerala coverage, units, revisions, and license. |
| FAOSTAT QCL (`faostat_qcl`) | FAO; release not pinned | Country/territory, 1961 to latest varying by item; not Kerala district-level | CC BY 4.0 plus FAO database terms; attribute FAO and dataset, honor third-party exceptions and no-endorsement conditions. | Blocked in current review | Blocked | Not cleared; terms restrict certain commercial-promotion uses, and geography is too coarse for district labels. |
| KAU crop/weather information (`kau_crops_and_weather`) | Kerala Agricultural University; no dataset version pinned | Kerala guidance and observatory locations vary by publication; only a current summary was checked, not historical coverage | No resource-specific license verified; assess attribution and reuse per publication. | Unverified | Conditional | Not assessed/cleared. Need a structured, versioned dataset, coverage, and document-level terms. |
| AGMARKNET daily mandi prices (`agmarknet_daily_mandi`) | Government of India agricultural marketing portal / data.gov.in; resource version not pinned | India market level; Kerala availability and historical retention not verified | Resource-specific reuse terms and attribution not verified. | Unverified | Conditional | Not assessed/cleared. Need live schema, Kerala records, units, history, and resource license. |
| SoilGrids 2.0 (`soilgrids_v2`) | ISRIC; product name identifies v2.0, snapshot/release not pinned | Global 250 m modelled maps; not observation dates | Exact applicable product license was not text-verified; retain attribution and product policy before reuse. | Conditional | Conditional | Not training-label eligible; model estimates are not local lab ground truth. Need version, units/scaling, local validation, and exact rights. |
| WoSIS profiles (`wosis_profiles`) | ISRIC; snapshot not pinned | Global soil profiles; sample dates vary; Kerala coverage not verified | Provider-specific terms; no single collection-wide license. Attribute the contributing source and profile. | Unverified | Conditional | Not assessed/cleared. Need per-profile rights, available Kerala records, methods, units, and sample provenance. |
| India Soil Health Card (`soil_health_card_lab`) | Government of India, Department of Agriculture and Farmers Welfare; version not pinned | India portal; geospatially joinable local data and time coverage not verified | Dataset-level license and bulk-export terms not verified; permission and attribution unresolved. | Unverified | Conditional | Not assessed/cleared. Need authorized sample records, methods, coordinates, units, and reuse permission. |
| Sentinel-2 L2A (`sentinel2_l2a`) | Copernicus / European Union; asset/product baseline not pinned | Global land; mission coverage/product dates vary | Sentinel data are described as free/full/open; retain Copernicus attribution and verify the applicable legal notice for the selected asset. | Conditional | Conditional | Not assessed/cleared. Need a pinned asset/product baseline, local coverage, processing provenance, and task-specific labels. |
| ERA5-Land (`era5_land`) | ECMWF / Copernicus; product named hourly from 1950-present, exact product version unresolved | Global land; hourly; current archives do not establish continuous Kerala coverage | Copernicus product terms and CDS terms; retain required attribution and accepted terms. Exact request and product evidence remain incomplete. | Approved for portfolio/research only | Conditional | **Rejected for training** for the two current archives (`NEEDS_MORE_DATA` / `REJECT_FOR_TRAINING`). Exact request parameters/version and adequate continuous coverage are missing. |
| NASA GPM IMERG (`nasa_gpm_imerg`) | NASA; V07B recorded | Most of Earth's surface; record spans TRMM/GPM eras, with exact coverage depending on product/run | GPM/TRMM data-use policy and NASA guidance; exact product notice/restrictions not verified. Attribute the product and version. | Approved for portfolio/research only | Conditional | Not assessed/cleared. Not downloaded; need exact product/run, data policy, Kerala coverage, and gauge validation. |
| Open-Meteo historical (`open_meteo_historical`) | Open-Meteo; model/version not pinned | Global model data; model determines variables, resolution, and time coverage | API data CC BY 4.0 with attribution; free-service terms are non-commercial. A commercial plan/decision is required for commercial use. | Approved for portfolio/research only | Blocked pending commercial-use decision | Not assessed/cleared. Need pinned model, retained request/response provenance, rights fit, and independent validation. |
| PlantVillage (`plantvillage`) | PlantVillage authors; Hugging Face mirror/version not pinned | No reliable farm coordinates or capture dates; not Kerala field evidence | Mirror card declares CC BY-SA 3.0; upstream checked repository had no license file; underlying image rights and share-alike obligations unresolved. Attribute authors/source. | Unverified | Conditional | Not assessed/cleared. Need authoritative rights, pinned manifest/split, deduplication, and locally representative field validation. |
| PlantDoc (`plantdoc`) | PlantDoc authors; dataset version not pinned | Web-sourced images; reliable location and capture dates not documented | Repository declares CC BY 4.0; underlying scraped-image rights remain unresolved. Attribute authors/source and retain license evidence. | Unverified | Conditional | Not assessed/cleared. Need image-rights review, pinned manifest, label review, and local expert-confirmed evaluation. |

Portfolio/research permission does not imply commercial approval, permission to redistribute, or ML-training eligibility. The source inventory records 13 candidates: 3 portfolio/research-only approvals, 2 conditional portfolio reviews, 1 blocked portfolio review, and 7 unverified; commercial review is 11 conditional, 2 blocked, and 0 approved. No source is currently cleared for training.

## Required evidence before crop claims can be published

- A source document or dataset with identifiable publisher, version/date, citation, license, attribution requirements, and applicable geographic/time scope.
- Claim-level citations for each profile value; preserve original units, definitions, methods, uncertainty, and date/version.
- For varieties, evidence of the variety identity and applicable crop/region; do not infer a variety from a crop name.
- For a district/crop relationship, an explicit source that supports the exact geographic and agronomic claim, a review record, and a status distinct from training eligibility.
- For local soil labels, georeferenced samples with collection date, depth, analytical method, units, lab, quality controls, and reuse permission.
- For disease claims, authoritative labels and Kerala-relevant, expert-confirmed field examples; online image classes alone do not establish local disease prevalence.

## Audit conclusion

The repository has a useful catalogue schema and seed list, but **Kerala crop suitability is not ready**. The catalogue is not agricultural evidence. No crop profile, variety, or district/crop relationship should be presented as verified based on the current seed data. Keep crop recommendations and ML training disabled until the evidence, rights, geographic support, and validation gaps above are resolved.
