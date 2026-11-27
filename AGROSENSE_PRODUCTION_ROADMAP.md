# AgroSense-360 Production Roadmap

**Status:** Planning only; implementation requires review and explicit approval.  
**Research and repository state checked:** 2026-11-20.

## Current verified baseline

- The application has a React/TypeScript/Vite frontend, FastAPI backend, SQLAlchemy/Alembic, PostgreSQL/PostGIS, a 14-district Kerala catalog, 31 crop profiles and four crop categories.
- The README says the platform is a scaffold, not launched or production-ready. Real external measurements and validated model outputs are deliberately not simulated. RAG, weather retrieval, soil integrations, inference and disease analysis are not connected; unavailable AI endpoints return 503.
- Crop profiles and district-crop suitability rows remain pending. No verified agronomic measurements, crop outcomes, disease field labels or trained models exist.
- No source is approved for commercial training. Two ERA5-Land archives were acquired and reconciled as existing files; that record establishes historical acquisition and archive-integrity facts only, not whether acquisition was authorized or permission for portfolio display, research, sharing, training, commercial use, or deployment. Both remain rejected for training and should be preserved unchanged. Any proposed activity requires separate, valid project-owner authorization and applicable source-owner rights. Commercial use remains separately gated.
- Audit detail: request 1 has only two principal time-varying timestamps; request 2 has 12 irregular timestamps per principal variable. Both are global 0.1-degree grids, but Kerala-specific missingness was not established. The declared GRIB message-length discrepancies in `tvh.grib` and `tvl.grib` remain unresolved.
- The current soil and disease trainers use random splits that the inventory identifies as leakage risks. Do not report their metrics as production validation.
- The user-reported development laptop is Windows 64-bit, Ryzen 3 7320U, 8 GB RAM (about 7.24 GB usable), integrated AMD Radeon, and 352 GB free at inspection. CUDA is not assumed.

## Target architecture

```text
Official/licensed sources
     | source/license manifest, immutable snapshots, hashes
     v
Versioned ingestion + quality gates ----> object storage (raw originals)
     |                                      |
     +--> validated daily/hourly features  +--> Parquet/Zarr derivatives
                    |                                      |
                    v                                      v
             PostGIS district context <--- feature snapshots
                    |
        +-----------+----------------------+
        |                                  |
        v                                  v
   Approved ML registry             Curated knowledge/RAG
        |                                  |
        +---------------+------------------+
                        v
               FastAPI read-only services
                        |
               evidence/uncertainty gates
                        |
                  React interface
```

Raw climate rasters and image collections belong in approved object storage, not PostgreSQL rows or Git. PostgreSQL/PostGIS should hold operational records, district/crop references, compact validated aggregates, source metadata, inference metadata and retrieval indexes. Any vector extension/table, new source tables, or new API contracts require a later schema/migration review; none is proposed or changed here.

## Phased roadmap and approval gates

### Phase 0 - Review and scope freeze

**Deliverable:** owner-approved versions of the four Stage 13 planning documents.  
**Gate:** resolve portfolio versus commercial scope, weather UTC versus IST day semantics, model targets, privacy rules, provider budget and acceptance owners. Keep current training and acquisition gates closed until documented.

### Phase 1 - Source, license and geography readiness

**Deliverables:** exact resource-level rights evidence; approved district boundary asset and version; source/target dictionary; acquisition request manifest template; feature and label definitions.

- Reconfirm ERA5-Land public-demo terms for the exact request and preserve required attribution. Commercial and training use requires separate approval.
- Identify authorized, licensed district polygons and verify the provisional request envelope covers every district.
- Resolve or explicitly exclude unverified sources: KAU structured agronomy, district crop/yield records, mandi market data, SoilGrids product license and WoSIS provider rights, and PlantVillage/PlantDoc image-level rights.
- Define labels for crop recommendations, soil suitability, disease and risk. If there are no appropriate labels, do not advance that pipeline.

**Gate:** named reviewer approves each exact source/resource/version for its stated scope; all unresolved terms remain blocked/conditional.

### Phase 2 - Reproducible data foundation

**Deliverables:** versioned ingestion CLI/workflow; immutable raw object storage; request/source manifest; checksum and duplicate-prevention policy; schema and quality report; logs/alerts.

- Use the proposed monthly ERA5-Land request pattern only after approval. Start with a small approved pilot, verify exact CDS fields, output semantics, accumulation boundaries and district coverage, then proceed.
- Store raw request outputs unchanged, with source and license metadata, request fingerprint, task ID, retrieval time, SHA-256, member hashes and quality result.
- Produce separate, reproducible, chunked gridded/district derivatives only in an approved later data stage. Do not use the already rejected archives as training inputs.
- Local processing is preferred for the estimated bounded data volume. Reserve at least the planned 5 GB only after confirming actual output sizes. Use cloud storage for durable, access-controlled snapshots and cloud compute only when measured workloads require it.

**Gate:** all expected dates/variables/units, CRC/checksum, spatial/district coverage, missingness and accumulation checks pass; unresolved anomaly/data-source concerns are recorded and signed off.

### Phase 3 - LLM/RAG evaluation (parallel after source rights)

**Deliverables:** provider privacy/budget decision, source allowlist, ingestion and citation tests, Pydantic response contract, bilingual evaluation set, prompt-injection and abstention report.

- Begin with public, rights-cleared content and synthetic/non-sensitive questions.
- Compare provider candidates using identical tasks; measure support/citation, abstention, Malayalam terminology, latency, provider failure and spend.
- Create retrieval indexes only after the selected embedding model, dimensions, metadata filters, retention, and schema/migration have been approved.
- Keep unavailable UI/API behavior explicit until quality and privacy gates pass.

**Gate:** every asserted fact is evidence-bound; unsupported inputs abstain; retrieved instructions cannot trigger privileged tools; provider spend/retention and user-data policies are approved.

### Phase 4 - Labels and task-specific ML baselines

**Deliverables:** approved label collection protocol; group/spatial/time split manifests; baseline comparison; model card and independent evaluation report.

Order of work:
1. Weather descriptive features and data-quality baselines (not ML training).
2. Weather forecasting/risk only after a target and independent reference labels exist.
3. Soil-based suitability only after georeferenced lab measurements and crop outcomes are available.
4. Crop ranking only after expert-verified crop/season/district labels or outcome data are justified.
5. Disease recognition only after image rights, expert labels and a Kerala field test set are approved.

Use CPU-first regularized/GAM/gradient-boosted tabular baselines. A cloud GPU is optional for a licensed, sufficiently labeled vision experiment; no model is trained in this stage. Replace random split logic before any reported model evaluation.

**Gate:** leakage-safe holdout, class/region subgroup metrics, calibration/uncertainty, baseline comparison, expert review and governance sign-off all pass.

### Phase 5 - Controlled API integration and operations

**Deliverables:** versioned read-only inference/RAG routes, typed request/response contracts, authorization tests, monitoring and rollback playbook.

- Keep model training outside the API runtime. Load only a signed/approved registry artifact.
- Keep inference requests small and validate district/crop IDs, units, data freshness and missingness.
- Add provider/model and evidence versions to responses and observability records.
- Use deterministic fallback and abstention. Do not fall back silently to another LLM provider or stale weather.
- Release behind feature flags and a small canary; keep prior model and rollback path.

**Gate:** access control, data deletion/retention, rate/budget limits, p95 latency under a measured SLO, error/abstention dashboards, rollback test, and public-demo privacy review.

### Phase 6 - Production readiness review

Require security/privacy review, lawful source and model use, disaster recovery, object-storage backup/restore test, API abuse controls, capacity/cost test, model monitoring and drift response, incident ownership, source re-review triggers, and documented user-facing limitations. Do not call the platform production-ready until these are evidenced in a separate approval.

## Cross-cutting engineering decisions

| Area | Proposed choice | Trade-off / condition |
|---|---|---|
| Local development | Windows virtual environment, chunked CPU workflows, small pilot files; no CUDA/local foundation LLM assumption | Slower image training; cloud compute only after rights, budget and workload justify it |
| Raw data | Immutable, versioned object storage; checksums; Git contains only manifests/pointers | Cloud provider/cost/retention and exact license obligations remain unresolved |
| Dataset versioning | DVC or equivalent content-addressed remote, plus canonical JSON provenance manifest | Select backend only after storage/security/budget review; never commit raw binaries |
| Processing | Idempotent monthly jobs; deterministic transforms; bounded chunking; schema and quality gates | Monthly requests increase job count but reduce memory and recovery cost |
| Analytical storage | Parquet for tabular features; chunked NetCDF/Zarr for gridded arrays; PostGIS for boundary/geometry and compact district aggregates | Choose a canonical derivative format after a pilot and license review |
| ML tracking | MLflow tracking/registry candidate; immutable model/data lineage | Requires protected artifact store and owner; not currently installed or configured |
| LLM | Provider-neutral server-side adapter; Pydantic output validation; hybrid RAG; paid usage budget for production | Provider remains unselected pending multilingual, privacy and cost evaluation |
| Retrieval | Supabase Postgres full-text plus pgvector after a reviewed migration | Current schema/extension state not inspected or changed; cannot add vectors before model dimensions are selected |
| Client UX | Clearly distinguish measured/source estimate, model prediction, user-provided data and unknown | Requires product design approval and source-citation UX |

## Risk register

| Risk | Consequence | Planned control |
|---|---|---|
| Treating global ERA5-Land as Kerala-observed truth | False local precision | Preserve reanalysis label; district boundary/cell and station validation; report uncertainty |
| Incorrect accumulation/timezone handling | Wrong rainfall/radiation totals or day boundaries | Verify forecast step metadata and test month/year/leap boundaries; explicitly choose UTC or IST aggregation |
| Incomplete or unlicensed labels | Invalid training/use rights | Fail-closed inventory gate; reviewer evidence; no model training until approved |
| Small number of independent district/farm outcomes | Overfit and misleading metrics | Group/spatial/time splits; report sample coverage; stop if evidence is too small |
| Free-tier provider data use or vendor retention | Exposure of farm/user data | Synthetic-only free-tier evaluation; paid production terms/privacy review; minimize provider payload |
| LLM citation/injection failure | Unsupported or unsafe agronomic advice | RAG allowlist, hard authorization, citation validator, no arbitrary tools, abstention and adversarial tests |
| Laptop memory/disk pressure | Crashes or duplicate/raw data loss | Monthly chunks, streaming I/O, capacity checks, immutable raw store, avoid duplicate decompressed copies |
| Silent source/model drift | Outdated recommendations | Pin source/model versions; freshness metadata, scheduled revalidation and rollback |

## Estimated effort/storage and assumptions

The proposed weather rectangle and 4-byte-value calculation in the [weather plan](./KERALA_WEATHER_ACQUISITION_PLAN.md) yield about **1.349 GiB** of uncompressed values for the selected six daily fields and two hourly accumulated fields, before compression, coordinates and boundaries. A **5 GB planning reserve** is proposed, not a measured CDS archive size. The user reported 352 GB free on the laptop; recheck capacity immediately before any future acquisition.

No delivery dates or model accuracy targets are asserted. The critical path is rights and boundaries -> weather pilot/QA -> reproducible snapshot -> valid labels -> evaluation -> controlled integration.

## Decisions still required

1. Portfolio-only work or future commercial operation; who approves dataset and model decisions?
2. Which official, licensed district boundary/version governs all-14-district checks?
3. Are daily UTC statistics acceptable, or must daily summaries align to IST (UTC+05:30)?
4. What exact crop-recommendation outcome is supported by available ground truth?
5. Who can collect/approve soil laboratory and field outcome labels?
6. Which disease classes, image rights and Kerala field evaluation sites are in scope?
7. Provider, data-processing terms, region, retention, monthly budget and latency SLO?
8. Where will immutable raw and model artifacts be stored, who has access, and what is the retention period?
9. Which data-quality thresholds, district coverage minimums and abstention behavior are acceptable?

## Approval boundary

This roadmap is not approval to implement, submit a CDS request, download or preprocess data, alter database schema, train a model, configure providers, or deploy. Review and approve the plans first; acquire only after a separate explicit decision and completion of the rights and data-quality gates.

## Project references

- [README](./README.md)
- [Dataset inventory](./DATASET_INVENTORY.md)
- [Dataset licensing strategy](./DATASET_LICENSING_STRATEGY.md)
- [Local development guide](./LOCAL_DEVELOPMENT_GUIDE.md)
- [ERA5-Land quality assessment](./ERA5_LAND_QUALITY_ASSESSMENT.md)
- [ERA5-Land acquisition report](./DATASET_ACQUISITION_REPORT.md)
- [Stage 13 weather plan](./KERALA_WEATHER_ACQUISITION_PLAN.md)
- [Stage 13 LLM design](./AGROSENSE_LLM_ARCHITECTURE.md)
- [Stage 13 ML design](./AGROSENSE_ML_ARCHITECTURE.md)
