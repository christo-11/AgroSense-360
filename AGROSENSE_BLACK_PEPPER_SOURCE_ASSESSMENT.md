# AgroSense-360 Black Pepper Pilot Source Assessment

## Decision summary

No source currently establishes black-pepper suitability or soil conditions in Idukki. The source inventory contains candidate resources and rights-review status; it does not contain black-pepper field observations. Do not acquire or train on any source until the exact resource/version, intended-use terms, and data-quality evidence have been reviewed.

`APPROVED_PORTFOLIO_RESEARCH_ONLY` means only portfolio/research use under documented conditions. It is not commercial approval, permission to redistribute, or ML-training approval. Existing inventory training quality/relevance fields for the candidate sources are `NOT_ASSESSED`; ERA5-Land's current archives are separately `REJECT_FOR_TRAINING`.

## Candidate source ledger

| Source / owner | Dataset and version | Geographic relevance | License and attribution | Portfolio / research | Commercial use | ML training | Limitations and missing evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Kerala Agricultural University (KAU)** | “Kerala Agricultural University extension and observatory information”; no versioned historical export identified | Kerala observatory locations and crop guidance vary by publication; no Idukki black-pepper record identified | No resource-specific license verified. Require the exact publication/export terms and attribution before reuse. | `UNVERIFIED` | `CONDITIONAL` | `NOT_ASSESSED` | Existing inventory describes a current observatory summary, not a verified historical series. Need the exact black-pepper publication/dataset, release/date, district evidence, station metadata, and written reuse terms. |
| **ECMWF / Copernicus Climate Data Store** | ERA5-Land hourly product; product/version and exact request parameters unresolved; two archives already exist | Global 0.1-degree grid intersects Kerala, but no Idukki boundary/cell-value assessment was made | Copernicus Licence to Use Products v1.2 and CDS terms; retain required C3S attribution/disclaimer and product terms. | `APPROVED_PORTFOLIO_RESEARCH_ONLY` | `CONDITIONAL` | `NOT_ASSESSED` in source inventory; current archive quality is `REJECT_FOR_TRAINING` | Two archives are sparse and irregular; 65.87% global-grid missingness. Existing file presence/integrity does not establish local weather quality or suitability. Exact request history/product version remain unresolved. |
| **ISRIC** | SoilGrids 2.0; no project snapshot/version pin and inventory status `metadata_verified_only` | Global modeled maps at nominal 250 m; no local black-pepper sample records | ISRIC data policy; exact applicable product license was not text-verified. Retain product attribution and verify exact terms. | `CONDITIONAL` | `CONDITIONAL` | `NOT_ASSESSED`; source review labels it `NOT_LAB_GROUND_TRUTH` | No local value raster/sample acquired. Model outputs are estimates, not soil lab measurements. Repository source review does not list phosphorus or potassium layers. Need exact product release, layer units/scaling, local validation, and license evidence. |
| **ISRIC and contributing data providers** | World Soil Information Service (WoSIS); selected snapshot/profile not identified | Global soil profiles; no verified Idukki/black-pepper profile identified | Contributor-specific terms; no single WoSIS-wide license. Preserve contributing-provider citation and terms. | `UNVERIFIED` | `CONDITIONAL` | `NOT_ASSESSED` | No profile data acquired. Need exact permitted profile(s), location accuracy, sample date, depth, analytical method, units, and redistribution/training permission. |
| **Government of India, Department of Agriculture and Farmers Welfare / Soil Health Card or participating lab** | No exact dataset release/export identified | India portal; local georeferenced Idukki black-pepper sample coverage not verified | Dataset-level license and bulk-export terms not verified; obtain authorization and record-level privacy/reuse terms. | `UNVERIFIED` | `CONDITIONAL` | `NOT_ASSESSED` | No soil measurements in the repository. Need authorized lab records with coordinates/accuracy, sample date, depth, pH, organic carbon, N/P/K fractions and methods, units, lab QC, crop/site linkage where recorded, and reuse permission. |
| **Government of India, Ministry of Agriculture and Farmers Welfare / data.gov.in** | “District-wise, season-wise crop production statistics from 1997”; current resource version/schema not verified | India district-level candidate; Kerala/black-pepper rows not verified | Resource-level license and attribution not verified; prior catalog access returned 403. Do not infer a portal-wide license. | `UNVERIFIED` | `CONDITIONAL` | `NOT_ASSESSED` | Could help test district-level production evidence only if the resource has relevant crop/year/district fields and permitted use. No resource data was requested. Need schema, Kerala coverage, units, revisions, API terms, and attribution. |
| **NASA** | GPM IMERG Final Run; V07B named in inventory, no project asset/snapshot acquired | Broad regional precipitation estimates; no Idukki pixel validation | GPM/TRMM data-use policy and NASA ESDIS guidance; cite the product/version and verify product-specific terms. Not assumed CC0. | `APPROVED_PORTFOLIO_RESEARCH_ONLY` | `CONDITIONAL` | `NOT_ASSESSED` | Rainfall-focused estimate only; not a full weather record and never soil truth. No project data file, local gauge comparison, or asset metadata. |
| **Open-Meteo** | Historical Weather API; exact model/version and query response not pinned | Global model data; local resolution/coverage depends on selected product | API data listed as CC BY 4.0 with attribution; free API terms are non-commercial. Commercial use requires a separate plan/decision. | `APPROVED_PORTFOLIO_RESEARCH_ONLY` | `BLOCKED` for the free tier / pending commercial decision | `NOT_ASSESSED` | No external API request was made. Not a current project dataset; model and response provenance must be pinned. Portfolio approval does not grant training permission. |

### Current source status counts

The machine-readable inventory contains 13 candidates. At the repository's recorded review state, three have portfolio/research-only approval; portfolio status for other candidates is conditional, blocked, or unverified. Commercial review has 11 `CONDITIONAL`, 2 `BLOCKED`, and 0 `APPROVED`. No candidate is currently approved for ML training. These inventory statuses are not a fresh legal review.

## Exact evidence and permissions required before requesting data

### 1. District/crop evidence for Idukki

- **Candidate source:** a KAU or other Kerala agricultural authority publication/record that explicitly covers black pepper in Idukki; the current KAU inventory entry is only a general publisher/source candidate, not an identified title or dataset.
- **Required citation fields:** exact title, publisher, edition/version/date, crop/variety, geography, method, and statement supported.
- **Permission required:** resource-specific written reuse/attribution terms for portfolio display; separate explicit ML-training and commercial-use decisions. Current license and permission: **not verified**.
- **Do not request or imply a KAU-held dataset exists** until the owner confirms the exact resource.

### 2. Weather for the pilot site

- **Existing exact resources:** `era5_land` source inventory entry and two archived requests. Both remain unusable for training under the existing quality decision; exact request parameters and product version need resolution from already-held provenance, not a new CDS request.
- **Possible additional source:** a versioned KAU observatory or India Meteorological Department historical station/gauge export covering the intended pilot area and period. The current inventory does not identify an authorized historical Idukki black-pepper dataset.
- **Required record fields:** station ID and owner, coordinates/accuracy/elevation, observation dates/time zone, variables/units/interval semantics, station history, quality flags, source/version, and independent-use permission.
- **Permission required:** retain the exact dataset-specific terms, attribution, and permission for portfolio/research use. Training or commercial use requires separate approval. None was requested in this stage.

### 3. Soil measurements

- **Requested dataset specification:** georeferenced soil-laboratory samples for the pilot sites, linked to black-pepper plots only where that crop link is actually documented.
- **Potential owners:** authorized Kerala agricultural/university laboratories, participating farms/labs, or the Government of India's Soil Health Card program. No exact Idukki black-pepper dataset was identified in the repository.
- **Required fields:** sample ID, coordinates and positional accuracy, collection date, depth/horizon, analyte, unit, method/extraction/fraction, lab and QC, source/version, crop/site context where known, and permission to use/share.
- **Permission required:** written data-owner and record-level reuse permission; explicitly resolve privacy, redistribution, research training, and commercial use. Current license/permission: **not verified**.
- **Model estimates:** SoilGrids may only be considered as a separately labeled estimate/covariate after exact product terms, version, units/scaling, and local validation are confirmed; it cannot substitute for measured pH/N/P/K. No acquisition request is made.

### 4. Crop production records

- **Candidate exact inventory resource:** Ministry of Agriculture and Farmers Welfare / data.gov.in, “District-wise, season-wise crop production statistics from 1997.”
- **Required verification:** confirm resource ID/version, Kerala and Idukki coverage, exact black-pepper item labels, crop-year/season definitions, area/production units, revisions, missingness, and whether yield is directly reported or derived.
- **Permission required:** verify the resource-level license/attribution and API terms before any access. The current inventory notes the resource page was inaccessible in the prior review; no API key or request was used in Stage 19.
- **Do not calculate or fabricate production/yield** until schema, denominator, units, and source records are available and reviewed.

## Data-use decision

| Use | Decision now | Reason |
| --- | --- | --- |
| Portfolio dashboard explaining evidence gaps | Permitted within existing source-specific conditions | It can display statuses and known archive limitations without inventing agricultural facts |
| Claim that black pepper is suitable for Idukki | Not supported | No source-backed district/crop relationship found |
| Soil ground truth | Not available | No authorized, measured, depth/method-documented soil samples are present |
| Use of existing ERA5-Land as continuous pilot weather series | Not supported | Extremely sparse temporal coverage and no Idukki mask/independent validation |
| ML training | Not authorized | Existing ERA5 archives rejected; no verified labels or training-approved source |
| Commercial use | Not authorized | No source is commercially approved |

No external source was contacted, no external API or acquisition request was made, and no data was downloaded in Stage 19.
