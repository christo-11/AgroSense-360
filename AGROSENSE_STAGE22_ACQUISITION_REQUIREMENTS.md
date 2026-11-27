# AgroSense-360 Stage 22 Acquisition Requirements

**Stage:** 22  
**Scope:** Official data acquisition requirements only  
**District:** Idukki remains provisional  
**Status:** Permission gate pending; no acquisition authorized

## Objective

Define exactly what evidence is required before AgroSense-360 may acquire any source for the black-pepper pilot. This document does not assert that any dataset exists or that any owner has granted permission.

## Required acquisition domains

| Requirement | Official data owner(s) | Exact dataset/publication needed | Geographic scope | Time period | Minimum fields | Permission/evidence needed |
|---|---|---|---|---|---|---|
| Idukki black-pepper cultivation evidence | Kerala Department of Agriculture; KAU; ICAR-IISR | Exact published district/crop evidence or authorized administrative release | Idukki, Kerala | Effective publication and observation dates | Crop, variety if recorded, district, area/number of holdings or cited finding, publication date, method | Written resource terms; exact title/version; attribution; research/training/commercial scope |
| District production and productivity | Directorate of Economics & Statistics, Kerala; data.gov.in/MoA&FW; Kerala Department of Agriculture | District-wise, season-wise crop production and area/yield resource | Idukki and preferably Kerala districts for comparison | At least 10 complete crop-years once season is approved | District, crop, variety if present, season/crop-year, area, production, yield or derivation rule, units, revisions, missing flags | Resource-specific licence/API terms, API/key authorization, exact resource ID, version and redistribution permission |
| Variety and cultivation practices | ICAR-IISR; KAU | Exact package of practices, variety release catalogue or research publication | Kerala, with Idukki applicability separately documented | Publication/revision date | Variety name, release authority, year, district applicability, planting/harvest season, spacing, shade/water/fertilizer practices, source method | Publication reuse terms, attribution, exact edition, permission for ML features if claimed as structured data |
| Soil measurements | Soil Health Card/lab authority; participating university/lab; ISRIC for provider-specific profiles | Georeferenced authorized soil laboratory observations or selected WoSIS profiles | Idukki plots/sites or verified Kerala profiles | Collection date and retained sample history | Sample ID, crop/variety, coordinates/accuracy, collection date, depth, analyte, fraction, unit, analytical/extraction method, lab/QC, uncertainty | Written owner/record-level reuse, privacy review, redistribution, research, training and commercial decisions |
| Rainfall and temperature | IMD | Authorized historical station/gauge/temperature release or exact weather export | Idukki and identified nearby independent stations | At least 10 complete crop-years for daily model research | Station ID/name, coordinates/elevation, date/time, variable, unit, interval, accumulation semantics, quality flags, relocations | Exact data release/terms, citation, redistribution and training permission |
| Humidity and other weather | IMD or an explicitly authorized reanalysis owner | Historical humidity/wind/pressure/solar-radiation dataset if required by the scientific question | Idukki or validated station coverage | Same approved period as rainfall/temperature | Variable, unit, UTC/local time semantics, quality, station/grid support | Resource-specific terms, model version or station provenance, independent validation |
| Rainfall model feature estimate | Copernicus CDS or NASA GPM, if separately approved | ERA5-Land or GPM exact pinned product subset | Idukki; native grid and mask | 10 complete crop-years or approved alternative | Product version, request parameters, variable, unit, timestamp, grid ID/CRS, missingness | Licence acceptance, third-party terms, commercial approval, quality and independent validation |
| Disease/pest observations | ICAR-IISR; Kerala Department of Agriculture; authorized extension/lab institutions | Expert-labelled field surveys or verified disease/pest records | Idukki plots/administrative units | Observation dates and season | Sample/site ID, crop/variety, disease/pest name, diagnostic method, severity/score, date, coordinates/accuracy, image or record ID | Data owner permission, privacy, expert review, image rights, redistribution and training approval |
| Yield/productivity validation | Directorate of Economics & Statistics; Department of Agriculture; approved research institutions | District/plot yield records with denominator and method | Idukki first; Kerala as later comparison | 10 complete crop-years where available | Crop/year/season, area, production, yield, unit, reporting method, revisions, missing flags | Exact resource release/terms and administrative source approval |

## Required acquisition metadata for every release

- Stable source ID and dataset name.
- Publisher and exact responsible data owner.
- Dataset/resource ID and release/version.
- Publication, effective and retrieval dates.
- Official resource URL and, if applicable, API endpoint.
- Licence name, licence version/URL and exact rights snapshot.
- Attribution and no-endorsement requirements.
- Portfolio/research, commercial, redistribution and ML-training decisions.
- Geographic coverage and projection/boundary version.
- Temporal resolution, interval, timezone and crop-season definition.
- Schema, units, quality flags and missing-value codes.
- File format and checksum.
- Retrieval method and immutable raw-data path or external storage location.
- Reviewer, review date and remaining concerns.

## Record-level data requirements

### Production/administrative records

No production or yield record may be ingested until crop, district, season, units, denominator and reporting year are verified. A derived yield value must retain area and production inputs and the formula.

### Soil records

Reject any soil row lacking:

- Sample ID and spatial reference.
- Collection date.
- Depth interval.
- Analyte or property.
- Analytical/extraction method or fraction.
- Unit.
- Lab/QC status.
- Crop/site context where it is claimed to be linked to black pepper.
- Written reuse permission.

### Weather records

Each row or grid message must identify:

- Station or native grid-cell ID.
- UTC timestamp and interval.
- Variable and source unit.
- Accumulation or instantaneous semantics.
- Provider quality flag and local missing reason.
- Spatial support and boundary or station metadata.
- Product/model version if estimated.

### Disease/pest records

No diagnosis may be inferred from an image label alone. Require crop/variety, observation date, geographic support, diagnostic authority or method, severity definition and uncertainty.

## Acquisition gate

Acquisition may begin only after all of the following are recorded:

1. Exact owner and resource.
2. Exact licence/terms and intended use.
3. Idukki or approved replacement district evidence.
4. Crop-specific relevance and schema.
5. Temporal and spatial coverage.
6. Data quality and missingness evidence.
7. Provenance and checksum plan.
8. Project owner approval to inquire or acquire.

No gate item is optional or inferred from public availability.
