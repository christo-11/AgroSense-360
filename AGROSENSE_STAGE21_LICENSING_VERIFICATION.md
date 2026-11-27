# AgroSense-360 Stage 21 Licensing Verification

**Assessment date:** 2026-11-23  
**Scope:** Read-only licence evidence review; existing approval records are unchanged

## Summary

Public accessibility does not establish portfolio, commercial or training permission. The Stage 21 findings confirm some official licensing facts but do not change any source status in `data/metadata/source_inventory.json`.

## Licensing matrix

| Source | Official URL/licence evidence | Licence/version | Attribution | Research/portfolio | Commercial | ML training | Redistribution | Stage 21 class |
|---|---|---|---|---|---|---|---|---|
| ERA5-Land/Copernicus | Dataset: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land; licence: https://apps.ecmwf.int/datasets/licences/copernicus/; terms: https://cds.climate.copernicus.eu/disclaimer-privacy | Licence to Use Copernicus Products; current page is the applicable licence record | Clear Copernicus C3S/CAMS attribution; modified data notice and no-endorsement/disclaimer requirements | Likely permitted for lawful, non-commercial research/portfolio use under the licence and accepted CDS terms | No existing signed commercial approval; status remains conditional | `NOT_AUTHORIZED` for existing sparse archives | Distribution permitted under licence subject to attribution and separate third-party terms | `VERIFIED_LICENSE` / `NOT_AUTHORIZED` training |
| NASA GPM IMERG V07B | https://gpm.nasa.gov/data/policy | GPM/TRMM data usage policy; exact asset/third-party terms remain asset-specific | Cite dataset authors/producers, title, version, archive/distributor and access date; acknowledge NASA/Goddard/PPS | Portfolio/research reuse may be possible if exact asset metadata and acknowledgement are retained | Existing project approval remains conditional | `NOT_AUTHORIZED` until exact data, quality, relevance and governance gate are satisfied | Exact secondary-archive provenance and third-party restrictions must be checked | `VERIFIED_LICENSE` at policy level / `REQUIRES_REVIEW` asset level |
| Open-Meteo | https://open-meteo.com/en/terms and https://open-meteo.com/en/licence | CC BY 4.0 for API data plus free/public API terms | Appropriate Open-Meteo/source attribution and link to licence | Free API is limited to non-commercial use; public research is a permitted example | Paid subscription may be required; no paid plan or commercial approval here | `NOT_AUTHORIZED`; no exact model, request/response and quality approval | CC BY redistribution/adaptation is permitted for licensed API data subject to attribution; source-derived third-party terms must be retained | `VERIFIED_LICENSE` / `NOT_AUTHORIZED` commercial/training |
| FAOSTAT | https://www.fao.org/faostat/en/#data/QCL and https://www.fao.org/contact-us/terms/db-terms-of-use/en | CC BY 4.0 plus FAO Statistical Database terms | Required FAO citation format and access date | Research/statistical use is generally permitted under the database terms | Datasets shall not promote a commercial enterprise or imply FAO endorsement; existing project status remains blocked | Existing project has no training clearance; geography also irrelevant to Idukki | Third-party exceptions and redistribution restrictions must be checked | `VERIFIED_LICENSE` / `BLOCKED` project use |
| SoilGrids 2.0 | https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html; https://isric.org/about/data-policy | Official product identified; ISRIC policy/outputs require exact resource review; no exact version/licence snapshot verified | SoilGrids citation and ISRIC/contributor acknowledgement are required by the documentation/policy | Candidate for research only, not lab ground truth | Existing project review remains conditional | `NOT_AUTHORIZED` as ground-truth labels | Reproduction/reuse policy and contributor/provider obligations remain to be confirmed | `PARTIALLY_VERIFIED` / `REQUIRES_REVIEW` |
| WoSIS | https://docs.isric.org/globaldata/wosis/faq-wosis.html | Quality-assessed standardized profile data shared under contributing-provider conditions; no single licence | Original providers, ISRIC/WoSIS and selected snapshot/profiles must be cited as required | `REQUIRES_REVIEW` for every selected record | `REQUIRES_REVIEW` per provider | `NOT_AUTHORIZED` until record-level permissions and quality are verified | Provider-specific restrictions may prohibit redistribution | `REQUIRES_REVIEW` |
| Sentinel-2 L2A | https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html | Copernicus Sentinel legal framework/terms apply; exact selected asset notice not inspected | Copernicus/Sentinel attribution as required by the applicable legal notice | Public research reuse may be possible but selected baseline/asset terms remain to be verified | Existing project review remains conditional | `NOT_AUTHORIZED` until exact asset, labels and governance approval | Redistribution and derived-product terms depend on exact notice and third-party components | `REQUIRES_REVIEW` |
| Kerala Data Portal | https://datahub.kerala.gov.in/ | Government of Kerala portal terms; exact dataset terms may differ for third-party content | Government of Kerala/C-DIT/portal source must be prominently acknowledged | Official FAQs allow free research/publication reuse of portal material, with accuracy and non-misleading use | No explicit commercial approval was verified for all hosted data | `NOT_AUTHORIZED` as no verified crop-specific labels/dataset were found | Reproduction free of charge; third-party content excluded; source-dependent terms apply | `VERIFIED_LICENSE` for portal terms / `NOT_FOUND` for crop data |
| data.gov.in | https://www.data.gov.in/ | 403 during Stage 21 review; exact resource licence not verified | Not verified | Not verified | Not verified | `NOT_AUTHORIZED` | No redistribution until exact resource terms are inspected | `REQUIRES_REVIEW` |
| KAU | https://kau.in/ | No exact publication/export or resource licence identified | Not verified per selected resource | `REQUIRES_REVIEW` | `REQUIRES_REVIEW` | `NOT_AUTHORIZED` | No blanket website permission inferred | `REQUIRES_REVIEW` |
| ICAR-IISR | https://spices.res.in/ | Institutional official source; exact publication/app terms and page/licence not separately identified | Use publisher name and title as required for each specific publication/app | Suitable as evidence source only, pending exact document | `REQUIRES_REVIEW` for redistribution/reuse | `NOT_AUTHORIZED` absent exact dataset and terms | No data export licence verified | `REQUIRES_REVIEW` |
| IMD | https://mausam.imd.gov.in/ | Public portal terms/licence for exact station/dataset not selected or verified | Exact citation and attribution required when selected | `REQUIRES_REVIEW` | `REQUIRES_REVIEW` | `NOT_AUTHORIZED` | Redistribution and API access terms require verification | `REQUIRES_REVIEW` |

## Licence interpretation

- ERA5-Land: the Copernicus licence permits lawful reproduction, distribution, communication, adaptation and combination, with attribution and no-endorsement requirements. It does not turn unverified sparse archives into quality-approved training data.
- GPM: data are freely available under the policy, but freely available is not the same as an exact acquisition manifest or ML-training approval.
- Open-Meteo: the free API is explicitly non-commercial and CC BY 4.0. A portfolio/research use must remain within non-commercial terms and retain attribution.
- FAO: general database terms permit research/statistical use but prohibit commercial promotion and FAO endorsement. It remains unsuitable for Idukki district evidence.
- Kerala Portal: portal content may be reproduced free of charge with source acknowledgement; third-party content and exact source department terms are excluded.
- The ICAR-IISR, KAU, IMD and data.gov.in records require exact resource/document verification before any dataset is requested.

## Training permission findings

No source in this stage was promoted to `APPROVED_FOR_TRAINING`.

The existing project record remains fail-closed: a source may be public or reusable for research, but training additionally requires:

1. Signed/commercial or research training approval under the repository governance process.
2. Exact acquired dataset version and provenance.
3. Immutable file checksum.
4. Data quality and training relevance verification.
5. Verified geographic/crop/label suitability.
6. Leakage-safe features and labels.

Existing ERA5-Land archives remain ineligible.
