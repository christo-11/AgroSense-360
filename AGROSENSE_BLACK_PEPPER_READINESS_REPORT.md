# AgroSense-360 Black Pepper Pilot Readiness Report

## Executive decision

The black-pepper pilot is **not ready for agricultural recommendations or ML training**. Idukki is a reasonable catalogue-level candidate to investigate, but its black-pepper relevance is **provisional**: the existing README pairs Idukki with cardamom as an initial project focus, and no inspected repository source supports an Idukki/black-pepper relationship. No alternative district is supported by the available evidence.

The repository contains two acquired ERA5-Land archives with recorded file-integrity evidence, but they are sparse, irregular, and explicitly rejected for training. No black-pepper soil observations, verified crop requirements, production labels, or locally validated weather series are available. No database/API/ML changes were made; a standalone in-memory contract validator and tests were added to make future data acceptance rules executable.

## Evidence checked

- Branch `main` and worktree status; all pre-existing changes were preserved.
- Crop/district migration seed, SQLAlchemy models, catalogue endpoints/schemas, and current catalogue tests.
- Current `source_inventory.json`, ERA5-Land acquisition manifest, and ERA5 quality report.
- `README.md`, `DATASET_INVENTORY.md`, Stage 17/18 governance and quality reports, Kerala crop audit, and data readiness/weather specification.
- Existing dataset-governance tests and training approval rules.
- The ERA5 archive files were located under `data/raw/`; recorded and actual sizes match: 647,003,080 bytes and 2,026,384,498 bytes. The quality report records ZIP CRC checks as `PASS`. File integrity does not change the quality/training decision.

Live catalogue/database state was not queried. No external API or publisher was contacted.

## District selection

| Evidence | Status |
| --- | --- |
| Idukki is a seeded Kerala district | `VERIFIED` as a catalogue entry |
| The README names Idukki as an initial focus with cardamom | `VERIFIED` as project-planning text only |
| Black pepper (`Piper nigrum`) is linked to Idukki by a cited dataset/publication | `MISSING` |
| Idukki black-pepper cultivation/suitability is established | `NOT ESTABLISHED` |
| Alternative district has stronger black-pepper evidence | `NOT FOUND` |

Therefore Idukki remains `PROVISIONAL` for this pilot. The requested scientific name is user-supplied; the crop seed's `scientific_name` field is null and needs an attributable taxonomy reference before database verification.

## Feature readiness matrix

| Proposed feature or field | Status | Evidence and remaining work |
| --- | --- | --- |
| Black-pepper common-name catalogue row | `VERIFIED` | Migration seeds “Black pepper”; this does not prove a local crop relationship. |
| Scientific name `Piper nigrum` | `REQUIRES_VALIDATION` | User supplied; no scientific-name value or citation in the seeded record. |
| Kerala/Idukki catalogue identity | `VERIFIED` | Migration seeds Kerala district names, including Idukki; no boundary polygon/version is present in that migration. |
| Idukki black-pepper pilot relevance | `PROVISIONAL` | README's initial Idukki/cardamom note is not black-pepper evidence; need a source tied to the exact crop and district. |
| Black-pepper variety, season, practices, and agronomic requirements | `MISSING` | No sourced profile values or variety rows found. |
| Weather archive acquisition and file integrity | `VERIFIED` at file level | Manifest sizes match the two found files and quality report records CRC `PASS`. This is not a weather-quality approval. |
| Existing weather observations as pilot series | `PROVISIONAL` / insufficient | Two timestamps in one archive; 12 irregular timestamps in the other; 65.87% global missingness. No continuous Idukki series. |
| Kerala/Idukki weather spatial coverage | `REQUIRES_VALIDATION` | 0.1-degree global grid intersects Kerala, but no district polygon or Kerala-only cell validation was performed. |
| Weather variable units/time | `REQUIRES_VALIDATION` | Quality metadata records UTC timestamps and source units (e.g. temperature K, precipitation m); normalized conversions/accumulation semantics have not been approved for the pilot. |
| Duplicate weather timestamps | `PROVISIONAL` | The per-variable timestamp lists inspected contain no repeated entries (0 of 94 and 0 of 609 entries); this is not a complete independent duplicate-record audit of all archive messages/grid observations. |
| Black-pepper soil measurements | `MISSING` | No lab samples or measured pH, N, P, K, texture, or organic-carbon records. |
| Soil model estimates | `MISSING` as project observations | SoilGrids is metadata-only in the inventory; no local raster/point values were acquired. Any future values must remain `ESTIMATED`, not `MEASURED`. |
| District/crop production or yield | `MISSING` | The data.gov.in resource is a candidate only; Kerala/black-pepper schema, units, coverage, and terms are not verified. |
| Portfolio/research display | `VERIFIED` only within source-specific conditions | Source inventory grants portfolio/research-only use for some candidates; preserve attribution and keep other rights unresolved. |
| ML training permission | `NOT_AUTHORIZED` | No source is approved for training; existing ERA5 archives are explicitly `REJECT_FOR_TRAINING`. |
| Commercial use | `NOT_AUTHORIZED` | Source inventory has 0 commercially `APPROVED` sources. |

## ERA5-Land weather assessment

| Check | Archive 1 | Archive 2 |
| --- | --- | --- |
| Recorded format | NetCDF-4/HDF5 plus a NetCDF classic member | GRIB editions 1 and 2 |
| Recorded acquisition time | 2026-11-20 02:22:48 UTC | 2026-11-20 02:23:35 UTC |
| Recorded / actual size | 647,003,080 / 647,003,080 bytes | 2,026,384,498 / 2,026,384,498 bytes |
| Dynamic timestamps | 2, 2024-01-03 03:00–06:00 UTC, 3-hour interval | 12 distinct times, 2011-01-11 13:00 to 2011-01-29 22:00 UTC |
| Irregular gaps | Only one 3-hour interval is not a series | 2, 7, 15, 63, and 327 hours |
| Grid | Global 0.1° spacing; grid intersects Kerala | Global 0.1° spacing; grid intersects Kerala |
| Missingness | 8,541,474 of 12,967,200 values per main field (65.87%) | 4,270,737 of 6,483,600 points per dynamic message (65.87%) |
| Units observed in report | `t2m`: K; `tp`: m | `2t`/`2d`: K; `tp`: m; `10u`/`10v`: m s⁻¹ |
| Duplicate timestamp check | No repeats in per-variable timestamp lists (94 timestamp entries checked) | No repeats in per-variable timestamp lists (609 timestamp entries checked) |
| Kerala mask/cell values | No administrative polygon or Kerala-only values checked | No administrative polygon or Kerala-only values checked |
| Quality/training decision | `NEEDS_MORE_DATA`; `REJECT_FOR_TRAINING` | `NEEDS_MORE_DATA`; `REJECT_FOR_TRAINING` |

The report stores the timestamps explicitly in UTC and variable-level unit metadata. Product version and exact request parameters remain unresolved. The source grid's intersection with Kerala is not evidence of valid Idukki coverage. Ancillary records do not extend the sparse dynamic weather series. The quality report also notes message-length discrepancies in two ancillary GRIB1 members.

## Soil readiness

No soil measurement files or records were identified. The inventory lists SoilGrids as `metadata_verified_only`, not as an acquired local observation dataset. Its model estimates cannot be treated as laboratory ground truth; repository documentation says its mapped properties do not include phosphorus or potassium. WoSIS has provider-specific terms and no selected local profile. Soil Health Card/lab data have no verified bulk export, local coverage, or dataset-level permission.

Required before soil analysis: authorized site/sample records with coordinate accuracy, date, depth, analyte, unit, method/extraction fraction, laboratory/QC, crop/site context where recorded, source version, and written reuse permission. Weather features cannot fill missing soil fields.

## Tests and implementation boundary

Added a standalone, no-I/O Pydantic contract at `backend/scripts/black_pepper_pilot_contract.py` and focused tests at `backend/tests/test_black_pepper_pilot_contract.py`. Tests cover missing source provenance, unknown crop/district references, invalid units, duplicate observation natural keys, missing/non-UTC timestamps, training on an unapproved source, unverified soil measurements, and estimated-versus-measured labeling. Test fixtures use null/missing values and are never stored as agricultural observations.

The contract is not connected to FastAPI, the database, or training entry points. No production code, catalogue record, database schema, or migration was modified.

### Validation result

Using `PYTHONPATH=backend python -m pytest --noconftest backend/tests/test_black_pepper_pilot_contract.py -q`, all 10 focused contract tests passed. The repository application conftest was excluded because loading it imports GeoAlchemy 2, which is not available in the current Python environment; this did not affect the standalone contract test module. No packages were downloaded or installed.

## Risks and blockers

1. No source-backed black-pepper/Idukki evidence; district choice remains provisional.
2. No verified scientific-name citation in the catalogue.
3. No black-pepper soil measurements or locally validated weather series.
4. ERA5 archives have severe temporal and global-grid missingness and do not support the stated pilot question.
5. Candidate sources have unresolved versions, rights, local coverage, or training permission; portfolio approval does not resolve these.
6. Existing data model links sources at a profile/relationship level rather than at each claim; the new contract is a standalone design aid, not production enforcement.

## Recommended Stage 20

**Stage 20 — Source authorization and pilot evidence confirmation.** With explicit user approval, contact the relevant data owners to identify exact, versioned KAU/official district evidence, historical station/gauge records, and authorized soil-lab samples. Resolve Idukki's black-pepper relevance, licenses/attribution, data fields, spatial/temporal coverage, and use permissions before requesting or acquiring any dataset. Keep training disabled until these evidence and quality gates pass.
