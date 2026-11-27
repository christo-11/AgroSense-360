# AgroSense-360 ML Architecture

**Status:** Design only. No model is approved, trained, evaluated or deployed.  
**Research checked:** 2026-11-20.

## Current readiness

The repository is a scaffold with 14 Kerala districts, 31 crop profiles and four crop categories. Crop profiles and district-crop suitability records are pending; no suitability associations or verified crop/yield labels are present. The current dataset governance gate rejects non-approved data before training entry points access ML inputs. The two ERA5-Land archives are `NEEDS_MORE_DATA` and `REJECT_FOR_TRAINING`; other candidate sources in the inventory are blocked, conditional or not acquired.

Therefore the following are target designs, not claims that training data or models exist. Do not use weather variables as crop recommendation labels. Do not use SoilGrids estimates as laboratory truth.

## Pipeline overview

```text
Licensed sources + verified labels
        |
        v
Immutable raw snapshot -> schema/quality gates -> versioned feature snapshot
        |                                    |
        |                                    v
        +----------------------------> leakage-safe training/evaluation
                                             |
                                      model registry + model card
                                             |
                                  approval + canary deployment
                                             |
                              versioned FastAPI inference endpoint
```

Every model release must point to a dataset snapshot, source/license record, feature pipeline version, validation split manifest, training code commit, dependency lock, model artifact checksum and evaluation report.

## Common modeling and release rules

- Keep geography, time, source, farm/field, crop, variety and label provenance on each row/image. Split by the true independent unit; random row/image splits are not adequate where records share a farm, plot, season or plant.
- Fit imputers, scalers, feature selection, calibration and resampling on training folds only. Preserve missingness indicators. Never use future weather or labels in past predictions.
- Establish a simple, domain-approved baseline before trying boosted trees or neural networks. Report uncertainty and subgroup performance; no single aggregate accuracy is enough.
- Evaluate on a locked, untouched test period/geography after model selection. Use temporal and spatial/group holdouts; do not tune against the final test set.
- Explain boosted models with feature effects/SHAP or permutation analysis, but label these as model explanations, not causal agronomic effects. Document feature availability at decision time.
- Save metrics and artifacts in MLflow Tracking/Model Registry or an approved equivalent. Registry metadata must bind the exact data snapshot/checksum, source/license decision, feature schema, parameters, code revision, environment, training seed and model card.
- Serve only signed/approved artifacts through typed FastAPI endpoints. Validate units, ranges, input freshness and model version. Provide abstention for out-of-domain or missing inputs.
- No foundation model training. No CUDA assumption. CPU-first tabular development is appropriate; image training may justify approved cloud GPU compute after label and licensing gates pass.

## Pipeline specifications

### 1. Crop suitability and recommendation

**Question/target:** Rank crops for a district/field and season, but only after creating authoritative ground truth. Suitable targets are expert-verified crop suitability class/score or crop-specific observed yield/production outcomes with area and management context. Do not train a “recommendation” label from weather patterns or from the model's own recommendations.

- **Features:** verified district/field location and season; soil laboratory measurements with depth/method/units; weather summaries from a validated uninterrupted series; crop calendar; irrigation/management; cultivar; elevation/topography where licensed; and known crop availability. Include missingness and data freshness.
- **Labels required:** season- and location-specific expert agronomic suitability or observed crop outcome/yield, with harvest area, crop identity/variety and source. District-crop catalog rows currently pending are not labels.
- **Dataset requirements:** representative examples across districts, crops, seasons and management systems; licensed yield/area records; KAU/extension expert review; known label definitions and date. The current yield and KAU sources are conditional/unverified.
- **Baselines:** reviewed KAU/extension rule table with explicit “unknown” cases; naive district/season historical crop prevalence only as a comparison, never as suitability truth.
- **Candidates:** regularized logistic/ordinal regression or ranking model first; GAM for interpretable nonlinear agronomic response; CPU XGBoost/HistGradientBoosting only if sample size supports it. A ranking model may be more defensible than a forced single-class prediction.
- **Metrics:** macro-F1/balanced accuracy for classes; precision@k/recall@k for ranking; top-k expert agreement; calibration/Brier score for probabilities; MAE and uncertainty interval coverage for yield targets; results stratified by district, crop, season and input-data coverage.
- **Validation:** hold out later seasons and spatial blocks/districts; group repeated observations from the same farm/plot; keep each crop-season label and derivative features in one split.
- **Leakage risks:** future/harvest-date weather, target-derived crop area statistics, duplicate crop profiles, spatially duplicated district aggregates, using the same sample both in SoilGrids training and as a measured target.
- **Explainability/deployment:** show the top supported factors and missing evidence, not causal claims; return a ranked shortlist with “insufficient data” when appropriate. Keep model version and evidence citations in each response.

### 2. Weather feature analysis

Separate deterministic feature generation from supervised prediction. A validated weather dataset can produce descriptive features (daily temperature summaries, rainfall totals, dry-spell durations, radiation/wind summaries) without training an ML model.

- **Optional supervised targets:** future rainfall/temperature anomaly, heat/dry-spell event, or a separately defined crop-impact target. Targets must come from an appropriate, licensed reference such as quality-controlled observations or authoritative event records; no such label set is established in the current inventory.
- **Features:** strictly lagged ERA5-Land fields and summaries, seasonal/climatological baselines, location/elevation and data-quality flags. ERA5-Land is reanalysis, not a station measurement.
- **Baselines:** seasonal climatology and persistence/seasonal-naive forecasts; linear/regularized models.
- **Candidates:** generalized additive or regularized regression; CPU gradient-boosted trees for tabular lag features. Avoid deep sequence models until the sample volume and label quality justify them.
- **Metrics:** MAE/RMSE/bias for continuous forecasts; PR-AUC, recall, false-alert rate, Brier score and lead time for rare events; interval/quantile coverage for uncertainty.
- **Validation:** rolling-origin time splits and a spatially blocked holdout; train only on information available before each forecast issue time.
- **Leakage risks:** target-hour values in input windows, using future revised/reanalysis data for real-time claims, overlapping windows across train/test, inconsistent UTC/IST days, and incorrect accumulation de-aggregation.
- **Explainability/deployment:** publish data vintage, issue time, lead time and uncertainty; serve deterministic weather summaries independently of an ML forecast.

### 3. Soil-based crop suitability

- **Target:** measured crop-specific yield, survival, nutrient response or expert-verified suitability under a defined soil/crop/management condition. Soil property prediction is a separate task and requires laboratory measurements as targets.
- **Features:** lab-measured pH, organic carbon, N/P/K with extraction method, texture, depth/horizon, water retention, drainage, topography, crop/variety, management and weather; include laboratory/provider, sample date and uncertainty.
- **Labels/data:** permitted georeferenced Kerala soil profiles and field outcome records with sampling protocol, depth, unit, lab method, coordinate accuracy and consent/redistribution rights. No measurements are present; SoilGrids is modeled 250 m context and lacks phosphorus/potassium layers.
- **Baselines:** KAU/extension crop thresholds with citations; regularized regression/GAM.
- **Candidates:** interpretable GAM or regularized models; CatBoost/XGBoost only after data size, independent units and missingness are assessed.
- **Metrics:** MAE/RMSE and interval coverage for continuous response; macro-F1/recall and calibration for categories; crop/district/farm subgroup errors and spatial generalization.
- **Validation:** leave-farm/field and spatial-block-out; hold out districts or new survey rounds. Do not split replicate depths or repeated samples from one site across train and test.
- **Leakage/explainability:** do not use SoilGrids values derived partly from the same target profiles as independent labels/features without provenance checks. Show measurement method/depth and uncertainty; explanations are associations, not causal fertilizer prescriptions.
- **Deployment:** return an evidence-qualified advisory only when inputs match training support. Otherwise present measured values and refer to a qualified agronomist.

### 4. Crop disease recognition (conditional)

- **Target:** expert-confirmed crop/disease/healthy class plus an explicit unknown/out-of-distribution outcome.
- **Features:** image and capture metadata (crop, variety, device, lighting, district, date, plant/leaf group); no EXIF coordinates unless authorized.
- **Labels/data:** documented image-level rights, expert diagnosis, severity/healthy labels, duplicate groups, crop/variety, capture conditions, and an independently curated Kerala field test set. PlantVillage and PlantDoc rights/provenance remain conditional; neither is verified Kerala field data.
- **Baselines:** image-quality rejection, majority class, and a simple frozen pretrained feature/classifier baseline.
- **Candidates:** transfer-learn a compact MobileNet/ResNet-class vision backbone with a frozen-feature baseline before fine-tuning. Check the pretrained weights' license. Do not train from scratch.
- **Metrics:** macro-F1, per-class precision/recall and confusion matrix; field-test recall, calibration, abstention and out-of-distribution performance. Do not report only overall accuracy.
- **Validation:** group all images of the same leaf/plant, farm, capture session and near-duplicate cluster into one split; hold out farms/districts and an independent field season.
- **Leakage/explainability:** do not let background, watermark, image-source or augmentation duplicates reveal the label. Saliency maps are inspection aids, not proof of diagnosis.
- **Deployment:** CPU inference on the laptop is a development goal, not a measured SLA. Convert/quantize to ONNX only after accuracy and calibration comparison. Cloud GPU training is optional only after rights, labels and budget approval. The API should abstain at low confidence and advise expert confirmation.

### 5. Agricultural risk and anomaly detection

- **Target:** define separate events such as flood, drought, heat stress or pest outbreak. An anomaly score is not a probability that damage occurred and is not a causal diagnosis.
- **Features:** validated weather history, soil moisture, crop stage/season, terrain, drainage, crop/variety and verified local event reports.
- **Labels/data:** timestamped, geolocated and independently validated impact/event records with event definition and reporting bias notes. No project event-label set is present.
- **Baselines:** climatological percentile/z-score and simple, expert-reviewed thresholds; use an unsupervised detector only to prioritize review.
- **Candidates:** Isolation Forest for anomaly triage; calibrated logistic/GAM or gradient-boosted trees for supervised event risk only when sufficient positives and negatives exist.
- **Metrics:** event recall, precision/PR-AUC, false alerts per district/time, lead time and Brier/calibration; report recall at a specified operational alert burden.
- **Validation:** temporal and district/farm block holdouts; prevent neighboring grid cells or duplicate incident reports from leaking across splits.
- **Explainability/deployment:** expose anomaly vs. supervised risk as different outputs, cite source data and report data staleness. Route uncertain events to human review, not automatic advisories.

## Hardware and compute plan

The supplied HP 255 G10 has 8 GB RAM, an AMD Ryzen 3 7320U and integrated Radeon graphics; CUDA is not available by assumption. Use CPU-first scikit-learn and XGBoost (`device="cpu"`, constrained threads, histogram trees) for small tabular baselines. Process gridded data in bounded chunks and avoid all-global arrays. Reserve local disk for immutable raw files and use cloud object storage for versioned backups.

Do not install or run a large local LLM as part of ML. For image training, first prove a labeled/rights-cleared dataset and a CPU baseline; then price a short-lived cloud GPU experiment with budget limits and data-retention controls. Production inference can begin with small CPU tabular models; image model hosting or higher scale is a separate cost/latency decision.

## Data-to-model traceability

Each dataset snapshot should carry the source inventory ID, exact resource/version/license, request parameters, retrieval time, original SHA-256, quality report, spatial/temporal coverage, units, missingness, label definition and approval record. Each feature snapshot should carry transformation code/config hashes and input snapshot IDs. Each model artifact should carry training/evaluation split IDs, seed, library versions, hyperparameters, metrics by subgroup, calibration, model card, artifact SHA-256 and approval.

Use DVC or an equivalent content-addressed data remote for large snapshots; commit only manifests/pointers, never raw data. MLflow Tracking/Model Registry is a proposed model lineage and promotion layer, subject to a future storage/operations decision. Keep unapproved/conditional data outside training pipelines; the governance gate must fail before loading a model stack or reading protected inputs.

## Official technical references (checked 2026-11-20)

- [Scikit-learn cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html) (holdout and validation leakage concepts).
- [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html) (CPU is a supported device; CUDA is a separate option).
- [PyTorch transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html).
- [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/) for model versions, lineage, metadata and controlled promotion.
- [DVC data versioning](https://dvc.org/doc/start/data-management/data-versioning) for versioned data references and remote storage.
- Project gates: [README](./README.md), [local development guide](./LOCAL_DEVELOPMENT_GUIDE.md), [dataset inventory](./DATASET_INVENTORY.md), [licensing strategy](./DATASET_LICENSING_STRATEGY.md), [quality assessment](./ERA5_LAND_QUALITY_ASSESSMENT.md).
