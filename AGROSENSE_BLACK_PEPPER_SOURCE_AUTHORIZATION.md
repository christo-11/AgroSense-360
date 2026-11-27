# AgroSense-360 Black Pepper Source Authorization

**Stage:** 20  
**Decision scope:** Portfolio/research assessment for a future Kerala black-pepper pilot  
**Assessment date:** 2026-11-23  
**Status:** Planning and evidence validation only

## Executive decision

No data source is currently authorized for acquisition for the Idukki/black-pepper pilot. The repository has no exact, training-cleared, crop-linked, district-linked, or observed black-pepper dataset. Existing portfolio/research classifications are not acquisition approvals or ML-training approvals.

The pilot can proceed only to further evidence and permission review. It is not ready for actual acquisition.

## Classification rules

- `APPROVED_FOR_PILOT_RESEARCH`: exact resource, portfolio/research terms, crop/geography/time scope, and data quality are sufficiently identified.
- `APPROVED_FOR_TRAINING`: commercial or research training approval, acquisition provenance, quality, relevance, and signed governance gate are all satisfied.
- `CONDITIONAL`: useful evidence or product exists, but exact rights, version, coverage, quality, or data provenance remains unresolved.
- `BLOCKED`: known terms or evidence conflicts with the project scope.
- `REQUIRES_USER_APPROVAL`: the project owner or source owner must explicitly authorize a particular inquiry or use.

These statuses are independent. No source is approved for training.

## Source authorization matrix

| Source ID | Owner and official location | Dataset/publication | Version/date | Coverage | Licence/attribution | Portfolio/research | Commercial/training restriction | Quality limitations | Stage 20 classification |
|---|---|---|---|---|---|---|---|---|---|
| `kau_crops_and_weather` | Kerala Agricultural University; https://kau.in/ | Crop, variety, observatory or research publications; no exact export identified | Not pinned | Kerala; Idukki and black-pepper links unknown | No resource-specific licence verified | Unverified | Requires separate exact-publication reuse, commercial and training decisions | No structured historical series or exact black-pepper publication identified | `REQUIRES_USER_APPROVAL` |
| `india_district_season_crop_production` | Ministry of Agriculture and Farmers Welfare / data.gov.in; https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997 | District-wise, season-wise crop production statistics from 1997 | Not pinned; end date unknown | India; Kerala/Idukki/black-pepper rows unverified | Resource licence and attribution unverified | Unverified | API key, exact terms and schema approval required; training not assessed | Prior page 403; crop/item names, units, revisions and missingness unknown | `REQUIRES_USER_APPROVAL` |
| `soil_health_card_lab` | Government of India, Department of Agriculture and Farmers Welfare; https://soilhealth.dac.gov.in/ | Soil Health Card/lab records | Not pinned | India; Idukki coverage and crop linkage unknown | Dataset and bulk-export terms unverified | Unverified | Written record-level and privacy/reuse permission required; training permission not assessed | No authorized georeferenced samples, depth, method, lab/QC or units | `REQUIRES_USER_APPROVAL` |
| `wosis_profiles` | ISRIC/World Soil Information; https://docs.isric.org/globaldata/wosis/faq-wosis.html | WoSIS soil profiles | Contributor snapshot varies | Global profiles; Kerala/Idukki availability unverified | Contributor-specific terms | Unverified | Provider-specific reuse and training decisions required | Sampling date, depth, unit, analytical method and provider vary | `CONDITIONAL` |
| `soilgrids_v2` | ISRIC; https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html | SoilGrids 2.0 | Product identified; release/snapshot not pinned | Global 250 m modeled raster/points | ISRIC policy applies; exact output licence not text-verified | Conditional | Commercial rights unverified; model estimates are not lab targets | No observation date; no verified P or K layers; local validation unavailable | `CONDITIONAL` |
| `era5_land` | ECMWF/Copernicus CDS; https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land | ERA5-Land hourly reanalysis | Product named; exact request/product version unpinned | Global 0.1-degree land grid | Copernicus Licence v1.2 and CDS terms; C3S attribution/disclaimer required | Approved for portfolio/research only | Commercial use conditional; training rejected for existing archives | 2 and 12 sparse/irregular main timestamps; no Kerala district/cell or independent gauge validation | `CONDITIONAL` |
| `nasa_gpm_imerg` | NASA GPM; https://gpm.nasa.gov/data/imerg | GPM IMERG Final Run V07B | V07B identified; exact asset not pinned | Global precipitation estimate | GPM/TRMM use policy and NASA ESDIS guidance; not CC0 | Approved for portfolio/research only | Commercial use conditional; training not assessed | No exact asset or Kerala gauge validation; precipitation only | `CONDITIONAL` |
| `open_meteo_historical` | Open-Meteo; https://open-meteo.com/en/docs/historical-weather-api | Historical Weather API | Model/version not pinned | Global reanalysis/model | API data CC BY 4.0; free API terms non-commercial | Approved for portfolio/research only | Free tier blocked for commercial use; training not assessed | No request/response provenance or independent Kerala validation | `CONDITIONAL` |
| `sentinel2_l2a` | Copernicus/European Union; https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html | Sentinel-2 Level-2A surface reflectance | Exact scene, baseline and product date not pinned | Global land | Sentinel legal notice/Data Space terms; exact legal notice for selected asset required | Conditional | Commercial and training status not assessed | No crop/disease labels, scene, mask, season or local field validation | `CONDITIONAL` |
| `agmarknet_daily_mandi` | Government of India / data.gov.in; https://agmarknet.gov.in/ | Current daily mandi prices | Not pinned | India market level; Kerala coverage unknown | Resource terms unverified | Unverified | Requires exact data-use and API approval | No verified commodity variety, grade, units, arrival fields or historical coverage | `REQUIRES_USER_APPROVAL` |
| `faostat_qcl` | FAO; https://www.fao.org/faostat/en/#data/QCL | FAOSTAT Crops and Livestock Products QCL | Release not pinned | Country/territory, not Kerala district | CC BY 4.0 plus FAO Statistical Database Terms | Blocked | FAO terms conflict with potential commercial promotion; training not cleared | Too coarse for district targets; no Kerala crop linkage | `BLOCKED` |
| `plantvillage` | PlantVillage authors / Hugging Face; https://github.com/spMohanty/PlantVillage-Dataset | PlantVillage image dataset | Mirror and upstream version unpinned | Controlled images; no reliable geography | Hugging Face mirror declares CC BY-SA 3.0; upstream no verified licence file | Unverified | Underlying image rights and share-alike obligations unresolved | Controlled imagery, no capture geography, uncertain black-pepper disease relevance | `CONDITIONAL` |
| `plantdoc` | PlantDoc authors; https://github.com/pratikkayal/PlantDoc-Dataset | PlantDoc classification dataset | Dataset version unpinned | Scraped internet images; geography unknown | Repository declares CC BY 4.0; underlying image rights unverified | Unverified | Image rights and training use unresolved | No Kerala field provenance or expert-confirmed local labels | `CONDITIONAL` |

## Exact permissions required

1. **Idukki/black-pepper evidence:** obtain a KAU or other authoritative record that explicitly links the exact crop/variety and district, with title, publication date, method, geographic scope and reuse terms.
2. **Production statistics:** obtain resource-owner confirmation of the exact resource, licence, schema, Kerala/Idukki rows, units, revisions and API access terms.
3. **Weather:** for ERA5-Land, pin product/request provenance and complete the Kerala spatial/temporal/independent validation. Separate commercial and training approvals are required. NASA GPM and Open-Meteo may be considered only after exact asset/version, rights, coverage and research scope are approved.
4. **Soil:** obtain written reuse permission for georeferenced, depth-specific lab records linked to actual black-pepper sites or explicitly approved research profiles. For WoSIS, contributor-specific terms must be reviewed per record. SoilGrids may be retained only as a modeled covariate, not ground truth.
5. **Disease:** obtain expert-confirmed Kerala field-image labels and dataset rights. Existing PlantVillage/PlantDoc assets cannot establish black-pepper disease prevalence or local suitability.
6. **Training:** even for an otherwise permitted research source, training requires source approval, quality verification, training relevance verification, an immutable snapshot, provenance manifest and signed governance approval.

## Acquisition prohibition

Until the exact source and use are approved, AgroSense-360 must not request data, call an acquisition API, enter an account/API-key process, download content or submit an acquisition form. Existing ERA5-Land archives already present may remain archived and may be referenced for integrity/quality assessment, but not used as pilot training or observation evidence.
