# Dataset Licensing and Provenance Strategy

## Policy

AgroSense-360 has two distinct uses: a public non-commercial portfolio demonstration and a possible future commercial product. Permission for one does not imply permission for the other. Educational, research, open-access, or non-commercial terms are not commercial clearance.

The source of record is [`data/metadata/source_inventory.json`](./data/metadata/source_inventory.json), with source research and limitations in [`DATASET_INVENTORY.md`](./DATASET_INVENTORY.md). Reviews are resource-specific, not website-wide. `portfolio_reviews` controls the portfolio/research classification. The separate `commercial_reviews.approval_status` and signed training eligibility gate control data entering ML training. A portfolio-only status never approves model training.

## Status definitions

- `APPROVED_PORTFOLIO_AND_COMMERCIAL` — permission and obligations reviewed for both uses, for the exact resource/version.
- `APPROVED_PORTFOLIO_RESEARCH_ONLY` — use is restricted to the documented non-commercial portfolio/research scope and its attribution/usage terms.
- `CONDITIONAL` — a specific term, access right, or intended-use question remains unresolved; do not integrate or redistribute pending review.
- `BLOCKED` — known restrictions conflict with the intended use.
- `UNVERIFIED` — resource-level permission, rights, schema, or ownership has not been established.

Only the separate commercial approval gate's signed `APPROVED` status can allow a source to proceed toward training. Quality, geography/crop relevance, acquisition, and provenance checks are still required.

## Current resource classification

The inventory is checked as of 2026-11-19. No dataset has been downloaded. Each `dataset_version` is `null` with `version_status: NOT_ACQUIRED`; this is intentionally not replaced with a guessed “latest” version.

| Resource and official source | Portfolio status | Commercial/training status | Current limitation |
|---|---|---|---|
| [data.gov.in district crop production](https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997) | UNVERIFIED | UNVERIFIED | Catalog/API returned access errors in prior checks; Kerala rows, schema, units, and resource terms unresolved. |
| [FAOSTAT QCL](https://www.fao.org/faostat/en/#data/QCL) | BLOCKED | BLOCKED | Additional terms restrict use in connection with commercial enterprise/product/service promotion; archive was not acquired. |
| [Kerala Agricultural University](https://kau.in/) | UNVERIFIED | UNVERIFIED | No resource-specific, versioned dataset or reuse terms verified. |
| [AGMARKNET/data.gov.in](https://agmarknet.gov.in/) | UNVERIFIED | UNVERIFIED | API schema, Kerala coverage, prices/arrivals units, and reuse terms unresolved. |
| [SoilGrids 2.0](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html) | CONDITIONAL | CONDITIONAL | Product attribution and contributor-data separation need review; gridded estimates are not lab labels. |
| [WoSIS](https://docs.isric.org/globaldata/wosis/) | UNVERIFIED | UNVERIFIED | Contributor-specific rights; selected records not reviewed. |
| [Soil Health Card](https://soilhealth.dac.gov.in/) | UNVERIFIED | UNVERIFIED | No permitted georeferenced export or individual record permission verified. |
| [Sentinel-2 L2A](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html) | CONDITIONAL | CONDITIONAL | Verify selected product/asset legal terms and attribution; no imagery acquired. |
| [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) | CONDITIONAL | CONDITIONAL | Accept and retain terms for the actual request; no data acquired. |
| [NASA GPM IMERG](https://gpm.nasa.gov/data/imerg) | CONDITIONAL | CONDITIONAL | Confirm product/version and third-party terms before use; no data acquired. |
| [Open-Meteo Historical API](https://open-meteo.com/en/terms) | APPROVED_PORTFOLIO_RESEARCH_ONLY | BLOCKED | Free API is non-commercial and requires CC-BY attribution. It is not connected/queried; this does not allow commercial product or training use. |
| [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) | UNVERIFIED | UNVERIFIED | Mirror license does not establish upstream image-level rights; no images acquired. |
| [PlantDoc](https://github.com/pratikkayal/PlantDoc-Dataset) | UNVERIFIED | UNVERIFIED | Repository license does not resolve web-scraped image-level rights; no images acquired. |

No source is approved for both portfolio and commercial reuse, and no training dataset is approved or acquired.

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
