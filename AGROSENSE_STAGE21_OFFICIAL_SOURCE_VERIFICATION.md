# AgroSense-360 Stage 21 Official Source Verification

**Assessment date:** 2026-11-23  
**Scope:** Black pepper in Kerala, with Idukki as a provisional candidate district  
**Status:** Official-source verification and documentation; no acquisition or approval change

## Executive result

Stage 21 found official institutional and data-source evidence, but no exact, crop-specific Idukki agricultural dataset or black-pepper district production record suitable for acquisition.

- Kerala/black-pepper state-level cultivation: **PARTIALLY_VERIFIED** through official ICAR-IISR source identification, but no Idukki district claim was found.
- Idukki/black-pepper cultivation: **NOT_FOUND** in the official pages and Kerala data portal searches available for this stage.
- Varieties and growing season: **NOT_FOUND** as exact official crop/district evidence.
- Soil: **PARTIALLY_VERIFIED** only as a global modeled soil product; no authorized Kerala/Idukki lab data was found.
- Rainfall/weather: **VERIFIED_OFFICIAL** for source availability and general data definitions, but not verified for a Kerala/Idukki crop series.
- Production/yield: **NOT_FOUND** or **REQUIRES_REVIEW** for an exact district/crop/resource record.
- Disease/pests: **NOT_FOUND** for crop/district-specific authoritative evidence.

## Official source review

| Organization/source | Official URL | Evidence found | Verification status | Limitations |
|---|---|---|---|---|
| Kerala Agricultural University | https://kau.in/ | Public homepage identifies weather data area; no historical weather data or exact black-pepper/Idukki evidence was available in the reviewed page | `PARTIALLY_VERIFIED` | No exact publication, release, crop/district dataset, licence or structured export identified |
| Kerala data portal | https://datahub.kerala.gov.in/ | Official portal states it provides state data and reproduction rules; searches for "black pepper" returned no charts | `NOT_FOUND` for crop evidence | `Idukki` search returned general/district content, but no black-pepper record |
| ICAR-IISR | https://spices.res.in/ | Official institute page identifies ICAR-IISR black-pepper, turmeric, ginger and cardamom mobile apps and describes package-practice, variety and pest-management information | `VERIFIED_CROP_SPECIFIC` | Home page does not establish Idukki cultivation or provide exact data, dates, varieties or district observations |
| ICAR | https://icar.org.in/ and https://icar.org.in/en/about-us | Official organizational source; institute content identifies IISR as a crop-research institution | `PARTIALLY_VERIFIED` | ICAR page/institute pages were in maintenance or returned limited content during review |
| India Meteorological Department | https://mausam.imd.gov.in/ | Public official weather portal and station/district observation interfaces | `VERIFIED_OFFICIAL` | No exact Idukki station export or black-pepper phenology/target series verified |
| SoilGrids/ISRIC | https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html | Official documentation identifies SoilGrids250m v2.0, global 250 m modeled maps and six depth intervals | `VERIFIED_OFFICIAL` | Remote global model estimates, not Idukki lab measurements |
| WoSIS/ISRIC | https://docs.isric.org/globaldata/wosis/faq-wosis.html | Official documentation defines quality-assessed/standardized soil profiles and contributor-specific sharing conditions | `PARTIALLY_VERIFIED` | No selected Kerala/Idukki profile or per-provider licence was identified |
| Copernicus CDS ERA5-Land | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land | Official page identifies global 0.1 degree hourly land reanalysis from January 1950 to present | `VERIFIED_OFFICIAL` | Reanalysis, not observations; existing archives remain unsuitable for training |
| NASA GPM/IMERG | https://gpm.nasa.gov/data/policy | Official GPM/TRMM data policy and citation instructions | `VERIFIED_LICENSE` | Exact V07B asset, Kerala coverage and gauge validation are not acquired or verified |
| data.gov.in | https://www.data.gov.in/ | Port 403 during this review; inventory retained an exact district-crop candidate but no resource evidence | `REQUIRES_REVIEW` | Resource schema, licence, Kerala/Idukki rows and version are unresolved |
| Kerala data portal | https://datahub.kerala.gov.in/search?q=black%20pepper | Exact search returned 0 results | `NOT_FOUND` | Search is not a complete audit of all state publications |

## Evidence matrix

| Evidence | Source | Verification | Evidence type |
|---|---|---|---|
| Black pepper cultivation in Kerala | ICAR-IISR official institute page and app listing | `VERIFIED_CROP_SPECIFIC` for an official crop institute; Kerala cultivation prevalence not quantified | Published institutional research/guidance |
| Idukki cultivation | Kerala Data Portal search and repository evidence; no exact official Idukki crop record found | `NOT_FOUND` | No supporting record |
| Varieties | ICAR-IISR official page says spice varieties are available as general institutional information | `PARTIALLY_VERIFIED` | Institutional package/variety information; no exact approved Idukki variety list found |
| Growing season | No exact official Idukki or Kerala black-pepper season record verified | `NOT_FOUND` | Unsupported without document |
| Soil properties | SoilGrids official documentation; repository SoilGrids/WoSIS inventory | `PARTIALLY_VERIFIED` | Remote/global modeled or profile-survey evidence, not Idukki ground truth |
| Rainfall/weather | IMD public portal and ERA5-Land official product page | `VERIFIED_OFFICIAL` for source identity; `NOT_AUTHORIZED` for pilot use from existing archives | Published weather/reanalysis or station portal evidence |
| Production/yield | data.gov.in candidate and Kerala Data Portal search | `NOT_FOUND` / `REQUIRES_REVIEW` | Administrative data candidate only |
| Disease/pest information | ICAR-IISR page mentions pest-management information, but no exact black-pepper pest/disease page or Idukki field record was verified | `PARTIALLY_VERIFIED` | Institutional research guidance; no measured prevalence/labels |

## Exact verification findings

### Crop and location

- ICAR-IISR is an official ICAR institution focused on spices and explicitly identifies a "ICAR-IISR Black Pepper" application. This provides a verified crop-specific institutional source for further document selection.
- It does not establish that Piper nigrum is grown in Idukki, nor does it provide an Idukki cultivation area or yield statistic.
- The Kerala Data Portal search for "black pepper" returned zero charts. This is a negative result only; it does not prove that no other state publication exists.
- Idukki remains provisional.

### KAU

- The KAU homepage was accessible, but it reported that weather data for the day was unavailable in the repository and supplied no exact historical black-pepper publication or export.
- No exact KAU document with title, publication date, district, crop, licence and reuse terms was located during this read-only review.

### IMD

- The IMD public portal was verified as an official weather source. It exposes district warnings and realized temperature/rainfall interfaces.
- No exact Idukki historical station series, data release, citation/terms, spatial period or licence was selected or downloaded.

### Soil

- SoilGrids is an official ISRIC product: 250 m model maps at six depth intervals. It remains an estimate.
- WoSIS provides measured soil profiles and standardization but requires compliance with each contributing provider's conditions. No Idukki profile was selected.

### Production

- The data.gov.in district-crop resource remains the strongest candidate in the repository, but the resource page and API were inaccessible and no exact resource ID/schema/licence was verified.
- Kerala Data Portal did not return a black-pepper chart in the search performed.

## Remaining evidence gaps

1. Exact Idukki/black-pepper official publication or statistics.
2. Exact black-pepper varieties, release dates and Kerala/Idukki applicability.
3. Official growing-season and phenology source.
4. Measured Idukki soil profiles with depth, methods, units and permission.
5. Idukki station/gauge rainfall and temperature series with exact release and terms.
6. Expert-confirmed black-pepper disease/pest occurrence and severity labels.
7. Exact district crop production/yield resource with schema and licence.
