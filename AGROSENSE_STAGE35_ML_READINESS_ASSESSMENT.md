# AgroSense-360 Stage 35 — ML Readiness Assessment

**Assessment date:** 2026-11-23  
**Decision:** **NOT READY FOR MODEL TRAINING OR DEPLOYMENT**

This assessment uses the existing project evidence and the Stage 28 archive reliability decisions. It does not train a model, authorize a dataset, or change any Stage 23 status.

## Executive assessment

The project has candidate model designs and a fail-closed dataset approval/provenance gate, but it does not have a verified, authorized black-pepper training dataset or valid crop-specific target labels. The existing ERA5-Land archives are not sufficient weather training inputs: request 1 is **ACCEPTABLE WITH LIMITATIONS** but contains only two dynamic timestamps; request 2 is **REJECTED** pending GRIB1 clarification and contains only 12 irregular timestamps per dynamic variable. Both remain unsuitable for production weather, local decision support, and ML training.

**Current state:** no source is approved for ML training; no black-pepper soil, yield, disease, or crop-suitability labels are verified; Idukki remains provisional; no model has been evaluated or deployed.

## Readiness by dimension

| Dimension | Evidence | Readiness |
|---|---|---|
| Historical coverage | Request 1: 2024-01-03 03:00 and 06:00 UTC only. Request 2: 12 timestamps per dynamic variable across four January 2011 dates, with irregular gaps. | **Insufficient** for seasonal prediction or robust training |
| Sample count | Two archives exist, but timestamp/message counts are not independent crop-label sample counts. No row-level, site-level or outcome dataset is present. | **Not assessable / insufficient** |
| Feature availability | Archives list temperature, precipitation, wind, dewpoint, soil-layer and other reanalysis variables. Stage 33 features remain designs only; no authorized normalized feature snapshot exists. | **Candidate variables only** |
| Target availability | No verified Idukki black-pepper yield, disease, soil laboratory, expert suitability, crop-stage, or weather-impact targets. Catalogue profile/suitability records are not verified labels. | **Blocked** |
| Missingness | Existing quality report records about 65.87% global missing values per main grid field; this is not Kerala-specific. Request 2 also records marker `9999`; affected GRIB1 members have unresolved header mismatch. | **Fails/incomplete for intended use** |
| Class balance | No labeled target set, hence no class counts or balance statistics. | **NOT ASSESSED** |
| Geographic representation | Global grid intersects Kerala, but no Kerala district mask/per-cell coverage or local independent validation exists. Idukki/black-pepper link is unverified. | **Not representative/verified** |
| Rights and governance | Stage 23 records no current acquisition/use authorization, no source-owner permission, and no source approved for training. | **NOT AUTHORIZED** |
| Reproducibility | Existing JSON inventory, manifest, quality evidence and signed training gate exist; exact ERA5-Land product version and original request history remain unpinned/unverified. | **Incomplete** |
| Model validation/deployment | No trained model, accepted labels, locked test set, metrics, model registry entry, or deployment evidence. Current insight service is unavailable until verified services exist. | **Not ready** |

## Task-specific readiness

| Candidate task | Required target evidence | Current blocker |
|---|---|---|
| Black-pepper district/field suitability | Expert-verified, crop/variety/site/season-specific suitability or valid observed outcome with provenance | No verified Idukki crop evidence, expert labels, or suitability records |
| Yield/productivity prediction | Official or measured crop/area/production/yield records with units, season, geography and management context | District-crop resource is unverified; no black-pepper yield labels |
| Disease/pest recognition or risk | Rights-cleared, expert-confirmed disease observations/images, severity and independent field test set | No verified black-pepper disease labels; PlantVillage/PlantDoc source-image rights and local applicability unresolved |
| Soil-based suitability | Depth/method/unit-documented laboratory soil and verified crop response/suitability target | No authorized local soil measurements or crop outcomes; SoilGrids is modeled context, not lab ground truth |
| Weather prediction | Appropriate observed weather/event target and continuous, quality-checked features available at forecast issue time | Existing data are sparse estimates; no independent Idukki station/gauge target or operational forecast archive |

## Leakage and evaluation risks

Any future ML design must explicitly address:

- **Temporal leakage:** ERA5/reanalysis values may be revised, and analysis fields are not a forecast available at a historical issue time. Use only inputs available before the prediction cutoff.
- **Overlapping windows:** rolling weather features, duplicate grid cells, adjacent dates and repeated reports must not cross train/test partitions.
- **Spatial leakage:** nearby cells, farms, stations or district aggregates may share weather and target information. Group by farm/site/station and use spatial blocks or held-out districts.
- **Target leakage:** harvest/production totals, suitability notes, disease diagnosis, post-event values, or target-derived crop statistics must not enter predictor features.
- **Label leakage and confounding:** neighboring plot samples or the same plant/image session must remain in one split; record management, cultivar and sampling context.
- **Soil circularity:** do not evaluate SoilGrids or a model on soil profiles that may have contributed to that gridded product without checking its source lineage.
- **Threshold/transform leakage:** fit imputation, scaling, percentile thresholds, feature selection and calibration inside training folds only.
- **Geographic mismatch:** global missingness or grid intersection with Kerala is not proof of valid Idukki coverage; no plot-level claims from coarse grids.

## Future data and validation gates

Before any training can be proposed:

1. Define one target, prediction horizon, unit of analysis, geography, crop/variety context and intended use.
2. Obtain exact, purpose-authorized datasets and targets; pin resource versions, terms, request metadata and checksums.
3. Pass the existing governance gate: signed `APPROVED` source review, explicit permitted training purpose, immutable matching provenance, quality/relevance verification and eligible records.
4. Resolve all parser/format issues; apply the Stage 32 checks and independently validate weather estimates against suitable, authorized observations.
5. Establish source and target sample counts, missingness, class balance, spatial/temporal coverage, label uncertainty and representativeness before selecting a model.
6. Pre-register train/validation/test boundaries. Use rolling-origin temporal validation for forecast tasks, and group/farm/station or spatial-block holdouts for generalization. Keep a locked final test period/geography.
7. Compare with simple, domain-approved baselines; report uncertainty, calibration and per-district/crop/season performance. Define an abstention outcome for unsupported inputs.
8. Document model/data/feature lineage, label definitions, code/environment, checksums, metrics and review decision before any deployment discussion.

The existing weather quality specification includes provisional research gates (such as multi-year completeness and independent station validation). Those thresholds require scientific approval for the actual task and are not evidence that any current dataset passes.

## Governance and status boundary

The source inventory currently has no training-approved source. Stage 23 remains: project-owner authorization pending/no for use actions, source-owner permission not received, acquisition/use not authorized, and no ML training authorization. The Copernicus inquiry remains **NOT SUBMITTED**; owner approval is **NOT RECORDED**; no external response exists.

No sample count, class distribution, model metric, licence permission, or performance claim is invented here. No trained model or feature set was created. **Training and deployment are blocked.**
