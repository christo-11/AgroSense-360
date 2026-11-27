# AgroSense-360 Stage 23 Permission-Response Log

**Log status:** INITIAL_EMPTY

This log is intentionally empty of permissions or responses. It does not create authorization.

## Log fields

Each row must retain:

- Source owner.
- Official contact channel, only if verified.
- Dataset or information requested.
- Requested geography.
- Requested time coverage.
- Intended research purpose.
- Intended ML training purpose.
- Licence and attribution requirements.
- Redistribution requirements.
- Commercial-use restrictions.
- Inquiry authorization status.
- Inquiry sent date.
- Response received date.
- Response evidence location.
- Permission decision.
- Outstanding conditions.
- Reviewer.
- Review date.
- Next action.

## Initially empty source-owner entries

| Owner | Official contact channel | Dataset/information requested | Geography/time | Research/ML purpose | Licence/attribution | Redistribution/commercial restrictions | Inquiry authorization | Sent | Received | Response evidence | Permission | Outstanding conditions | Reviewer/review date | Next action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kerala Agricultural University | NOT_VERIFIED | Exact black-pepper/Idukki publication, crop evidence, varieties, practices, weather or soil data | Idukki/Kerala; period to be confirmed | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact resource and owner contact | - | Await project-owner authorization |
| ICAR-Indian Institute of Spices Research | NOT_VERIFIED | Exact variety, package-of-practice, Idukki applicability, pest/disease and research publications | Kerala/Idukki; period/publication date to be confirmed | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact resource, contact and reuse terms | - | Await project-owner authorization |
| Kerala Department of Agriculture | NOT_VERIFIED | District crop production/area/yield, varieties, soil or crop surveillance records | Idukki/Kerala; period to be confirmed | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact custodian/resource/terms | - | Await project-owner authorization |
| Kerala Directorate of Economics and Statistics | NOT_VERIFIED | District crop statistics and yield definitions | Idukki/Kerala; period to be confirmed | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact owner/resource/schema/licence | - | Await project-owner authorization |
| India Meteorological Department | NOT_VERIFIED | Historical Idukki or nearby station weather exports | Idukki/Kerala; at least 10 crop-years or approved alternative | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact station release, terms and quality evidence | - | Await project-owner authorization |
| ISRIC/WoSIS and contributing providers | NOT_VERIFIED | SoilGrids release or selected provider-specific soil profiles | Idukki/Kerala; profile collection dates to be confirmed | Research; potential training only if explicitly approved | Contributor/provider-specific; to be confirmed | Redistribution/privacy/provider restrictions | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Provider record, licence, quality and Idukki coverage | - | Await project-owner authorization |
| Government of India/data.gov.in and agricultural statistics owner | NOT_VERIFIED | Exact district/season crop production and yield resource | Idukki/Kerala; 1997 onward or exact confirmed period | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Resource ID, schema, crop label, licence and API terms | - | Await project-owner authorization |
| Kerala Soil Health Card/lab authorities | NOT_VERIFIED | Authorized georeferenced soil laboratory records | Idukki; collection period to be confirmed | Research; potential training only if explicitly approved | To be confirmed | Privacy, record-level reuse and redistribution | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Written owner permission, methods, depth, lab/QC | - | Await project-owner authorization |
| Idukki district administration/agricultural office | NOT_VERIFIED | Official Idukki cultivation and surveillance evidence | Idukki; period to be confirmed | Research; potential training only if explicitly approved | To be confirmed | To be confirmed | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact office/resource/terms | - | Await project-owner authorization |
| ECMWF/Copernicus Climate Data Store | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land | Exact ERA5-Land request/release and current terms | Idukki/Kerala grid; period to be confirmed | Research; training requires separate approval | Copernicus attribution/disclaimer; exact third-party terms | Existing commercial/training decisions unresolved | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact owner decision was not requested through this stage | - | Remains outside acquisition scope |
| NASA GPM/IMERG | https://gpm.nasa.gov/data/policy | Exact V07B asset and data-use metadata | Idukki/nearby grid/gauge coverage; period to be confirmed | Research; training requires separate approval | NASA/GPM citation and asset acknowledgement | Exact asset/third-party restrictions | NOT AUTHORIZED | - | - | - | NOT RECEIVED | Exact asset, terms and independent validation | - | Remains outside acquisition scope |

## Response handling rules

- Store response evidence outside this log as a path or immutable reference.
- Never copy or print credentials or secrets.
- Preserve original response text and received date.
- Separate acknowledgement of receipt from permission.
- A response that is silent or ambiguous remains NOT AUTHORIZED.
- Every source approval change requires the repository's protected governance process.
