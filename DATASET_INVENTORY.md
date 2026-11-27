# AgroSense-360 Real Agricultural Data Inventory

**Research checked:** 2026-11-19
**Scope:** Official-source, resource-level license/access review and read-only discovery as of 2026-11-19. No dataset was downloaded during that audit, no credential was read or used, and no model was trained. A later Stage 17 provenance reconciliation verified two previously recorded ERA5-Land archives without downloading or modifying them.

## Executive summary

There are useful public sources for global soil context, satellite imagery, weather, plant disease images, national yield history, and Indian mandi prices. Public availability does not mean that each source is suitable as a local ground-truth label or is licensed for every commercial use.

As of the Stage 12 audit on 2026-11-19, no source in this inventory had been ingested into AgroSense-360. On 2026-11-20, two ERA5-Land archive files were later verified against their acquisition and quality records. They remain unsuitable for training. The soil and disease training scripts in `backend/scripts/` require curated, labeled data. In particular, SoilGrids does not provide phosphorus or potassium layers, and modelled SoilGrids values must not be presented as laboratory observations.

The Stage 12 audit checked official source and terms pages on 2026-11-19. SoilGrids documentation and layer metadata were reachable; no soil values or raster were requested. The data.gov.in production resource returned HTTP 403; no API key was read or used. FAO's statistical database terms were reachable, but the prior read-only bulk-file check returned HTTP 403. AGMARKNET returned its JavaScript application shell and no price schema was verified. These are access-check results, not claims that sources are unavailable generally.

As of the 2026-11-19 rights review, no candidate met the complete repository approval gate for the project's potential commercial use; no resource is classified `APPROVED`, and no candidate was classified `REJECTED`. Two ERA5-Land archives were acquired and verified on 2026-11-20, but this did not change source permissions or make them suitable for training. `CONDITIONAL` means terms, access, or rights still require resolution; `BLOCKED` means known terms conflict with the intended commercial use; `REJECTED` would mean the project will not pursue that resource.

## Stage 12 suitability and acquisition decision

| Intended portfolio capability | Suitable source candidate | Current decision | Why it is or is not suitable |
|---|---|---|---|
| Soil properties | SoilGrids 2.0 / WoSIS | CONDITIONAL | SoilGrids is modeled 250 m context, not lab ground truth; WoSIS rights vary by provider and a Kerala/P/K-labelled sample set is not yet verified. |
| Weather and rainfall | ERA5-Land / GPM IMERG / Open-Meteo | CONDITIONAL or BLOCKED | ERA5-Land and IMERG remain account/term-specific and lack a selected asset; Open-Meteo's free API is non-commercial and excluded. |
| Crop production and yield | data.gov.in district crop production / FAOSTAT QCL | CONDITIONAL / BLOCKED | The district resource needs a live resource licence and key; FAO additional terms prohibit commercial promotion use. |
| Market prices | AGMARKNET / data.gov.in mandi | CONDITIONAL | Resource-specific licence, key, Kerala coverage, units and schema are not verified. |
| Crop disease images | PlantVillage / PlantDoc | CONDITIONAL | Repositories and mirrors do not establish all underlying image rights; neither has verified Kerala field provenance. |
| Crop varieties and agronomic information | KAU publications / observatory | CONDITIONAL | No exact structured, licensed, versioned dataset or publication export was identified. |

At the 2026-11-19 audit, no source from this matrix was acquired. The later ERA5-Land acquisition is recorded separately below; it does not change any source approval. A Kerala-focused licence, selected version/asset, provenance manifest and checksums are still required before a source can progress beyond `CONDITIONAL` or `BLOCKED`.

## Repository audit and staged execution plan

- The Stage 12 repository scan found no raw/processed datasets or trained model artifacts. Stage 17 later verified the two listed ERA5-Land archives already in `data/raw/`; it added no dataset files.
- The only ML entry points are `backend/scripts/train_soil_model.py` and `backend/scripts/train_disease_model.py`. The soil trainer uses a random row split and does not capture source, unit, depth, time, or spatial-group provenance. The disease trainer makes a per-image random split and does not consume PlantVillage's leaf-grouped split. Neither should be used for a reported evaluation until its data-specific leakage controls are addressed.
- The API explicitly reports insight/model services as unavailable; crop-image analysis returns 503. There is no model registry or validated inference artifact.
- No credential was read or used in this audit. Sources requiring API keys, accounts, or permission were not accessed with credentials.
- `.gitignore` now excludes `data/raw/`, `data/interim/`, and `data/processed/`; the small source metadata and reports remain trackable.

Execution dependencies:

1. **Stage 6B:** finish source/rights verification; obtain required source credentials or permissions; acquire only appropriately licensed, versioned data. For Kerala yield, verify district-season coverage and units from the authenticated data.gov.in resource. For disease work, resolve image rights and obtain an expert-labeled Kerala field evaluation set. For soil, obtain georeferenced lab samples and method/depth metadata. No acquired dataset currently satisfies these requirements.
2. **Stage 7:** implement source-specific reproducible cleaning, quality reports, deduplication, units, and spatial/temporal/group-aware split manifests only after a dataset and license are approved.
3. **Stage 8:** train only tasks with validated labels and evaluate against leakage-safe holdouts and baselines. No training was run.
4. **Stage 9:** add inference endpoints only for models that pass Stage 8 evaluation and are registered with limitations. No model-serving changes were made.

Machine-readable source statuses are recorded in [`data/metadata/source_inventory.json`](./data/metadata/source_inventory.json). ERA5-Land is now recorded as acquired and archive-integrity verified, but its product version remains unpinned (`dataset_version: null`, `version_status: ACQUIRED_VERSION_UNPINNED`) and its quality status is `QUALITY_REJECTED`. Its individual archive checksums are retained in the acquisition manifest; the source-level checksum remains null because the source consists of multiple archives. The other candidates retain their prior acquisition states. Acquisition or a reachable research page does not mean a dataset is approved or suitable for training.

## Commercial-use status and approval gate

Statuses apply to each identified resource, not to an entire website:

- **APPROVED:** commercial use and applicable resource terms are verified, required evidence is recorded, an allowlisted reviewer signs the record, and no concerns remain.
- **CONDITIONAL:** commercial use may be possible, but terms or obligations still require review. The training gate rejects it.
- **BLOCKED:** known terms conflict with the intended commercial use. The training gate rejects it.
- **REJECTED:** the project has decided not to use the exact resource for the stated purpose.

Current classifications:

| Resource / publisher | Exact resource, license and version | Commercial use, attribution and redistribution | Access, coverage and format | Status |
|---|---|---|---|---|---|
| [District-wise, season-wise crop production](https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997) — Government of India / data.gov.in | Exact resource named; resource-level license/version not verified. | Commercial permission, attribution and redistribution not verified. | API key required for API access; resource page returned 403. Kerala rows/schema and JSON/CSV format not verified. | CONDITIONAL |
| [FAOSTAT Crops and Livestock Products (QCL)](https://www.fao.org/faostat/en/#data/QCL) — FAO | CC BY 4.0 plus FAO Statistical Database Terms of Use; additional terms have no version number shown. | Terms prohibit use in conjunction with promoting a commercial enterprise, product or service. FAO citation/attribution and third-party exceptions apply. | Global country/year data; bulk file was not acquired and prior request returned 403. | BLOCKED |
| [KAU crop, variety and observatory information](https://kau.in/) — Kerala Agricultural University | No exact structured dataset or resource-specific license/version verified. | Permission, attribution and redistribution are unknown; no general website license assumed. | Public HTML and linked PDFs; current observatory page is not a versioned historical data export. Kerala scope; format of any actual dataset unknown. | CONDITIONAL |
| [Current daily mandi prices](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi) — Government of India / AGMARKNET | Exact resource named; resource-level license/version not verified. | Commercial permission, attribution and redistribution not verified. | API key required for data.gov.in API; catalog returned 403 and AGMARKNET served a JavaScript shell. Kerala coverage, schema and format unverified. | CONDITIONAL |
| [SoilGrids 2.0](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html) — ISRIC | ISRIC data policy identified; exact applicable product license/version was not text-verified. | Attribution to ISRIC/product is documented; commercial and redistribution scope remains conditional on the exact policy/product terms. | Global 250 m model predictions at standard depths; JSON metadata/point-query documentation. No raster or values acquired. | CONDITIONAL |
| [WoSIS profiles](https://docs.isric.org/globaldata/wosis/faq-wosis.html) — ISRIC and contributing providers | No single WoSIS-wide license; terms vary by contributing dataset and version. | Cite ISRIC and the source provider; some profiles cannot be redistributed. | Global georeferenced profiles; selected record, Kerala coverage, export format and license not verified. | CONDITIONAL |
| [India Soil Health Card](https://soilhealth.dac.gov.in/) — Government of India | No dataset-level license/version or permitted bulk export verified. | Commercial use, attribution and redistribution not verified; do not export farmer-linked records without authorization. | No georeferenced bulk dataset accessed; format and Kerala coverage unavailable. | CONDITIONAL |
| [Sentinel-2 Level-2A](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html) — Copernicus / European Union | Data Space terms say Sentinel data are free, full and open under the Sentinel Data Legal Notice; no numeric notice version was verified. | Follow the Sentinel notice attribution and modification requirements; portal materials have separate terms. | Global L2A surface reflectance; SAFE/JP2 products. Download requires Copernicus registration; no asset selected. | CONDITIONAL |
| [ERA5-Land hourly](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) — ECMWF / Copernicus CDS | Licence to Use Copernicus Products v1.2 permits reproduction, distribution and adaptation. C3S attribution and disclaimer are mandatory. | Cited Copernicus terms may be compatible with specified publisher-use conditions, including C3S attribution/disclaimer and third-party terms; this is an internal licence/terms compatibility assessment only, not source-owner permission or project-owner authorization. Any acquisition, portfolio/demo, pilot research, public sharing, training, or deployment requires applicable source-owner rights and separate valid purpose-specific project authorization. | Two archives acquired on 2026-11-20: one NetCDF (647,003,080 bytes) and one GRIB (2,026,384,498 bytes). Files, sizes, recorded SHA-256 comparisons and ZIP CRC evidence reconcile; exact CDS query parameters remain unconfirmed because the request-history MHT was not inspected. Both archives are rejected for training. | Training/commercial status remains CONDITIONAL; internal classification: APPROVED_PORTFOLIO_RESEARCH_ONLY (licence/terms assessment only); portfolio/demo and pilot research: NOT AUTHORIZED. |
| [NASA GPM IMERG Final Run V07B](https://gpm.nasa.gov/data/imerg) — NASA | GPM & TRMM Data Usage Policy and NASA ESDIS guidance require source citation and acknowledgement. Policy is not labelled CC0. | Cited NASA/GPM policy may permit reuse subject to required citation/acknowledgement and exact V07B asset/third-party terms. This is an internal licence/terms compatibility assessment only, not source-owner permission or project-owner authorization. Any acquisition, portfolio/demo, pilot research, public sharing, training, or deployment requires applicable source-owner rights and separate valid purpose-specific project authorization. | Kerala included, 1998-present, 0.1-degree grid, 30-minute/daily/monthly products, HDF/GeoTIFF/NetCDF; no file acquired. | Training/commercial status remains CONDITIONAL; internal classification: APPROVED_PORTFOLIO_RESEARCH_ONLY (licence/terms assessment only); portfolio/demo and pilot research: NOT AUTHORIZED. |
| [Open-Meteo Historical API](https://open-meteo.com/en/terms) — Open-Meteo | API data: CC BY 4.0; free-service Terms of Use. | Free API is limited to non-commercial use; CC BY attribution/link/change notice applies. Commercial use would require a paid plan, excluded here. | Global model/reanalysis values, JSON API; no request made. Free API has published rate limits. | BLOCKED |
| [PlantVillage](https://huggingface.co/datasets/mohanty/PlantVillage) — authors / Hugging Face mirror | Mirror card declares CC BY-SA 3.0; upstream GitHub repository has no checked license. | Mirror attribution/share-alike scope does not establish image-level rights; no commercial reuse or redistribution until clarified. | 14 crop species, controlled leaf imagery, no Kerala field provenance; JPG/image records; card states ~2 GB. Headline 54,306 differs from split total 54,305. | CONDITIONAL |
| [PlantDoc classification dataset](https://github.com/pratikkayal/PlantDoc-Dataset) — authors | Repository declares CC BY 4.0; no separate rights clearance for scraped source images. | Repository attribution applies only to content the authors could license; underlying image permissions remain unresolved. | 2,598 images, 13 species, up to 17 classes per repository; web-sourced, no verified Kerala/time provenance. | CONDITIONAL |

**No resource is approved for commercial reuse or model training.** These decisions are resource-specific engineering gates, not legal advice. Ambiguous terms must be referred to the provider or qualified counsel.

### Internal portfolio licence/terms classification

**Governance boundary:** `APPROVED_PORTFOLIO_RESEARCH_ONLY` is an internal inventory assessment of apparent publisher licence/terms compatibility for a limited, non-commercial portfolio/research category. It is not project-owner authorization, source-owner permission, approval to access or acquire data, approval to conduct research, approval for ML training, or approval for public demonstration or deployment. Portfolio/demo and pilot research are separate project permission scopes; neither inherits authorization from the other. Stage 40 currently marks both **NOT AUTHORIZED**. This classification does not change any governance status or dataset acquisition status.

The portfolio classification is separate from the commercial and ML-training reviews. It describes an inventory-level assessment of publisher terms only; it does not authorize project activity. No source is approved for commercial reuse or model training.

| Resource | Internal portfolio licence/terms classification | Scope / remaining limitation |
|---|---|---|
| data.gov.in district crop production | UNVERIFIED | Schema, Kerala rows, units, and resource terms unverified. |
| FAOSTAT QCL | BLOCKED | Terms concerning promotion of commercial products/services conflict with this hybrid project scope. |
| KAU publications and observatory | UNVERIFIED | No resource-specific reuse terms or versioned export. |
| AGMARKNET daily mandi | UNVERIFIED | API resource, Kerala coverage, and reuse terms unverified. |
| SoilGrids 2.0 | CONDITIONAL | Product attribution and separation from contributor records need review; estimates are not lab truth. |
| WoSIS | UNVERIFIED | Contributor-specific rights; no selected Kerala record reviewed. |
| Soil Health Card/lab records | UNVERIFIED | No permitted georeferenced export or record-level permission. |
| Sentinel-2 L2A | CONDITIONAL | Verify selected product/asset terms and attribution before use. |
| ERA5-Land hourly | APPROVED_PORTFOLIO_RESEARCH_ONLY | Cited Copernicus terms may appear compatible with limited non-commercial portfolio display, subject to exact CDS request terms, third-party terms, C3S attribution, and the required disclaimer. This classification is not project authorization. |
| NASA GPM IMERG Final Run V07B | APPROVED_PORTFOLIO_RESEARCH_ONLY | Cited GPM/NASA terms may appear compatible with limited non-commercial portfolio display, subject to exact asset metadata, citation, acknowledgement, and any third-party terms. This classification is not project authorization. |
| Open-Meteo free API | APPROVED_PORTFOLIO_RESEARCH_ONLY | Cited CC BY/free-service terms describe non-commercial use subject to attribution. No API query or integration is recorded; this classification does not authorize a query, project research, or public demonstration. |
| PlantVillage | UNVERIFIED | Mirror license does not establish upstream image-level rights. |
| PlantDoc | UNVERIFIED | Repository license does not resolve web-scraped image rights. |

These are scope-specific repository decisions based on the cited evidence, not legal advice. Re-review before public deployment if the use changes, and do not infer commercial rights from a portfolio/research status.

`backend/scripts/dataset_governance.py` is the fail-closed eligibility checker used by both training entry points. It rejects non-APPROVED resources and requires complete source/license metadata, an exact license version, a file format, verified third-party rights, an allowlisted reviewer, a private HMAC approval signature, acquired data, verified data quality and relevance, and a matching provenance manifest with a source URL, version, timezone-aware retrieval date, license, input path, and SHA-256 digest. It rejects duplicate resource IDs, invalid URLs, missing license fields, tampered signatures, and checksum/source mismatches. No command-line override exists. `backend/scripts/review_dataset.py` records allowlisted reviews; approval requires evidence and no remaining concerns. Keep `DATASET_REVIEWER_EMAILS` and `DATASET_APPROVAL_HMAC_KEY` private; this audit did not read or use either value.

### Soil and disease ground-truth requirements

Keep laboratory measurements separate from SoilGrids model estimates. A permitted Kerala soil sample record should include sample ID, coordinates and positional accuracy, district, collection date, depth/horizon, pH, organic carbon, measured nitrogen, available phosphorus and potassium (with extraction method/fraction), texture, units, laboratory/provider, source, permission, and quality flags. No measurements are present.

For disease images, collect only images with documented commercial image rights and expert-confirmed labels. Each record should include image ID, crop/variety, disease or healthy label, permitted district/region, capture date, expert verification, annotator/expert reference, rights/license/source, and a group ID that keeps related views in one split. Audit exact/near duplicates and class balance; hold out farms, collection groups, and an independently curated Kerala field test set. Do not treat PlantVillage or scraped PlantDoc images as expert-confirmed Kerala data.

The current generic trainers remain unsuitable for evaluation: soil uses random row splits without spatial/source grouping or complete measurement provenance; disease uses random per-image splitting and ignores `leaf_id`. Stage 7 must replace these splits with task-appropriate spatial/group/time holdouts and emit manifests before Stage 8 training.

## 1. Soil intelligence and laboratory labels

### SoilGrids 2.0 - global raster predictions and point-query API

- **Official sources:** [SoilGrids FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html), [REST API OpenAPI specification](https://rest.isric.org/soilgrids/v2.0/openapi.json), [live property/layer metadata](https://rest.isric.org/soilgrids/v2.0/properties/layers), [ISRIC data policy](https://isric.org/about/data-policy).
- **Access:** The documented REST API supports point queries and exposes layer metadata. The current OpenAPI document does not declare API-key authentication. It is not a bulk sample-label API; use the ISRIC Soil Data Hub for map downloads and check service limits before production use.
- **Coverage/resolution:** Global maps at 250 m, with standard depth intervals 0-5, 5-15, 15-30, 30-60, 60-100, and 100-200 cm. Organic-carbon stock is provided at 0-30 cm.
- **Properties in the live API metadata:** bulk density, CEC, coarse fragments, clay, nitrogen, organic-carbon density/stock, pH in water, sand, silt, and three water-retention properties. The response exposes mean, quantiles, and uncertainty. **Phosphorus and potassium are not listed as SoilGrids layers.**
- **Labels/units:** These are model predictions, not new laboratory measurements. The API layer-list response does not itself include units; retain the dataset's unit/scaling metadata and verify it before converting or training. Do not treat raw raster integer encodings as physical units.
- **License:** The official FAQ identifies SoilGrids 250 m v2.0, but the applicable product license in the linked ISRIC data-policy PDF was not text-verified in this audit. Treat rights as conditional; do not rely on the earlier CC-BY assertion until the exact policy/product terms have been retained.
- **Limitations:** 250 m pixels do not resolve individual small fields. Map uncertainty and the source profile distribution vary geographically. Using a SoilGrids estimate of SOC as both a training target and an input feature can create circularity, especially where the target profile contributed to the map.
- **Recommendation:** Use SoilGrids as a broad baseline/covariate and uncertainty surface, not as the supervised ground truth for AgroSense SOC, pH, or nitrogen models. It cannot supply the requested P/K labels.

### WoSIS - public standardized soil profile records

- **Official sources:** [WoSIS overview](https://www.isric.org/explore/wosis), [technical documentation and access](https://docs.isric.org/globaldata/wosis/), [WoSIS FAQ, properties and units](https://docs.isric.org/globaldata/wosis/faq-wosis.html).
- **Access:** Public standardized profiles are exposed through ISRIC data services, including WFS and GraphQL tutorials. Download/use is subject to the license attached to the contributing dataset.
- **Coverage/labels:** Global profiles and horizons. Current ISRIC overview reports over 230,000 georeferenced profiles in 174 countries, with over 900,000 horizons and 6 million records; another documentation page reports approximately 228,000 profiles. Counts depend on snapshot/version. Properties include organic carbon, total nitrogen, phosphorus (including extractable/total forms), pH, and other chemical/physical measurements. Potassium is not listed among the currently standardized properties on the overview page.
- **Units and provenance:** Records can include units, analytical-method aggregates, horizon/depth, sampling date, location uncertainty, and source-specific metadata. For example, the WoSIS code table reports organic carbon and total nitrogen in g/kg and pH as dimensionless; phosphorus forms and their units/methods must be read from the specific property record. Methods and available properties vary by profile; do not collapse different extraction methods into a single label without a documented harmonization policy.
- **License/access caveat:** WoSIS explicitly follows source-provider licenses. ISRIC says an additional approximately 110,000 shared profiles cannot be distributed due to restrictive provider licenses. Do not assume the entire underlying profile collection is downloadable or redistributable under one license.
- **Recommendation:** Use an explicitly licensed WoSIS snapshot for a soil-data pipeline prototype and schema testing. For a useful local model, collect contemporary, georeferenced lab samples from the intended pilot farms, including lab method, depth, date, units, and uncertainty.

### Kerala Agricultural University (KAU) - crop guidance and observations

- **Official source:** [KAU](https://kau.in/).
- **Access check:** The official homepage was reachable and exposed a current observatory weather summary, but this check did not verify a downloadable, versioned historical weather dataset or a stable public API. No crop guide, variety table, or pest/disease dataset was downloaded in this audit.
- **Coverage/use:** KAU is an appropriate Kerala-specific publisher to consult for crop practices and varieties. Treat individual publications as source documents; capture publication date, crop/variety, geography, units, and cited authority before adding agronomic profile claims.
- **License/limitations:** The applicable license and reuse conditions must be checked on each publication or dataset. A public webpage is not blanket permission to redistribute its contents.
- **Status:** Research source identified; structured data availability and per-document licensing remain unverified. No KAU values were entered into the crop catalogue.

### Soil Health Card / project laboratory data - needed local labels

- **Official portal:** [India Soil Health Card](https://soilhealth.dac.gov.in/).
- **Availability:** The portal is a potential government reference for the Indian soil-testing program, but a public, bulk, geospatially joinable export/API was not verified in this research. Treat records as requiring authorized access or direct collection from participating labs, not as an available open training file.
- **Required collection schema:** sample ID, coordinates and positional accuracy, farm/plot ID, collection date, depth/horizon, crop/season, SOC/organic carbon, pH, total and/or available N/P/K as explicitly measured, units, extraction/analysis method, lab, quality-control flags, and permission to use/share.
- **Critical comparability issue:** "P" or "K" alone is not a reproducible label. Record the chemical fraction and extraction method (for example available vs total, and the lab protocol); values from different methods may not be comparable.

## 2. Satellite intelligence

### Copernicus Sentinel-2 Level-2A surface reflectance

- **Official sources:** [Copernicus Data Space Sentinel-2 documentation](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html), [OData catalogue API](https://documentation.dataspace.copernicus.eu/APIs/OData.html), [STAC catalogue](https://browser.stac.dataspace.copernicus.eu/collections/sentinel-2-l2a), [registration](https://documentation.dataspace.copernicus.eu/Registration.html), [token documentation](https://documentation.dataspace.copernicus.eu/APIs/Token.html), [Copernicus Data Space terms](https://dataspace.copernicus.eu/terms-and-conditions).
- **Access:** Search/download through OData or STAC. A Copernicus Data Space account and expiring access token are required for product downloads; this is account authentication, not an API key. Do not hardcode the username, password, or token.
- **Coverage/resolution/time:** Global land-monitoring mission. Sentinel-2 L1C is available globally from 2015; L2A provides atmospherically corrected surface reflectance and scene-classification (SCL) output. The MSI has 13 bands at 10 m, 20 m, and 60 m native resolutions; nominal revisit varies by latitude and constellation.
- **Features:** NDVI = `(B08 - B04) / (B08 + B04)`. A common BSI definition is `((B11 + B04) - (B08 + B02)) / ((B11 + B04) + (B08 + B02))`. Record the exact formula. B02/B04/B08 are 10 m; B11 is 20 m, so BSI requires a documented common grid/resampling choice. The existing soil trainer's red-edge inputs can use B05/B06; its SWIR inputs can use B11/B12. Record product baseline, reflectance scaling, projection, acquisition time, and masks.
- **Cloud/missing data:** Mask clouds, cirrus, cloud shadows, snow, and invalid pixels using SCL/quality layers. A missing valid pixel is not zero reflectance. Composite windows must follow crop calendar and avoid future imagery relative to the prediction date.
- **License:** Copernicus Data Space terms state that Sentinel data are free, full, and open under the Sentinel Data Legal Notice. The linked notice was not text-verified for version-specific wording in this audit. Attribute the source and review that notice for the selected asset. Other portal content has separate terms.
- **Recommendation:** Start with a single pilot farm/region and a crop-season-specific L2A composite. Do not download global archives. Keep red-edge/SWIR and indices at an explicitly chosen common resolution.

## 3. Weather and precipitation

### Open-Meteo Historical Weather API

- **Official sources:** [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), [forecast API](https://open-meteo.com/en/docs), [terms and usage limits](https://open-meteo.com/en/terms).
- **Access/key:** Public HTTP API; no API key is documented for the free tier. The free API is restricted to non-commercial use and has published rate/call limits (including 10,000 calls/day, 5,000/hour, and 600/minute). Commercial use requires an appropriate paid plan; no paid service was used in this work.
- **Coverage/time:** Global historical reanalysis. The current docs list ERA5 from 1940 at 0.25 degrees and ERA5-Land from 1950 at 0.1 degrees, plus newer model products from 2017 onward. The selected model determines resolution, variables, and update latency.
- **Fields/units:** Temperature, precipitation, humidity, radiation, wind, evapotranspiration, soil temperature/moisture, and other model-dependent fields. Request and store the response's units, model name, timezone, and coordinates. Reanalysis values are estimates, not station observations.
- **License/limitations:** API data are offered under CC-BY 4.0, with attribution; free-service use is non-commercial under the API terms. Availability/accuracy are not guaranteed. Avoid mixing changing forecast models when building long historical series.
- **Recommendation:** Use for low-volume, non-commercial prototyping and weather feature extraction. For commercial production, resolve the license/plan first; do not silently rely on the non-commercial free tier.

### ECMWF/Copernicus ERA5-Land

- **Official sources:** [ERA5-Land dataset page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land), [CDS API instructions](https://cds.climate.copernicus.eu/how-to-api).
- **Access/key:** Register for a Climate Data Store account, create/store a personal access token outside the repository, accept the dataset Terms of Use, and use the CDS API client. The dataset page generates the exact request. No token was available or used.
- **Coverage/resolution/time:** Global land fields, hourly, January 1950 to present; 0.1-degree grid, with approximately 9 km native resolution. Data are distributed in GRIB.
- **Fields/units:** Land-surface and near-surface variables, including four soil layers (0-7, 7-28, 28-100, 100-289 cm) and 2 m atmospheric fields. Raw units vary by variable (for example, temperature vs accumulated precipitation); preserve the catalog's variable/unit metadata and convert deliberately.
- **Limitations/license:** Reanalysis is a model-based estimate influenced indirectly by observations. Uncertainty increases farther back in time; it is not a farm weather station. Dataset terms must be accepted and retained. Check the dataset's current license/attribution notice at download rather than assuming a generic license.
- **Recommendation:** Prefer for reproducible historical training inputs and climate baselines, with a small AOI/time request. Open-Meteo ERA5-Land is simpler for point queries; direct CDS is preferable when retaining a source dataset and request provenance.

### NASA GPM IMERG precipitation

- **Official sources:** [NASA GPM IMERG overview and downloads](https://gpm.nasa.gov/data/imerg), [NASA Earthdata Search](https://www.earthdata.nasa.gov/data/tools/earthdata-search), [Earthdata Login](https://www.earthdata.nasa.gov/data/earthdata-login), [NASA data-use guidance](https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance).
- **Access/key:** NASA Earthdata Login registration is required to download Earth science data. This is an account, not a separate paid API key. Some PPS access paths require additional registration.
- **Coverage/time:** Multi-satellite precipitation estimates over most of Earth's surface. NASA describes a continuous record spanning the TRMM era (1998-2015) and the GPM era (2014-present). Product families include half-hourly, 3-hourly, daily, and monthly formats; the spatial grid and exact date coverage depend on the product/version.
- **Fields/units/latency:** Precipitation rate or accumulation, depending on product. Early, Late, and Final runs trade latency against processing quality; NASA recommends Final for research where latency is not critical. Some files use scale factors, so read product metadata before conversion.
- **License:** NASA ESDIS guidance says NASA-led mission data without a marked restriction are generally CC0, but it explicitly defers to product-specific restrictions and third-party rights. The exact IMERG product notice was not verified; no acquisition is approved on the basis of the general guidance alone.
- **Recommendation:** Use as a rainfall-extreme/precipitation complement, not as a substitute for temperature, humidity, or local gauges. Start with daily aggregation and compare against a local station where possible.

## 4. Crop disease image data

### PlantVillage

- **Sources:** [Author-maintained GitHub repository](https://github.com/spMohanty/PlantVillage-Dataset), [Hugging Face dataset mirror/card](https://huggingface.co/datasets/mohanty/PlantVillage), [original paper](https://doi.org/10.3389/fpls.2016.01419).
- **Availability/labels:** The current upstream README reports 54,306 images, 14 crop species, and 26 diseases. The Hugging Face card lists 38 healthy/disease labels and train/test splits of 43,596/10,709 examples (one fewer than the upstream headline count); honor its `leaf_id` grouping and resolve this count discrepancy against the actual manifest before use. The card reports an approximately 2 GB download.
- **Access/license:** Public repository and mirror, no API key. The Hugging Face card declares CC-BY-SA-3.0; the upstream repository has no `LICENSE` file at the checked path (raw LICENSE request returned 404). Do not assume the mirror grants rights to all underlying images. Keep this dataset out of a commercial model until rights and share-alike obligations are reviewed.
- **Limitations:** Mostly controlled leaf/background conditions; no reliable farm GPS, capture date, or field-management metadata. Its class distribution is uneven and its visual domain does not represent field phone photos.
- **Leakage warning:** Several images can show the same physical leaf. Use the supplied leaf-grouped split/`leaf_id`, not a random image split. The existing `train_disease_model.py` makes a random per-image split and does not read `leaf_id`; change the split logic before any training/evaluation.
- **Recommendation:** First controlled benchmark only, using the published grouped split. Keep the official test set untouched.

### PlantDoc

- **Sources:** [PlantDoc classification dataset and license](https://github.com/pratikkayal/PlantDoc-Dataset), [separate object-detection dataset](https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset), [paper](https://doi.org/10.1145/3371158.3371196).
- **Availability/labels:** The classification repository reports 2,598 images, 13 plant species, and up to 17 classes. It contains train/test folders; the object-detection data are a separate repository.
- **Access/license:** Public GitHub download, no API key. The repository declares CC-BY-4.0. Cite the authors and retain attribution; because the images were scraped from the internet, verify underlying image rights before redistribution or commercial use.
- **Limitations:** Small, class-imbalanced, web-sourced images with variable label quality and weak location/time provenance. It is not a representative India field survey.
- **Recommendation:** Use only as a small field-style external evaluation/transfer set after class mapping and duplicate checks. A locally collected, expert-confirmed field test set is still needed for deployment claims.

## 5. Historical crop yield

### FAOSTAT Crops and Livestock Products (QCL)

- **Sources:** [FAOSTAT QCL domain](https://www.fao.org/faostat/en/#data/QCL), [FAOSTAT statistical database terms](https://www.fao.org/contact-us/terms/db-terms-of-use/en).
- **Access:** Public FAOSTAT download interface provides machine-readable datasets; no API key is required for the portal/bulk download. The legacy API service was not verified in this research and should not be assumed operational.
- **Coverage/labels:** Global, more than 245 countries/territories, 1961 to the most recent available year (varies by country/item). QCL contains crop items, area harvested, production, and yield elements, with country/year dimensions.
- **Units/license:** Preserve the returned element and unit field; do not assume one yield unit across all downloads. FAO statistical datasets are CC-BY-4.0 unless metadata says otherwise, with additional database terms, attribution, third-party exceptions, and restrictions against implying FAO endorsement.
- **Current access and use check:** The official QCL page and FAO database terms were reachable; a HEAD request to the official QCL bulk ZIP returned HTTP 403, so no archive was acquired. FAO's additional terms prohibit use in conjunction with promoting a commercial enterprise, product, or service, and third-party data may have different rights. Resolve intended use and item-level metadata before using this source; do not treat CC-BY alone as clearance for a commercial AgroSense product.
- **Limitations:** National annual aggregates are too coarse for plot-level predictions and conceal within-country climate, irrigation, and management variation. Reporting delays, revisions, and crop-definition differences require provenance.
- **Recommendation:** Use as a global/India national sanity-check baseline, not as a local farm training target.

### India district/season crop production statistics

- **Candidate official source:** Ministry of Agriculture and Farmers Welfare / data.gov.in, [District-wise, season-wise crop production statistics from 1997](https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997).
- **Access:** The data.gov.in API generally uses a resource ID and a user API key. The catalog page returned HTTP 403 in this research environment; the project has no non-empty API key. The resource schema, current update status, license, and exact API response could not be inspected. Treat this as a candidate, not yet a validated download.
- **Likely modeling use:** If the current resource includes area and production by state/district/year/season/crop, derive yield only as production divided by harvested area after verifying both units and excluding missing/zero area. Do not label the derived value as a directly measured yield.
- **Recommendation:** This is the preferred local-yield candidate if the resource has adequate district coverage and stable units. First obtain a small sample through the official catalog, record field definitions/revisions, and reconcile district boundaries and crop years. Use FAOSTAT as the independent national check.

## 6. Market prices and arrivals

### AGMARKNET / data.gov.in mandi prices

- **Sources:** [AGMARKNET 2.0](https://agmarknet.gov.in/), [data.gov.in current daily mandi price resource](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi), [data.gov.in API portal](https://www.data.gov.in/apis).
- **Access/key:** data.gov.in's resource API requires an API key. The public endpoint form is `https://api.data.gov.in/resource/<resource-id>?api-key=<YOUR_KEY>&format=json&limit=...`; store the key in an environment/secret manager only. The AGMARKNET home page was reachable, but its dynamic data interface was not validated here. The data.gov catalog returned HTTP 403 and a no-key API probe returned HTTP 400.
- **Data fields/units:** The resource is a daily commodity/market price feed. Validate the live schema before ingestion, particularly state/district/market identifiers, commodity/variety, arrival date, min/max/modal price, currency, and price unit. Do not assume that a price row contains an arrivals quantity. Arrival quantity needs a separately identified, licensed resource and its own units.
- **License/availability:** The current catalog/license and API response were not readable from this environment. Check the individual resource terms and National Data Sharing and Accessibility Policy notice before reuse or redistribution; do not assume every portal resource has identical terms.
- **Quality risks:** Market closures and no-quote days are missing observations, not zero prices. Check price outliers, variety and grade changes, market-code changes, arrival-vs-trade date, unit/currency consistency, and revisions. Use inflation-adjusted prices for long periods and avoid future-date leakage.
- **Recommendation:** Start with one commodity, state, and market group; separately ingest prices and arrivals only after verifying their resource schemas and rights. Use modal price as an observed market quote, not a guaranteed farm-gate sale price.

## 7. Can lab labels be matched to Sentinel-2?

Yes, conditionally. A match is technically possible when a laboratory sample has trustworthy coordinates, collection date, depth, plot identity, and analytical method, and a valid Sentinel-2 L2A observation/composite exists for the same field and relevant period. It is not a reliable join on district name alone.

1. Retain the sample's GPS accuracy and make the plot polygon/point geometry explicit. Soil-profile positional uncertainty in WoSIS can be large enough to make 10-20 m pixel assignment ambiguous.
2. Keep horizons and lab methods distinct. Match the laboratory depth to the intended SoilGrids depth only as an explicit mapping, not by silently equating unlike intervals.
3. Use a season-appropriate cloud-free composite. For soil property models, vegetation canopy often obscures the soil signal; bare-soil windows or soil-specific features may be necessary. For crop/yield tasks, use crop-calendar windows and only imagery available at the prediction cutoff.
4. Resample 10 m and 20 m bands to one declared analysis grid and aggregate pixels over the farm/plot rather than selecting a single arbitrary pixel.
5. Prevent circular labels: SoilGrids is itself a model built from soil observations. Do not evaluate a SoilGrids-trained target against source profiles that may have informed SoilGrids without a source-aware independent split.

There are currently no project lab samples, plot-season image features, or documented matching records in the repository. This join is therefore a design path, not a completed dataset.

## 8. Availability and credentials checklist

| Source | Publicly discoverable now | Credentials for bulk/API access |
|---|---|---|
| SoilGrids REST/layers | Yes; current OpenAPI and layer metadata retrieved | No API key documented; verify operational limits |
| WoSIS profiles | Yes, subject to provider-specific release terms | Public services documented; no general API key documented |
| Sentinel-2 via Copernicus Data Space | Yes | Registered account + access token; no API key |
| Open-Meteo free API | Yes | No key; free tier is non-commercial and rate-limited |
| ERA5-Land via CDS | Yes | CDS account + personal access token + dataset terms acceptance |
| NASA GPM IMERG | Yes | Earthdata Login for downloads; not a paid API key |
| PlantVillage / PlantDoc | Yes, public author/research repositories | No API key; observe dataset/image licenses |
| FAOSTAT QCL | Yes | No key for portal/bulk downloads; legacy API not verified |
| India data.gov.in yield/mandi resources | Catalog page returned HTTP 403; live schema not verified | API key required; project key setting is empty |
| India soil laboratory labels | Not verified as an open bulk training dataset | Obtain lab partnership, permissions, and georeferenced samples |

## 9. Data-quality and leakage controls

- **Spatial leakage:** Random rows from neighboring fields or horizons can land in both train and test. Split by profile, farm, district/spatial block, and preferably time; keep all horizons from one profile together.
- **Soil target leakage:** SoilGrids predictions are not independent lab labels. Do not train/evaluate a model using a SoilGrids value as its target and a related SoilGrids feature, or mix source profiles across folds.
- **Image leakage:** PlantVillage has multiple images per physical leaf. Honor its leaf IDs and published grouping. Deduplicate exact hashes and near-duplicates across PlantVillage/PlantDoc and across split directories.
- **Class/geography bias:** Image datasets overrepresent certain crops, diseases, controlled backgrounds, and web image sources. Audit per-class counts and source provenance; keep an independently collected field test set.
- **Temporal leakage:** Never use weather, satellite composites, market prices, or crop revisions from after the intended forecast cutoff. Prefer chronological holdouts.
- **Spatial/temporal resolution mismatch:** Sentinel pixels, 250 m SoilGrids cells, approximately 9 km ERA5-Land cells, district yield statistics, and market-day prices represent different spatial/temporal supports. Keep each support explicit.
- **Missingness/units:** Keep missing as missing, not zero. Preserve original unit strings, source version, method, quality flags, dates, crop/market codes, and transformations in a dataset manifest.
- **Dataset revisions:** Pin versions/snapshots and download dates. Avoid training on a moving API response without storing its source identifiers and retrieval metadata.

## 10. Recommended low-RAM download and validation plan

1. Choose one pilot district, crop, crop season, and prediction question. Do not begin with country/global raster or image downloads.
2. Create a manifest before data extraction: source URL/DOI, dataset/resource ID, version, license, attribution, retrieval date, fields/units, geographic/time filters, and file checksums.
3. Validate one small record/sample per source:
   - SoilGrids: request only required properties/depths and verify units/scaling.
   - WoSIS/lab: inspect provider license, methods, dates, coordinates, uncertainty, and depth coverage.
   - Sentinel-2: select one AOI/season, use L2A/SCL, calculate bands/indices on a declared 20 m grid.
   - Weather: request only required variables and date range; record model, units, timezone, and data source.
   - Plant disease: inspect license, class counts, hashes, leaf IDs, and split membership before image decoding.
   - Yield/market: validate current India catalog schema and resource license before requesting bulk data.
4. Keep raw source files immutable and separate from cleaned features. Write derived tables/manifests with source IDs; never overwrite source labels with harmonized values.
5. Keep raster work windowed/subsetted and images on disk. Use streaming or small batches; do not load full satellite archives or all images into RAM.
6. Do not put API keys/tokens in this repository. Store data.gov/CDS/Copernicus/Earthdata credentials in local environment or an approved secret manager, and keep them off the frontend.

## 11. Recommended model plan (no training performed)

- **Soil regression:** First build a georeferenced lab dataset and method/unit harmonization. Use SoilGrids only as a baseline/covariate with its uncertainty, and collect P/K labels from labs. Split by spatial block/profile and test on later or held-out farms. The current `backend/scripts/train_soil_model.py` expects blue/green/red/red-edge/NIR/SWIR/elevation/slope plus SOC, pH, N, P, K; it does not yet encode source versions, units, sample date/depth, or spatial-group splits.
- **Satellite indices:** Start with deterministic NDVI/BSI and quality-controlled time-series summaries, not a learned model. Validate index behavior on the pilot AOI and crop calendar first.
- **Weather:** Benchmark a transparent climatology/persistence baseline against selected Open-Meteo/ERA5-Land variables using chronological holdouts. Use IMERG for precipitation-focused comparisons.
- **Disease:** Use PlantVillage's leaf-grouped split for a controlled benchmark; evaluate separately on PlantDoc and then on expert-confirmed local field photos. Before training, update the existing image trainer to respect supplied splits/leaf IDs, report per-class metrics, and audit duplicates. For heavy runs, use Colab or Kaggle; keep batches small and images streamed from disk.
- **Yield:** Define the target explicitly as production/area with a verified unit and crop-season-year. Start with a simple tabular baseline; use year-forward and district/farm holdouts, not random rows. Exclude inputs unavailable at the forecast issue date.
- **Market:** First validate a clean market/commodity/variety time series. Compare seasonal-naive baselines with carefully time-split features; distinguish modal wholesale price from farm-gate revenue and arrival volume.

No model was trained, no accuracy is claimed, and no inference integration is enabled by this inventory.

## 12. Blockers before data ingestion

1. Confirm pilot geography, crops, seasons, and whether intended use is commercial; this determines whether non-commercial-only services and FAO's additional terms are compatible.
2. Obtain authorized, georeferenced soil laboratory samples with documented P/K fractions and methods; public global datasets are not a substitute for local labels.
3. Obtain an authorized data.gov.in API key and confirm yield and mandi resource availability, exact schemas, units, license, and update cadence.
4. Confirm PlantVillage mirror licensing is acceptable for the intended distribution; collect a locally representative expert-labeled disease test set.
5. Define common spatial/temporal supports, crop calendars, missing-data policy, and model evaluation splits before feature extraction.
6. Obtain and securely configure only the required account credentials/tokens; none are included in source code or this inventory.

## Source notes

Source documentation and accessible dataset pages were checked on 2026-11-19. Public documentation being reachable does not guarantee service uptime or permission to redistribute all contents. In particular, data.gov.in catalog/API details and Soil Health Card bulk access could not be verified from this research environment; validate them manually before implementation.
