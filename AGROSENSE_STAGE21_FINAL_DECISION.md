# AgroSense-360 Stage 21 Final Decision

## Executive decision

**Official-source verification status:** PARTIALLY_VERIFIED  
**Acquisition readiness:** NOT READY  
**ML-training readiness:** NOT READY  
**Idukki status:** PROVISIONAL

Stage 21 verified official organizations and exact licence/policy URLs for several candidate sources. It did not verify the exact Idukki/black-pepper evidence or a district crop production dataset needed for acquisition.

## Sources investigated

- Kerala Agricultural University
- Kerala Department/State Data Portal
- ICAR-IISR and ICAR
- India Meteorological Department
- ISRIC SoilGrids and WoSIS
- ECMWF/Copernicus CDS ERA5-Land
- NASA GPM/IMERG
- Open-Meteo
- Government of India data.gov.in
- FAO/FAOSTAT
- Copernicus Sentinel-2

No source approval record was changed.

## Evidence outcomes

### Verified

- ICAR-IISR is an official relevant institution for spice research and explicitly identifies a black-pepper crop application.
- The Kerala Data Portal is an official Government of Kerala data portal with reproducible-source and acknowledgment rules.
- IMD is an official weather source.
- ERA5-Land, GPM/IMERG and SoilGrids are official and identifiable products with published documentation or policy.
- Copernicus, NASA GPM and Open-Meteo have identifiable licence/policy language for exact resource classes.

### Not verified / not found

- Exact Idukki/black-pepper cultivation evidence
- Idukki-specific production/yield
- Black-pepper variety applicability
- Growing season
- Measured Idukki soil observations
- Idukki rainfall/temperature station series
- Expert-confirmed Idukki black-pepper disease/pest labels

## Licensing findings

- Public access does not imply training or commercial permission.
- Copernicus ERA5-Land has a clear licence permitting lawful use subject to attribution and no-endorsement/disclaimer clauses.
- NASA GPM has a clear data-use policy requiring acknowledgement/citation and exact asset provenance.
- Open-Meteo's free API is non-commercial and CC BY 4.0; paid terms do not replace a project training approval.
- FAO/FAOSTAT permits research use under CC BY 4.0 plus additional terms but does not provide district evidence and is commercially restricted.
- SoilGrids, WoSIS and Sentinel-2 remain source/asset review items.
- data.gov.in, KAU, ICAR/IISR publication exports and IMD exact datasets remain unverified for resource-specific terms.

## Research-use permissions

The following are **not acquisition approvals**:

- ERA5-Land portfolio/research classification
- NASA GPM policy-level availability
- Open-Meteo non-commercial/free API classification
- Kerala Data Portal reproduction terms

Before any data is acquired, exact source, resource ID, version, terms and provenance must be retained.

## ML-training permissions

**No source was promoted to approved for training.**

Reasons:

- No exact Idukki/black-pepper labels.
- No source-backed crop/district/time record.
- No soil ground-truth observations.
- No continuous and independently validated weather series.
- No signed governance approval or immutable acquired snapshot.
- Existing ERA5-Land archives remain rejected for training.

## Blocked or uncertain sources

- **BLOCKED:** FAOSTAT under the existing commercial project classification.
- **REQUIRES_REVIEW:** data.gov.in, KAU, ICAR/IISR publication exports, IMD exact records, WoSIS, SoilGrids, Sentinel-2.
- **NOT_AUTHORIZED:** all sources for ML training.
- **NOT_FOUND:** Idukki black-pepper evidence and exact crop production/disease records.

## Acquisition readiness

Do not acquire or integrate any new dataset in Stage 22 without explicit user/source authorization and an exact evidence gate.

Minimum acquisition prerequisites:

1. Exact authoritative Idukki/black-pepper source or approval to replace Idukki with a different evidence-backed district.
2. Exact publication/dataset name, edition/release, publisher and URL.
3. Exact licence/resource terms and attribution obligations.
4. Approved research, commercial and training use decisions.
5. Exact schema, crop/year/district/units and observations.
6. A provenance and quality manifest.
7. Signed repository governance approval before training.

## Remaining data gaps

- Idukki cultivation and production evidence
- Varieties and growing season
- Soil ground truth
- Weather/gauge observations
- Disease and pest observations
- District boundaries and source checksum/provenance

## Recommended Stage 22

**Stage 22 — Source-owner contact plan and acquisition gate preparation**

Prepare an exact, permission-gated request list for KAU, Kerala Department of Agriculture, ICAR-IISR, IMD, ISRIC/WoSIS, data.gov.in and the relevant district/statistics owner. Do not contact or submit acquisition requests until the project owner explicitly approves the inquiry scope.

Stage 22 deliverables should include an inquiry list, exact evidence/permission fields, source-owner contacts, review dates, and an acquisition decision gate. No credentials, downloads or external data API calls should be performed.
