# AgroSense-360 Black Pepper Pilot Plan

## Status and scope

**Stage 19 is design and readiness only.** The selected research question is:

> How can weather and available soil information be organized to understand the growing conditions of black pepper in Kerala?

The proposed crop is black pepper (`Piper nigrum` as supplied in the Stage 19 request), and Idukki is the candidate district. This plan does not assert cultivation, prevalence, or suitability in Idukki. It does not acquire data, change database records, or train a model.

The repository's catalogue migration includes a `Black pepper` crop label and an `Idukki` district label, but does not seed a scientific name or a district/crop relationship. The README names Idukki with cardamom as the initial pilot focus; that is a project-planning note, not evidence that black pepper is grown or suitable there. **Idukki is provisional for this black-pepper pilot.** No alternative district is recommended because the inspected repository contains no stronger district-level evidence.

## Evidence reviewed

- Current Git branch is `main`; the worktree already contains unrelated Stage 14–18 modifications and untracked reports. Those changes were preserved.
- The agricultural catalogue migration seeds 14 Kerala districts, four categories, 31 crop names, and empty `pending` crop profiles. It seeds no varieties, agricultural-source rows, or district/crop suitability records.
- `Crop.scientific_name` is nullable; the black-pepper seed row does not set it. `CropProfile` contains optional crop-wide fields, not observed site measurements. `DistrictCropSuitability` is a separate, source-linked but currently unpopulated relationship.
- The source inventory records 13 candidates. For the pilot-relevant sources, versions, licensing, permissions, and geographic limits are summarized in [AGROSENSE_BLACK_PEPPER_SOURCE_ASSESSMENT.md](./AGROSENSE_BLACK_PEPPER_SOURCE_ASSESSMENT.md).
- The two existing ERA5-Land files were found in `data/raw/` at their manifest-recorded sizes. The quality report still rejects both for training; it does not calculate valid coverage against Idukki or a Kerala district polygon.
- Existing readiness and weather reports were checked against the migration and current JSON metadata. Live database contents were not queried in this stage.

## District decision

| Question | Finding | Decision |
| --- | --- | --- |
| Is Idukki a catalogue district? | Yes; it is one of the migration-seeded Kerala districts. | Catalogue identity verified |
| Does the README mention Idukki as an initial focus? | Yes, for Idukki and cardamom. | Planning context only |
| Is black pepper linked to Idukki in the seeded catalogue? | No; no district/crop relationship is seeded. | Missing |
| Is a source-backed Idukki black-pepper cultivation or suitability record present? | None found in the inspected repository evidence. | Not established |
| Should another district be selected? | No comparative district data or sourced association was found. | Do not substitute or rank districts |

Keep the pilot district as `PROVISIONAL` until a source specifically supports black-pepper relevance to Idukki. A suitable supporting record would identify the publisher, crop and variety if applicable, district/geography, observation or publication date, method, and the source's terms. State-level presence alone is insufficient to validate a district-level claim.

## Proposed dataset structure

Use the normalized logical design in [AGROSENSE_BLACK_PEPPER_DATA_DICTIONARY.md](./AGROSENSE_BLACK_PEPPER_DATA_DICTIONARY.md). Keep separately identifiable:

1. **Measured observations:** station weather or laboratory soil measurements with collection method and traceable sample/station metadata.
2. **Estimated values:** reanalysis weather or modeled soil products, preserving model/product version and uncertainty. These are not measurements.
3. **Derived features:** explicit transformations of identified source observations, with formula, units, code/version, and input record IDs.
4. **Unverified information:** candidate crop guidance, unreviewed publications, or incomplete provenance. Keep it out of verified profile claims and training.

Weather variables may describe atmospheric conditions; they are not substitutes for soil pH, nitrogen, phosphorus, potassium, texture, or measured fertility. Do not infer these soil values from weather.

## Candidate readiness by feature

| Feature | Status | Evidence and constraint |
| --- | --- | --- |
| Black-pepper catalogue label | `VERIFIED` | The migration seeds the common name. This verifies a catalogue entry only. |
| Scientific name `Piper nigrum` | `REQUIRES_VALIDATION` | Supplied by the user; the catalogue seed leaves `scientific_name` empty and no taxonomic citation was found in the repository. |
| Kerala state/district catalogue | `VERIFIED` | Migration seeds Kerala district names, including Idukki; it does not provide district boundary geometries. |
| Idukki as a black-pepper pilot site | `PROVISIONAL` | README's prior Idukki/cardamom note is not black-pepper evidence. No sourced district/crop record exists. |
| Black-pepper growing season, variety, practices, or soil/climate requirements | `MISSING` | No verified profile claims or variety rows are seeded. |
| ERA5-Land file acquisition/integrity | `VERIFIED` at file level | Existing manifest and quality report record two files; both were found at recorded sizes, and the quality report records ZIP CRC `PASS`. This says nothing about suitability. |
| ERA5-Land weather series for the pilot | `PROVISIONAL` / insufficient | Only 2 dynamic times in one archive and 12 irregular times in the other; global missingness is 65.87%; no Idukki polygon/cell quality assessment or independent station comparison. |
| District-level weather coverage | `REQUIRES_VALIDATION` | The global grid intersects Kerala at 0.1-degree spacing, but the quality report says no Kerala polygon/cell values were checked. |
| Black-pepper soil observations | `MISSING` | No local, georeferenced black-pepper soil lab measurements are present. SoilGrids is metadata-only in the inventory; WoSIS and Soil Health Card records are not acquired/authorized. |
| Commercial use of pilot sources | `NOT_AUTHORIZED` | No source is commercially approved; several candidate rights remain conditional or unknown. |
| Model training | `NOT_AUTHORIZED` | Current ERA5 archives are explicitly rejected for training, and no black-pepper soil/target labels or training-approved sources are available. |

## Proposed staged workflow

### Gate A — evidence and scope

- Keep Idukki provisional; obtain a source-backed black-pepper district record before labeling the pilot as locally representative.
- Confirm crop taxonomy from an attributable authority before writing a scientific name into the catalogue.
- Choose the specific black-pepper question, observation period, target unit, spatial support, and intended use before selecting variables.
- Approve source-specific license and attribution terms; portfolio permission, source acquisition, data quality, and training permission remain separate decisions.

### Gate B — authorized pilot data specification

If approved by the project owner and the relevant data publishers:

- Request a versioned historical station/gauge export for the pilot area, with station IDs, coordinates/accuracy, dates, units, quality flags, operating history, and reuse permission. The current KAU inventory item only identifies general extension/observatory information; it does not identify a verified historical export.
- Request authorized georeferenced soil laboratory records from participating labs or the relevant government/academic data owner. Require sample IDs, coordinates/accuracy, collection date, depth, analyte, analytical/extraction method, units, lab/QC, crop/variety context where recorded, and written reuse permission.
- If an explicitly licensed reanalysis product is later selected, pin its release/request parameters and retain raw units, time semantics, native grid, masks, and source provenance. The two current ERA5-Land archives are not an acceptable substitute.
- Do not infer soil ground truth from SoilGrids, weather, or district-level crop summaries.

### Gate C — validation before analysis

- Validate source IDs, dataset versions, license/attribution, crop and district references, canonical units, UTC timestamps, duplicate natural keys, missingness flags, spatial coverage, measurement depth/method, and measured/estimated/derived labels.
- Keep raw inputs immutable and report quality per variable, district/site, season, and source version.
- Apply the thresholds in [AGROSENSE_WEATHER_QUALITY_SPECIFICATION.md](./AGROSENSE_WEATHER_QUALITY_SPECIFICATION.md) only after scientific review and pilot-specific approval.
- Do not train, infer, or publish recommendations in this stage.

## Repository changes and validation

Added a standalone Pydantic contract validator at `backend/scripts/black_pepper_pilot_contract.py` and focused tests at `backend/tests/test_black_pepper_pilot_contract.py`. The contract has no API, database, file, network, or model integration. Test records are in-memory placeholders with missing values; they are not agricultural observations.

No database schema or migration, production catalogue record, source approval, acquisition record, or archive was modified.

## Approval required before acquisition

No source has been contacted. Before requesting or acquiring additional data, approve the intended source and use. The precise dataset/source candidates, currently known license status, missing permission evidence, and requested evidence fields are listed in [AGROSENSE_BLACK_PEPPER_SOURCE_ASSESSMENT.md](./AGROSENSE_BLACK_PEPPER_SOURCE_ASSESSMENT.md). Where a resource/version or license is not yet identified, the next step is a permission/evidence inquiry—not a download or assumption of rights.

## Recommended Stage 20

**Stage 20 — Black-pepper pilot source authorization and data-contract review.** First obtain approval to contact the appropriate agricultural and data owners. Resolve whether Idukki is supported by source evidence, identify the exact licensed weather and soil records available for the pilot, and agree on the data dictionary and quality thresholds. Only after those decisions should a separate acquisition stage be proposed.
