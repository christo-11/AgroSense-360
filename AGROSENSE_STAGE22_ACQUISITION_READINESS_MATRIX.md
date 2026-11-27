# AgroSense-360 Stage 22 Acquisition Readiness Matrix

**Status policy:** Unknown is never approved.

## Status vocabulary

- `UNKNOWN`: no evidence or decision exists.
- `NOT_FOUND`: no exact record/resource was found.
- `REQUIRES_REVIEW`: exact resource, licence or use decision remains unresolved.
- `CONDITIONAL`: a potentially usable source exists but one or more gates remain unresolved.
- `BLOCKED`: the existing project or source terms prohibit the intended use.
- `APPROVED_FOR_PILOT_RESEARCH`: only exact non-commercial research scope is verified.
- `APPROVED_FOR_TRAINING`: exact signed training approval and provenance/quality gates are satisfied.
- `NOT_ACQUIRED`, `PERMISSION_PENDING`, `ACQUISITION_READY` and `TRAINING_NOT_ELIGIBLE` describe acquisition/training state separately.

## Readiness matrix

| Dataset | Owner | Official URL | Licence | Geographic coverage | Temporal coverage | Required variables | File format | Access method | Permission status | Acquisition status | Training eligibility | Outstanding requirements |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Idukki black-pepper cultivation evidence | Kerala Department of Agriculture; KAU; ICAR-IISR | Owner-specific exact URL not identified | UNKNOWN | Idukki/various Kerala | Publication dates unknown | Crop/variety/district/area or study finding | HTML/PDF/structured export unknown | Owner confirmation | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Exact document, publication date, district evidence, licence and reuse terms |
| District crop production | MoA&FW/data.gov.in or Kerala DES | https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997 | REQUIRES_REVIEW | India candidate; Kerala/Idukki unknown | 1997 onward, current end unknown | District, crop, season, year, area, production, yield, units, revisions | Unknown | Resource API; key normally required | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Resource ID/schema/rows/units/licence/API access |
| Varieties and package of practices | ICAR-IISR; KAU | https://spices.res.in/; https://kau.in/ | REQUIRES_REVIEW per document | Kerala; Idukki applicability unknown | Revision/publication date unknown | Variety, authority/year, season, method, pest/disease/practice fields | PDF/HTML/database unknown | Official publication/export | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Exact edition, Idukki relevance and reuse/training terms |
| IMD station weather | IMD | https://mausam.imd.gov.in/ | REQUIRES_REVIEW for exact release | Idukki/nearby stations unknown | Exact period unknown | T, RH, rainfall, wind, pressure, sunshine, station metadata | CSV/Bulk/NetCDF unknown | Authorized owner export | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Exact station, period, format, quality, terms and independent validation |
| ERA5-Land hourly reanalysis | ECMWF/Copernicus CDS | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land | Licence to Use Copernicus Products v1.2 | Global 0.1 degree land grid | Hourly from 1950 to present, exact request unknown | T, RH, precipitation, wind, pressure, soil moisture/land variables | NetCDF/GRIB | CDS account/request | CONDITIONAL | NOT_ACQUIRED for pilot; 2 existing sparse archives | TRAINING_NOT_ELIGIBLE | Pinned request/version, Kerala mask/quality, independent gauge validation |
| GPM IMERG V07B | NASA GPM/GES DISC | https://gpm.nasa.gov/data/imerg | GPM/TRMM policy; no exact asset licence | Global precipitation grid | V07B product period; exact run unknown | Precipitation rate/accumulation, unit/scale factor | HDF/NetCDF/GeoTIFF | Earthdata/PPS | CONDITIONAL | NOT_ACQUIRED | NOT_ELIGIBLE | Exact asset, date range, units, Kerala gauge validation |
| SoilGrids 2.0 | ISRIC | https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html | Exact output/release terms not verified | Global 250 m | Snapshot/release unknown | pH, SOC, nitrogen, texture, depth, uncertainty | Raster/GeoTIFF/API/JSON | REST or raster export | CONDITIONAL | NOT_ACQUIRED | NOT_ELIGIBLE as ground truth | Licence, product snapshot, P/K limitation, local validation |
| WoSIS profiles | ISRIC/contributing providers | https://docs.isric.org/globaldata/wosis/faq-wosis.html | Contributor-specific | Global point profiles; Kerala/Idukki unknown | Profile sampling dates vary | pH, P, N, texture, carbon, depth, method, uncertainty | CSV/GeoParquet/API unknown | Provider/profile selection | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Kerala/Idukki profiles, per-provider terms, lab methods |
| Soil Health Card/lab records | Govt. of India/participating labs | https://soilhealth.dac.gov.in/ | Dataset/record terms unknown | India; Idukki coverage unknown | Collection dates unknown | pH, N/P/K, organic carbon, depth, method, coordinates, lab/QC | Portal/tabular/export unknown | Authorized owner/lab export | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Written permission, privacy review, georeferenced records |
| Sentinel-2 L2A | Copernicus | https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html | Sentinel legal notice/terms | Global | Exact scene/processing baseline unknown | Bands, indices, cloud mask, timestamp | SAFE/GeoTIFF/JP2 | Copernicus Data Space | CONDITIONAL | NOT_ACQUIRED | NOT_ELIGIBLE | Asset/baseline, Idukki scenes, cloud mask, labels, terms |
| Black-pepper disease/pest observations | ICAR-IISR; Kerala Department/labs | Exact URL unknown | REQUIRES_REVIEW | Idukki/plot unknown | Observation period unknown | Crop/variety, disease/pest, severity, diagnostic method, date, site | CSV/Excel/images/database | Authorized owner export | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Crop-specific field survey, expert validation, privacy/image rights |
| AGMARKNET market prices | MoA&FW/data.gov.in | https://agmarknet.gov.in/ | Unknown | India market level | Current/history unknown | Commodity, variety/grade, market, date, price, units, arrivals | Unknown | API/portal | REQUIRES_REVIEW | NOT_ACQUIRED | NOT_ELIGIBLE | Variety/crop match, Kerala coverage, unit/rights |
| FAOSTAT QCL | FAO | https://www.fao.org/faostat/en/#data/QCL | CC BY 4.0 plus FAO additional terms | Country/territory | 1961 onward by item | Area/production/yield | Bulk/tabular | Public download | BLOCKED for project scope | NOT_ACQUIRED | NOT_ELIGIBLE | Country geography does not support Idukki |
| Open-Meteo historical | Open-Meteo | https://open-meteo.com/en/docs/historical-weather-api | CC BY 4.0; free API non-commercial | Global model | Product-dependent | Weather variables | JSON/API | API | BLOCKED for commercial project | NOT_ACQUIRED | NOT_ELIGIBLE | Paid/commercial decision, model provenance, independent validation |

## Existing acquired asset disposition

The two existing ERA5-Land archives remain recorded and integrity-verified. They are not pilot acquisition candidates for training or district claims. No new asset may be added, downloaded or ingested until the Stage 22/23 gate is approved.

## Potentially usable sources

Only for later pilot research, subject to exact release and permission:

- ERA5-Land for reanalysis covariates after quality and independent station validation.
- GPM IMERG for precipitation estimates after exact asset and validation.
- SoilGrids as a modeled covariate only.
- IMD station observations, if an exact Idukki export is authorized.
- Official crop production or soil records, if exact Idukki/crop links and rights are provided.

No source is currently acquisition-ready.
