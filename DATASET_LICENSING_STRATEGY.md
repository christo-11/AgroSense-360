# Dataset Licensing and Provenance Strategy

## Policy

AgroSense-360 has two distinct uses: a public non-commercial portfolio demonstration and a possible future commercial product. Permission for one does not imply permission for the other. Educational, research, open-access, or non-commercial terms are not commercial clearance.

The source of record is [`data/metadata/source_inventory.json`](./data/metadata/source_inventory.json), with source research and limitations in [`DATASET_INVENTORY.md`](./DATASET_INVENTORY.md). Reviews are resource-specific, not website-wide. `portfolio_reviews` controls the internal portfolio/research licence/terms classification. The separate `commercial_reviews.approval_status` and signed training eligibility gate control data entering ML training. A portfolio-only status never approves model training.

## Status definitions

- `APPROVED` — exact commercial-use terms, version, attribution, redistribution rights, access, and third-party rights are verified for the resource; required evidence and an allowlisted reviewer signature are present.
- `CONDITIONAL` — a specific term, access right, or intended-use question remains unresolved; do not acquire, integrate, or redistribute pending review.
- `BLOCKED` — known restrictions conflict with the intended commercial use.
- `REJECTED` — the project has decided not to use the exact resource for the stated purpose.

Portfolio classifications are separate:
- `APPROVED_PORTFOLIO_AND_COMMERCIAL` — internal inventory assessment that publisher terms and obligations appear compatible with both stated categories for the exact resource/version.
- `APPROVED_PORTFOLIO_RESEARCH_ONLY` — internal inventory assessment of apparent publisher licence/terms compatibility for a limited, non-commercial portfolio/research category.
- `UNVERIFIED` — resource-level permission, rights, schema, or ownership has not been established.

**Governance boundary:** These values are internal inventory assessments, not project-owner authorization or source-owner permission. `APPROVED_PORTFOLIO_RESEARCH_ONLY` is not approval to access or acquire data, conduct research, train ML, publicly demonstrate, or deploy. Publisher terms that appear compatible do not themselves authorize project activity. Portfolio/demo and pilot research remain separate project permission scopes; Stage 40 currently marks both **NOT AUTHORIZED**.

New commercial reviews use only `APPROVED`, `CONDITIONAL`, `BLOCKED`, or `REJECTED`; unresolved research is recorded as `CONDITIONAL`, not as an implied approval. Only the separate commercial approval gate's signed `APPROVED` status can allow a source to proceed toward training. Quality, geography/crop relevance, acquisition, and provenance checks are still required.

## Current resource classification

The inventory is checked as of 2026-11-19. No dataset has been downloaded. Each `dataset_version` is `null` with `version_status: NOT_ACQUIRED`; this is intentionally not replaced with a guessed “latest” version.

| Exact resource and publisher | Internal portfolio licence/terms classification | Commercial/training status | Current limitation |
|---|---|---|---|
| [District-wise, season-wise crop production](https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997) — Government of India | UNVERIFIED | CONDITIONAL | Exact resource licence, access schema, Kerala rows, units, and version unresolved; resource page returned 403. |
| [FAOSTAT QCL](https://www.fao.org/faostat/en/#data/QCL) — FAO | BLOCKED | BLOCKED | CC BY 4.0 is supplemented by FAO database terms prohibiting commercial promotion use; archive not acquired. |
| [KAU crop, variety and observatory information](https://kau.in/) — Kerala Agricultural University | UNVERIFIED | CONDITIONAL | No exact structured dataset, version, or resource-specific reuse terms identified. |
| [Current daily mandi prices](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi) — Government of India / AGMARKNET | UNVERIFIED | CONDITIONAL | Exact resource licence, API schema, Kerala coverage, units, and format unresolved; API requires a key. |
| [SoilGrids 2.0](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html) — ISRIC | CONDITIONAL | CONDITIONAL | Applicable product licence not text-verified; modeled 250 m values are not lab labels. |
| [WoSIS profiles](https://docs.isric.org/globaldata/wosis/faq-wosis.html) — ISRIC and providers | UNVERIFIED | CONDITIONAL | Rights are contributor-specific; no selected record or license reviewed. |
| [India Soil Health Card](https://soilhealth.dac.gov.in/) — Government of India | UNVERIFIED | CONDITIONAL | No permitted georeferenced bulk export or record-level permission verified. |
| [Sentinel-2 L2A](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html) — Copernicus / EU | CONDITIONAL | CONDITIONAL | Data Space says Sentinel data are free/full/open, but exact linked notice and selected asset were not reviewed; download account required. |
| [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) — ECMWF / Copernicus CDS | APPROVED_PORTFOLIO_RESEARCH_ONLY | CONDITIONAL | Cited publisher terms may appear compatible with limited non-commercial portfolio display, subject to Copernicus Licence v1.2, C3S attribution/disclaimer, the exact CDS request, and third-party asset terms. This is not project authorization. |
| [NASA GPM IMERG V07B](https://gpm.nasa.gov/data/imerg) — NASA | APPROVED_PORTFOLIO_RESEARCH_ONLY | CONDITIONAL | Cited GPM/NASA terms may appear compatible with limited non-commercial portfolio display, subject to GPM citation/acknowledgement and exact asset metadata. This is not project authorization; future commercial use remains separate and no download exists. |
| [Open-Meteo Historical API](https://open-meteo.com/en/terms) — Open-Meteo | APPROVED_PORTFOLIO_RESEARCH_ONLY | BLOCKED | The free API terms are non-commercial and require attribution; no query was made. This inventory classification does not authorize a query or project activity. Commercial use would require a paid plan, excluded here. |
| [PlantVillage](https://huggingface.co/datasets/mohanty/PlantVillage) — authors / Hugging Face mirror | UNVERIFIED | CONDITIONAL | Mirror card declares CC BY-SA 3.0; upstream image rights and license scope unresolved. |
| [PlantDoc classification dataset](https://github.com/pratikkayal/PlantDoc-Dataset) — authors | UNVERIFIED | CONDITIONAL | Repository declares CC BY 4.0, but underlying web-scraped image rights are not established. |

No source is approved for commercial reuse or training, and no dataset is acquired. No candidate was rejected; unresolved terms remain conditional or blocked rather than being treated as permission.

## Stage 12D weather licence/terms compatibility assessments

### ERA5-Land hourly data from 1950 to present

The inventory's `APPROVED_PORTFOLIO_RESEARCH_ONLY` value is an internal assessment that cited publisher terms may appear compatible with a limited, non-commercial portfolio/research category, subject to the exact resource and terms. It is not project-owner authorization, source-owner permission, or approval to access, acquire, research, publicly demonstrate, or deploy. Portfolio/demo and pilot research are separate scopes, and Stage 40 currently marks both **NOT AUTHORIZED**. The applicable official licence is [Licence to Use Copernicus Products v1.2](https://apps.ecmwf.int/datasets/licences/copernicus/), November 2019, supplemented by [CDS Terms of Use](https://cds.climate.copernicus.eu/disclaimer-privacy).

The licence permits reproduction, distribution, communication to the public, adaptation, modification and combination for lawful purposes worldwide, free of charge and royalty-free. Public use requires clear C3S attribution. Adapted distributions require the Copernicus modified-information notice and the required disclaimer that neither the European Commission nor ECMWF is responsible for use. Clause 7 excludes labelled third-party products or data that may have separate terms. ERA5-Land is reanalysis/model output rather than station observations. This inventory classification does not authorize acquisition; any acquisition requires a separate valid project-owner decision and applicable access/terms.

Future commercial-use review remains separate and is still **CONDITIONAL** in the commercial review. This portfolio classification does not satisfy project-owner authorization or the training gate.

### NASA GPM IMERG Final Run V07B

The inventory's `APPROVED_PORTFOLIO_RESEARCH_ONLY` value is an internal assessment that the cited publisher terms may appear compatible with a limited, non-commercial portfolio/research category, subject to exact asset terms. It is not project-owner authorization, source-owner permission, or approval to access, acquire, research, train ML, publicly demonstrate, or deploy. Portfolio/demo and pilot research are separate scopes; Stage 40 currently marks both **NOT AUTHORIZED**. The cited evidence is the [GPM & TRMM Data Usage Policy](https://gpm.nasa.gov/data/policy), [IMERG V07 Release Notes](https://gpm.nasa.gov/resources/documents/imerg-v07-release-notes), [IMERG V07 Technical Documentation](https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation) and [NASA ESDIS Data-Use Guidance](https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance).

The GPM policy says GPM/TRMM data are freely available and requires the dataset source to be acknowledged with authors/producers, title, version, archive/distributor and access date. The GPM policy must not be labelled as CC0. Individual asset metadata must be checked before redistribution because restricted or non-NASA source components may carry separate terms. The inventory classification records only apparent licence/terms compatibility for V07B Final Run; it does not authorize portfolio/public-demo display or any other project activity.

Future commercial-use review remains separate and is still **CONDITIONAL** in the commercial review; no model, provenance manifest or acquired file exists yet. The inventory classification does not satisfy project-owner authorization or the training gate.

## Stage 12 audit outcome

The 2026-11-19 Stage 12 re-review audited all 12 inventoried sources. It found no source that was both resource-license-clear for the project's future-commercial scope and acquired as an original, checksummed file. Consequently:

- no `APPROVED` commercial record was created;
- no dataset was downloaded or copied from an external source;
- no raw or intermediate dataset is in the repository;
- no SHA-256 dataset checksum exists;
- no dataset quality or relevance verdict was marked `VERIFIED`;
- no model or preprocessing work was performed.

The approved-then-acquire sequence remains mandatory. A conditional or blocked classification must not be changed by download success or public availability.

## Required record for each acquisition or use

Before any source is used, retain:

1. Publisher, original resource URL, download/API URL, and source-specific version/release/date.
2. Exact license/terms and dated permission evidence (official URLs, snapshots or written permission where applicable).
3. Portfolio scope and commercial-use permission as separate decisions.
4. Attribution, share-alike, redistribution, derivative-work, and third-party obligations.
5. Geographic coverage, crop/label relevance, time range, units, schema, missingness, quality checks, and known bias/leakage.
6. Retrieval timestamp, request parameters, source version, local data path, SHA-256 digest, and any preprocessing lineage.
7. Reviewer identity, review date, rationale, unresolved concerns, and approval signature where required.

For data not acquired, keep version and digest empty/null and state that provenance is not yet available. Do not fabricate an acquisition date, checksum, record count, label, or license.

## Operational gate and ownership

`backend/scripts/dataset_governance.py` rejects training unless the resource is signed `APPROVED`, acquired, quality/relevance-verified, and accompanied by a matching provenance manifest. `DATASET_REVIEWER_EMAILS` and `DATASET_APPROVAL_HMAC_KEY` are private backend/admin settings; do not commit them or paste them into chat. An approval review must be updated through a documented, protected repository process.

Raw and interim data directories are git-ignored. Keep data only in authorized storage with least-privilege access and retention rules. Avoid copying personal or farm-identifying data into public portfolio artifacts. Model cards and reports must preserve source/version lineage and attribution.

## Re-review triggers

Re-review when the project changes from portfolio to promotion/sales, adds a paid service, redistributes source data, publishes a derived dataset/model, changes a provider/product/version, expands geography/crops, or receives updated license/permission terms. If permission is ambiguous, keep the source blocked or unverified and contact the provider or qualified counsel.
