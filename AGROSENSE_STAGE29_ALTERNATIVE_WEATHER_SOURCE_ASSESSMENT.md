# AgroSense-360 Stage 29 — Alternative Weather Source Assessment

**Assessment date:** 2026-11-23  
**Purpose:** Compare weather-source candidates for future Kerala/Idukki black-pepper research. This is a source review only: no dataset/API requests, downloads, provider contact, or permission approvals occurred.

## Executive summary

No candidate is approved for acquisition or use by this assessment. The most relevant candidates for future review are:

1. **IMD gridded daily rainfall** for long-period India rainfall context, subject to resource-specific access and use review.
2. **CHIRPS v3** for high-resolution satellite/station-blended rainfall estimates, with its daily-product derivation and licensing conditions explicitly retained.
3. **IMD station observations** as potential local validation evidence, if an exact station series and written/official terms are established.
4. **ERA5 / ERA5-Land** as reanalysis covariates, not ground truth. The existing ERA5-Land archives retain their Stage 28 dispositions: request 1 `ACCEPTABLE WITH LIMITATIONS`, request 2 `REJECTED`; neither is approved for production, decision support, or training.
5. **NASA POWER** as an accessible daily meteorology candidate, with source-grid resolution and upstream data lineage checked for each parameter.
6. **NASA GPM IMERG** as a satellite precipitation estimate, not a local gauge measurement.

All unknown project permissions remain unapproved. “Free,” “open,” a public portal, or a general licence does not by itself satisfy AgroSense-360’s separate acquisition, portfolio, commercial, redistribution, or training gates.

## Candidate comparison

| Candidate / owner | Coverage and resolution | Time step and historical coverage | Variables and access | Licence, attribution and use conditions | Kerala/Idukki relevance and limitations |
|---|---|---|---|---|---|
| **ERA5 hourly single levels — ECMWF/Copernicus CDS**. [Dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) | Global; reanalysis grid 0.25°; ensemble uncertainty products use coarser grids. | Hourly from 1940 onward; the early ERA5T stream is updated with about five-day latency and may later be revised. | Broad atmospheric, land-surface and ocean-wave quantities; CDS web/API access, including GRIB and NetCDF. No request was made. | Copernicus Licence to Use Products; prior project evidence identifies v1.2. The licence is free, worldwide, non-exclusive, royalty-free and perpetual for lawful use; attribution is required, and adapted/publicly distributed products require the prescribed modified-data notice/disclaimer. Flagged third-party products may have separate terms. No project-specific ML approval is recorded. [Licence](https://apps.ecmwf.int/datasets/licences/copernicus/) | Higher grid spacing than ERA5-Land; globally complete reanalysis estimates, not direct observations. Potential alternative/cross-check only after exact request, product version, rights, Kerala validation and quality review. |
| **ERA5-Land hourly — ECMWF/Copernicus CDS**. [Dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) | Global land; distributed grid 0.1°; native resolution about 9 km. | Hourly from January 1950 onward. | Land states, surface and soil variables, with atmospheric forcing inputs; CDS access in GRIB/NetCDF. No request was made. | Copernicus licence and attribution requirements above; product-level/third-party terms must be checked. Licence status is not a quality or training decision. | Finer grid than ERA5, but remains model/reanalysis estimates influenced indirectly by observations. Existing archives are too sparse; request 2 has unresolved GRIB1 header inconsistency. A new complete, authorized request would be a separate decision. |
| **IMD daily gridded rainfall — India Meteorological Department, Climate Research and Services, Pune**. [0.25° rainfall product](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html) | India; 0.25° grid; page describes 135 × 129 grid points. | Daily; 1901–2024 stated on the official page, provided in annual files. | Rainfall in mm; yearly gridded NetCDF access from the official product page. Page requests citation to Pai et al. (2014) and includes an accuracy/liability disclaimer. | Exact dataset licence, commercial-use terms, redistribution and ML-training terms were not established by the reviewed page. Citation is requested, but citation alone is not a reuse licence. **REQUIRES RIGHTS REVIEW.** | Potential long-term regional rainfall context. The grid is a gridded product, not a direct gauge observation at each pixel. Kerala/Idukki cell coverage, underlying station density, completeness and local validation were not evaluated. |
| **IMD station observations and operational weather services — IMD**. [Official portal](https://mausam.imd.gov.in/) | Station- and service-specific; no exact Idukki station inventory, coordinates, or coverage was verified. | Portal exposes current realized weather and forecast/warning services; historical station period and cadence for a reusable dataset remain unknown. | Exact historical variables, formats, access mechanism and quality flags depend on selected station/product. Public interface availability is not evidence of bulk-data rights. No API or data access request was made. | Exact resource terms, attribution, commercial reuse, redistribution and ML-training conditions remain unverified. **REQUIRES RIGHTS REVIEW.** | Highest potential value as local independent comparison if an appropriate station is available, but station metadata, representativeness, history and permission must first be verified. District forecasts/advisories are not a substitute for a measured station time series. |
| **NASA POWER daily meteorology — NASA Langley Research Center POWER**. [POWER documentation](https://power.larc.nasa.gov/docs/) and [Daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Global, parameter-specific source grids; the Daily API documentation describes a 0.5° × 0.5° grid for regional daily requests and notes parameters retain original source resolution. | Daily UTC or local solar time from 1981-01-01 to near real time; exact limits can depend on parameter/source. | Meteorological and solar parameters; point and regional services, with CSV, JSON, NetCDF and ASCII listed. No API request was made. | NASA ESDIS guidance says NASA-sponsored data are generally open and NASA-led mission data are CC0 unless marked otherwise; non-NASA data are subject to sponsoring-organization terms. NASA acknowledgement and no implied endorsement apply. Exact POWER parameter lineage/terms must be checked. Commercial and ML conditions are not approved for this project. [NASA use guidance](https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance) | Convenient daily point/region candidate, but often coarser and source-dependent. Not a substitute for local gauges or high-resolution terrain/weather observations; exact source and cell resolution must be recorded per parameter. |
| **NASA GPM IMERG — NASA Goddard/PPS and GES DISC**. [IMERG](https://gpm.nasa.gov/data/imerg) and [usage policy](https://gpm.nasa.gov/data/policy) | Near-global precipitation product; product grids commonly 0.1°, exact selected asset/version must be confirmed. | Half-hourly core product, with daily/monthly derivatives; mission-era record spans more than two decades. Early/Late provide lower latency; Final is preferred for retrospective research. Exact V07 asset dates and run must be pinned. | Precipitation estimates; HDF, GeoTIFF and NetCDF options listed. Some access routes require NASA Earthdata/PPS registration. No data request was made. | GPM/TRMM data are described as freely available, with dataset-specific citation/acknowledgement required. NASA ESDIS guidance applies to NASA-led data unless marked otherwise; secondary archives and non-NASA/partner components require source-term review. No project ML approval is recorded. | Useful independent precipitation estimate for comparison, but satellite/retrieval estimates are not local rain-gauge observations. Orographic and intense-rain performance require Kerala-specific validation. |
| **CHIRPS v3 — UCSB Climate Hazards Center**. [CHIRPS v3 documentation](https://www.chc.ucsb.edu/data/chirps3) | Quasi-global land domain 60°N–60°S; 0.05° grid. | 1981 to near-present; preliminary and final products. Daily, pentad, dekad, monthly and annual outputs. The source describes pentad/monthly as fundamental; daily amounts are disaggregated estimates. | Rainfall estimates from satellite thermal infrared and station observations; GeoTIFF, NetCDF, BIL and COG. Daily `rnl` uses ERA5 to partition pentad totals; daily `sat` uses IMERG Late V07. | CHC page states CC BY 4.0 and public-domain dedication to the extent possible; attribution/citation should follow the product documentation. Commercial reuse is covered by the stated CC BY licence subject to its terms and any applicable third-party rights. The licence does not itself constitute project approval or an ML-specific approval. [Product citation/terms](https://www.chc.ucsb.edu/data/chirps3) | Fine-grained rainfall candidate. Daily `rnl` and `sat` are derived/disaggregated products, not independent daily gauge observations; do not treat them as independent of ERA5/IMERG. Complex terrain and extreme-rain bias are documented CHIRPS limitations. |
| **Open-Meteo historical/forecast services — Open-Meteo**. [Terms](https://open-meteo.com/en/terms), [licence](https://open-meteo.com/en/licence) | Model- and endpoint-dependent global/model grids; exact source/model resolution must be recorded for each response. | Historical and forecast periods depend on model/API endpoint; no exact product request or coverage was verified here. | Convenience API aggregating model outputs; access by API. No API request was made. | Free API is limited to non-commercial use; API data are under CC BY 4.0 with attribution. Commercial use requires a paid plan. Upstream data-source terms and exact model lineage remain relevant. No explicit project ML permission is recorded. | Potential prototype source only if the intended project use is non-commercial and the exact model/version, terms, and quality are reviewed. It is an aggregator, not an independent observation network; paid service does not automatically clear upstream data rights or training. |

### CHIRPS version note

The CHC page states that CHIRPS v3 is available and that production of CHIRPS v2 is expected to end after December 2026. A future selection should therefore pin **v3**, its preliminary/final status, and (for daily data) the `rnl` or `sat` product. Do not silently substitute v2 or mix daily products across versions.

## Suitability for the black-pepper pilot

### Historical rainfall and weather context

- **Potential candidates:** IMD 0.25° daily rainfall, CHIRPS v3, IMERG Final, NASA POWER daily data, and a newly specified ERA5/ERA5-Land request.
- **Local reference:** an authorized, quality-controlled IMD station series would be valuable for validation, if Idukki coverage and terms can be established.
- **Not ground truth:** ERA5/ERA5-Land, CHIRPS, IMERG, and POWER gridded outputs are model/reanalysis, retrieval, blended, or processed estimates. Their methods differ; they are not interchangeable with plot measurements.
- **Temporal fitness:** Most candidate products offer far more temporal history than the two existing ERA5-Land requests, but a product catalogue’s coverage does not prove that the needed Kerala/Idukki period is available, authorized, complete, or acquired.
- **Spatial fitness:** Native 0.05°–0.5° grids do not establish farm-level representativeness. Idukki’s complex terrain height/elevation and grid-to-station mismatch need explicit evaluation.

### Forecast use

IMD operational forecasts and advisories are relevant candidate services, but this review did not verify an exact machine-readable Idukki forecast dataset, lead times, archive, licence, API, or redistribution/training terms. ERA5 and ERA5-Land are retrospective reanalyses, not forecasts. Open-Meteo forecast endpoints are third-party aggregated model products with the restrictions in the comparison table.

## Evidence and permission gates before any acquisition

For each exact product/resource, a later authorized review must establish:

1. Product title, version, run/processing baseline, date range, variables, units, grid and source lineage.
2. Official access method and any required account, terms acceptance, or request parameters.
3. Applicable licence and terms version, required attribution, commercial/portfolio scope, redistribution rights, third-party restrictions, and any training-specific conditions.
4. Kerala/Idukki spatial extent, missingness, temporal continuity, quality flags and local validation design.
5. Project-owner authorization for the proposed acquisition and use, separate from publisher terms.
6. Immutable acquisition evidence, retrieval date, request/asset identifiers, file checksums and a quality report, only after acquisition is separately authorized.

No source in this comparison is approved for acquisition, production, pilot research, commercial use, redistribution, or ML training. No Copernicus inquiry status or Stage 23 authorization status is changed.

## Official source references

- ERA5: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- ERA5-Land: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land
- Copernicus licence: https://apps.ecmwf.int/datasets/licences/copernicus/
- IMD gridded rainfall: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html
- IMD portal: https://mausam.imd.gov.in/
- NASA POWER: https://power.larc.nasa.gov/docs/
- NASA POWER Daily API documentation (documentation only; no API call): https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- NASA ESDIS data-use guidance: https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance
- GPM IMERG: https://gpm.nasa.gov/data/imerg
- GPM data usage policy: https://gpm.nasa.gov/data/policy
- CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3
- Open-Meteo terms: https://open-meteo.com/en/terms
- Open-Meteo data licence: https://open-meteo.com/en/licence
