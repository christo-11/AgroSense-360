# AgroSense-360 Independent Principal Engineer Architecture Review

**Review date:** 2026-11-20  
**Scope:** Independent review of the four Stage 13 planning documents and verification of current official CDS and LLM-provider documentation.  
**Disposition:** The plans are directionally responsible, but are **not ready for implementation or full acquisition approval**. This review does not authorize either.

## Executive assessment

The strongest parts are the fail-closed data governance, preservation of the rejected ERA5-Land archives, separation of model predictions from verified facts, and explicit acknowledgement that suitable training labels are absent. No evidence supports training or deploying an agricultural recommendation model today.

The critical corrections are:

1. Treat the proposed **481 CDS jobs as a monthly execution plan, not an unavoidable minimum**. It follows from the current scalar `year`, `month`, and `daily_statistic` schema plus the selected products. A different, hourly-only design could reduce request count substantially but would increase data volume and processing burden.
2. The weather plan's 4-byte storage arithmetic is internally consistent, but the **5 GB reserve is not evidenced** by actual CDS output sizes, archive encoding, or staging requirements. Measure the approved pilot first.
3. Specify a pilot that cross-checks the daily-statistics product against hourly source data. A pilot that only downloads the planned daily variables and precipitation/radiation cannot independently validate the daily aggregation.
4. Separate **crop suitability classification/ranking from crop yield prediction**. They have different targets and labels and must not be pooled as interchangeable ground truth.
5. Simplify the first LLM/RAG implementation. Keep the provider-neutral boundary, but begin with one paid provider candidate, a curated rights-cleared corpus, server-side evidence binding, and no production provider routing. Add embeddings, reranking, and pgvector only when evaluation demonstrates a need.
6. Correct the interpretation of free tiers and make retention, billing, and eligibility checks explicit. An OpenAI “Free” usage tier's `$100/month` entry is a usage limit, **not $100 of free API credit**.

## A. Weather acquisition review

### Verified against current official CDS/ECMWF documentation

The live process definitions at review time confirm:

| Dataset/process | Verified schema and relevant choices | Review finding |
|---|---|---|
| `derived-era5-land-daily-statistics` | Process version `1.0.0`; `variable` is an array; `year` and `month` are scalar strings; `day` is an array; `daily_statistic` is a scalar enum (`daily_mean`, `daily_maximum`, `daily_minimum`); `frequency` is `1_hourly`, `3_hourly`, or `6_hourly`; `time_zone` is a fixed list of whole-hour UTC offsets; `area` is four numbers. | The plan's January 2015 example uses schema-valid values, including the 31 January days and the `[north, west, south, east]` area order. The daily schema does not expose `data_format` or `download_format`. The catalogue describes NetCDF in a ZIP. |
| `reanalysis-era5-land` | Process version `1.0.0`; `variable`, `day`, and `time` are arrays; `year` and `month` are scalar strings; `area` is four numbers; `data_format` is `grib` or `netcdf`; `download_format` is `zip` or `unarchived`. | The proposed hourly request fields are present in the live schema. `00:00`–`23:00` are valid time selections. Schema validity does not guarantee account authorization, queue acceptance, successful execution, or the requested output size. |

The daily schema lists the proposed `2m_temperature`, `2m_dewpoint_temperature`, `10m_u_component_of_wind`, and `10m_v_component_of_wind` variables. Its statistic enum supports the selected daily means and temperature maxima/minima. The hourly schema lists both `total_precipitation` and `surface_solar_radiation_downwards`. The daily catalogue explicitly omits accumulated parameters.

The hourly process is asynchronous (`async-execute`) and returns a referenced output asset. This matters for job polling, download URL expiry, and retry design; submitting a second request is not the same as resuming a file transfer.

### Corrections and qualifications

#### Request count: correct arithmetic, overstated necessity

For the specified 2015–2024 period and monthly chunks:

- Daily statistics: `120 months × 3 scalar statistics = 360 jobs`.
- Hourly precipitation/radiation: `120 monthly jobs`.
- One extra 2025-01-01 00 UTC request for the final 2024-12-31 forecast-step-24 accumulation: `1 job`.
- Total: **481 jobs** under this plan.

This count is consistent with the currently published scalar `year`, `month`, and `daily_statistic` inputs. It is **not the only possible architecture**:

- An hourly-only design could request all six time-varying variables (temperature, dewpoint, two wind components, precipitation, and radiation) in 120 monthly requests, then derive daily statistics locally. Under the plan's 1,836-cell and 4-byte assumptions, six hourly fields are about **3.60 GiB** of scalar values before metadata/compression; the current mixed design is about **1.35 GiB**. It trades more local processing and disk for fewer jobs and one common hourly source.
- A mixed design could retain the daily product for compact temperature/dewpoint/wind summaries and keep precipitation/radiation hourly. That is simpler to process but preserves the 481-job schedule.

The current plan should present both trade-offs and seek approval for the desired balance. Do not promise fewer jobs by using multi-month selections: the live schema exposes a scalar month, so such a reduction is not established by the current contract.

#### A one-month pilot is feasible, but its validation scope must be explicit

A useful pilot should use one complete historical month, such as August 2024, and include:

1. Three daily-statistics requests (mean, maximum, minimum).
2. A single hourly reference request for that month containing the daily variables as well as precipitation and radiation. The hourly schema supports an array of variables.
3. A next-month 00 UTC boundary record (2024-09-01 00:00 UTC for an August pilot).
4. Independent reconstruction of the daily temperature/wind statistics from the hourly fields, compared against the daily product with documented tolerances.
5. Rainfall and radiation accumulation checks across ordinary hours and the month boundary, plus inspection of GRIB reference time, step, and validity time.
6. Coordinate, land-mask, missingness, and district-polygon checks against a licensed boundary version.

This is roughly five request jobs if the hourly reference and boundary are separate. A single month can verify schema, formats, units, timing, aggregation, accumulation handling, and grid coverage for the pilot area. It cannot prove completeness or quality across the full decade, verify the 2024/2025 boundary, or establish that a decade-long feature is predictive.

#### Geography and grid dimensions

The provisional area `[13.0, 74.5, 8.0, 78.0]` is correctly ordered as north, west, south, east. If coordinates land on both bounding endpoints at 0.1-degree increments, the nominal rectangle is **51 latitude × 36 longitude = 1,836 points**. This is a planning calculation, not an observed output shape. The actual returned coordinates, axis direction, endpoint inclusion, and cell mask must be checked in the pilot.

The 0.1-degree grid is angular, not a constant 9 km projected grid. Do not call every cell exactly 9 km or treat the bounding rectangle as Kerala. The plan appropriately labels the box provisional, but should include a reproducible polygon-intersection test and verify all 14 districts against the chosen licensed boundary before requesting the full history.

Missingness QA needs a stricter distinction:

- ERA5-Land fields are masked over oceans. Coastal sea cells and cells outside a district polygon are not missing land observations.
- Preserve and use the ERA5-Land land-sea mask; report land-cell coverage separately from `_FillValue`/GRIB bitmap and temporal missingness.
- Do not infer district-level weather where a district has too few representative land grid cells. Publish the coverage rule and uncertainty rather than filling gaps.
- Validate missingness by variable, date, and district after masking; a global missing percentage is not a Kerala quality metric.

#### Daily statistics and units

UTC daily statistics are valid, but they are not Kerala civil-day statistics. The daily timezone options are whole-hour offsets; UTC+05:30 is not listed. The plan correctly avoids calling UTC results IST-day values. The user must decide whether UTC is acceptable or whether hourly data should be aggregated into IST windows later.

The daily extrema are extrema of the selected hourly samples, not sub-hourly instantaneous extremes. State that limitation in any user-facing feature. Keep source units in provenance, and define feature conversions explicitly: temperature/dewpoint from K to °C, precipitation from m to mm, and radiation from J m-2 to MJ m-2 where needed. For daily precipitation/radiation totals, use the next-day 00 UTC step-24 value for the preceding UTC day; do not sum the accumulated values at each validity time. For hourly increments, difference only within a single 00 UTC forecast cycle.

#### Storage and retry/resume

The scalar arithmetic in the plan is reasonable under its assumptions: 1,836 cells, 4 bytes per value, six daily arrays, two hourly arrays, and 3,653 days / 87,672 hours. Those assumptions are not a measured CDS file size or an adequate disk-space guarantee. In particular:

- The 4-byte dtype, returned grid shape, GRIB packing, NetCDF encoding, ZIP compression, output-member layout, and boundary overhead are unverified.
- The proposed 5 GB reserve has no pilot evidence and may not cover raw files plus temporary downloads, decompression, validation, and retained derivatives.
- The project already holds two large audit archives. Count their actual occupied disk space separately from the free-space snapshot.
- Measure the pilot's compressed and extracted sizes and peak temporary-disk use; extrapolate conservatively before the full run. Recheck free space before acquisition.

The current retry wording conflates **CDS task retry** and **HTTP transfer resume**. Use a local request ledger and the supported CDS client to poll the same asynchronous task and retrieve its result where still available. A request fingerprint prevents duplicate submission in the local workflow; it does not prove server-side idempotency. Before resuming a partial file, verify that the specific download URL supports byte ranges and returns a valid `206` response. If it does not, restart the transfer to a new `.part` file after checking task status; do not resubmit a valid CDS job merely because a transfer failed. The current plan's `.part`, checksum, CRC, and no-overwrite controls are good but do not themselves implement safe resumption.

The official CDS API guide says users must accept each dataset's Terms of Use from its download form before retrieval. Internal portfolio/demo approval is not a substitute for confirming the current publisher terms, attribution, and permitted redistribution/derivatives. The advanced ECMWF datastore client is described as incubating; the guide says users need not migrate from `cdsapi` at this time. Keep the acquisition client choice conservative and pin/review its version.

### Weather decision

**Approve as planning direction:** preserve the existing archives; use official process identifiers; use monthly idempotent chunks; retain raw files; validate all dates, units, steps, checksums, land mask, and district coverage; do not train on the current archives.

**Requires correction or explicit approval before a full request:** choose mixed versus hourly-only acquisition; approve the exact boundary geometry and all-district coverage rule; choose UTC versus IST-derived days; authorize source terms and attribution; pass the pilot; and replace the unverified 5 GB reserve with measured capacity planning. No full 481-job run is approved by this review.

## B. LLM architecture review

### Strong decisions to retain

- Provider keys and model calls remain server-side.
- The application owns evidence retrieval, authorization, Pydantic validation, and fallback; vendor SDK types should not leak into domain models.
- Missing evidence must yield abstention, not plausible invented agronomy.
- Initial evaluation should use synthetic/non-confidential inputs and approved sources.
- Keep the assistant unavailable while sources, privacy, and evaluations are blocked.

### Critical gaps and expensive choices

1. **The document compares providers but does not produce a concrete selection protocol or a budget scenario.** Provider marketing statements are not comparative evidence for Malayalam agronomic Q&A. Benchmark the same expert-reviewed English/Malayalam cases, with citation correctness and abstention as hard gates.
2. **The OpenAI Free-tier statement is easy to misread.** The current rate-limits page lists a Free tier with a `$100/month` usage limit and eligible-geography qualification; it describes a limit, not a `$100 free-credit grant`. Treat API use as billable unless the account explicitly shows no-cost credits.
3. **Free-tier data terms differ materially.** Google's unpaid Gemini services may use prompts and responses to improve products and permit human review; do not send personal/confidential farm data. Google's paid service terms say prompts/responses are not used to improve products but are logged for a limited safety period. OpenAI's API content is not used to train by default, while abuse-monitoring logs may retain content up to 30 days. Anthropic ZDR is an organization-level arrangement requiring approval; it is not an automatic property of using the API.
4. **No production cost forecast is possible from the plan as written.** For scale illustration only, 1,000 turns at 3,000 input and 500 output tokens each would cost about `$0.55` on GPT-6 Luna or Claude Haiku 5.5, and about `$11` on GPT-6 Sol or Claude Sonnet 5.5 at the reviewed standard per-token prices. This excludes embedding calls, retries, caching, tools, long-context pricing, tax, and provider price/availability changes. Set a token ceiling and hard billing cap; forecast from observed pilot usage.
5. **The architecture introduces more moving pieces than the first release needs:** three provider adapters, embeddings, hybrid search, a reranker, pgvector, provider-response caching, OpenTelemetry, and a model/provider selection layer. Each adds integration, privacy, migration, or cost work. Keep the adapter interface, but implement one provider only for a public-data pilot. Do not deploy automatic provider routing or a second adapter without a demonstrated availability or quality need.
6. **Citation-ID validation is not claim verification.** The server must attach citations from retrieved source records; the model must not author URLs, publisher metadata, or passage IDs. A citation existing in context does not show that it supports the claim. Require claim-to-passage support tests and expert review for agronomic statements; deterministic facts should be returned directly by services wherever practical.
7. **Reranking needs a measurable justification.** A second LLM/cross-encoder adds latency, token/compute cost, and another potential data transfer. Start with metadata filters plus lexical/vector retrieval; add a reranker only if a fixed bilingual retrieval set shows a material improvement over a simpler ranked/fused baseline.
8. **Embedding choice and dimensions must follow a retrieval test.** `gemini-embedding-2` is officially described as multilingual (over 100 languages), but that is not evidence of recall for Malayalam crop names, transliteration, or Kerala agronomy. The current docs specify task-prefix formatting for embedding-2; keep query/document formatting consistent. Compare it with a lexical baseline and another candidate on reviewed queries before migration. Embedding privacy, billing, model-version pinning, and re-embedding cost need their own entries.
9. **Prompt-injection defenses are good but cannot guarantee safe answers.** The strongest control is to give the initial assistant no tools that can write, fetch arbitrary URLs, or execute code. Retrieved-text delimiters and “ignore instructions” prompts are not security boundaries. Test malicious content in PDFs/OCR and measure unsupported claims and unauthorized action attempts; never let retrieved content expand permissions.
10. **Malayalam evaluation coverage is not yet operationally defined.** No source or gold answer currently covers all 14 districts × 31 crops. Build the first set from the small set of approved facts and a large explicit must-abstain set; do not generate “gold” agronomy from the model. Track dialect/transliteration and unit/date cases separately.
11. **Do not assume PostgreSQL's default English text-search configuration is a Malayalam analyzer.** Test native-script terms, transliterations, scientific names, and curated aliases; keep the exact-match/metadata baseline explicit. Add a language-aware tokenizer or embedding model only if the evaluation shows the baseline misses supported evidence.
12. **Check end-user age and geography against provider terms.** Google's Gemini API terms require API users to be at least 18 and prohibit API clients directed to or likely to be accessed by under-18s. If AgroSense-360 is intended for student/minor users, that is a provider-selection blocker, not just a prompt/privacy issue.

### Recommended initial LLM architecture

For a bounded, non-confidential prototype after source approval:

1. Keep FastAPI as the only model gateway. Use one provider adapter, one pinned model, strict token/time limits, and no silent cross-provider failover.
2. Start from a small, curated, rights-cleared set of source records. Return deterministic source facts and citation metadata directly when possible.
3. Begin retrieval with metadata filters and an inexpensive lexical baseline. Evaluate bilingual dense embeddings offline; add pgvector only after a retrieval benchmark and migration review. Add reranking only if it improves the measured set.
4. Use Pydantic structured output, then validate every evidence ID server-side and bind citations to exact source passages, versions, and page/section offsets. Reject unsupported claim types or abstain.
5. For a paid-provider pilot, benchmark a quality-oriented candidate such as Claude Sonnet 5.5 against GPT-6 Sol on the same public/synthetic set; select one passing candidate rather than integrating all vendors. No relative quality winner is established by the documents or this review. Revalidate exact model availability, country eligibility, terms, and prices immediately before selection.
6. Keep user/farm data out of provider prompts during the pilot. For later production use, approve a data-processing/retention posture, purpose limitation, deletion policy, and spend cap first.

This is a pilot recommendation, not authorization to create a provider account, submit user data, or implement an API integration.

## C. ML architecture review

### Training readiness and target definitions

The documents correctly state that appropriate labels are missing and do not invent accuracy figures. **No training pipeline is ready.** The two audited ERA5-Land archives are not usable training histories; weather cannot substitute for crop-outcome ground truth.

The crop recommendation pipeline must split into distinct estimands before any feature design:

- **Agronomic suitability/ranking:** label with an explicitly defined, expert-reviewed suitability assessment for crop × location × season (including “unknown” and scope of management assumptions). A crop profile or recommendation rule is not automatically a label.
- **Yield/production prediction:** label with observed yield (or production plus harvested area), crop/variety, season, management, and measurement provenance. Yield is an outcome under actual management and is not equivalent to intrinsic suitability. Do not combine suitability classes and yield values into one target or report their metrics together.

The soil, disease, weather, and event-risk pipelines also need separate target definitions and source/license decisions. The current inventory's conditional/blocked datasets do not become trainable because their downloads are public. SoilGrids estimates are covariates/context, not laboratory ground truth. Disease-image rights, image-level provenance, expert labels, and a Kerala field test remain mandatory.

### Corrections and requirements before model work

- Freeze an estimand, label rubric, decision time, population, unit of analysis, and intended user action before collecting data. Record label provenance, measurement uncertainty, consent, and license for each row/image.
- Use group splits by farm/plot/plant and season, then spatially blocked and temporally later evaluation. With only 14 districts, a district holdout can have high variance; report per-district sample counts and uncertainty. Use spatial buffers where nearby cells or neighboring farms can leak correlated signals.
- Keep an untouched final test set. Any tuning, imputation, scaling, feature selection, resampling, and probability calibration must be fit only on training/validation folds. Use nested/grouped validation where the sample size permits; if it does not, state that evidence is insufficient rather than inventing confidence.
- Compare to a cited, expert-approved rules baseline only after those rules are licensed and reviewed. Historical crop prevalence is not a suitability baseline. A deterministic climate summary is not a predictive model.
- Select metrics by task and class imbalance. Report subgroup support, confidence intervals, calibration, and abstention/coverage, not a single accuracy. Calibration is not meaningful with too few representative validation examples.
- Treat SHAP/permutation output as model association, not causal evidence or a fertilizer prescription. Explain the input data freshness and missingness to users.
- Add post-release monitoring before deployment: schema/unit failures, input and label drift, district/crop coverage, calibration and delayed outcomes, abstention rates, and a human-reviewed retraining trigger. Never automatically retrain/promote on drift alone; require new data/license checks and approval.
- Preserve reproducibility with source/resource/version, license decision, immutable snapshot hash, transform/config hash, split manifest, code revision, dependency lock, seed, model artifact hash, and signed evaluation report.

### Model and infrastructure choices

The proposed simple baselines (rules, regularized/GAM models, then CPU tree models) are proportionate. Do not deploy CatBoost/XGBoost, MLflow, DVC, object storage, or a cloud GPU merely because they appear in the roadmap. Start with reproducible scripts, immutable local snapshots/backups, manifests/checksums, and the project's existing database/API. Add managed storage or registries when team, audit, access-control, or artifact-volume needs justify their recurring cost.

Use CPU-first tabular experiments on the Ryzen laptop after labels exist. Small, monthly, spatially clipped weather arrays are suitable for chunked local QA; do not load global hourly grids or entire archives into RAM. A cloud GPU is justified only for a rights-cleared image task whose measured training workload cannot be handled locally and whose data-transfer/retention costs are approved. No NVIDIA CUDA is available by assumption.

## D. Hardware and deployment review

The 8 GB Ryzen 3 7320U laptop with integrated AMD graphics is adequate for code development, small tabular baselines, monthly weather QA, and API work. It is not a reason to provision cloud compute for the planned bounded weather pilot. Keep a working disk margin: 352 GB free was a point-in-time measurement, not a guarantee.

The target architecture currently implies several possible paid services (hosting, Supabase compute/storage, object storage and egress, embedding/model APIs, MLOps registry, observability, and optional GPU). The roadmap should classify each as **required for pilot / later optional / not justified**, rather than implying all are part of production.

Recommended deployment posture:

- Continue local Windows/CPU development and existing project services; no Kubernetes, dedicated vector database, GPU VM, or second cloud provider for the first pilot.
- Keep raw data out of Git and preserve source archives; use checksummed local storage plus an authorized backup only after licensing and privacy review.
- For a future public demo, use the existing backend hosting pattern and a small CPU inference process if a validated tabular model ever exists. Keep LLM calls server-side. Do not expose source/private data through the frontend.
- Add pgvector to the existing PostgreSQL only after a measured retrieval need and migration approval. It is not a reason to add another database.
- Define actual SLOs, traffic, budget, backup/restore and retention before selecting paid production tiers. The current roadmap has appropriate gates but no costed deployment profile.

## Decisions

### Accepted as sound direction (not execution approval)

- Preserve the current ERA5-Land ZIPs and audit records; reject them for training.
- Keep dataset license and governance checks fail-closed.
- Do not train any model until task-specific, rights-cleared labels exist.
- Keep LLM answers evidence-bound, source-cited, uncertainty-aware, and able to abstain.
- Use CPU-first, chunked local work for the weather pilot; use cloud compute only when measured need and rights justify it.
- Require a pilot and explicit approval before full acquisition or public inference.

### Corrections required in plans before approval

1. Change “481 requests” from implied necessity to a count for the selected monthly mixed-product design; add the hourly-only alternative and its storage trade-off.
2. Make the pilot cross-check daily product output against hourly temperature/dewpoint/wind, and test precipitation/radiation step semantics across a month boundary.
3. Replace the unsubstantiated 5 GB reserve with pilot-measured output, temporary, and extracted sizes plus a documented safety margin.
4. Separate crop suitability and yield prediction into different targets, labels, and evaluation reports.
5. Clarify that citations must be bound and support-checked by the server, not merely present in a Pydantic payload.
6. Replace “Free tier” shorthand with the exact billing interpretation and provider-specific data-retention terms; price an actual token-budget scenario.
7. Make DVC, MLflow, object storage, pgvector, reranking, multiple providers, and cloud GPU explicitly optional and gated by measured needs.
8. Add land-sea-mask-aware missingness, observed-vs-derived feature units, and post-deployment drift/calibration monitoring criteria.

### Decisions requiring user approval

- Public portfolio/demo only versus commercial scope, including source terms and attribution.
- Licensed Kerala district boundary/version, spatial coverage rule, and minimum acceptable land-cell coverage per district.
- UTC-day product acceptance versus a separately engineered IST-day aggregation.
- Mixed daily/hourly versus all-hourly acquisition architecture and corresponding storage plan.
- Exact weather pilot month, acceptance tolerances, and whether to proceed after the pilot.
- Crop suitability rubric and independent yield target; owners and process for collecting labels.
- Provider, model, data-processing/retention posture, monthly hard cap, and user-data policy.
- Whether a future vector-index migration or paid cloud storage is justified.

## Recommended implementation order

1. Approve scope, dataset terms/attribution, label governance, and licensed boundary source. Do not submit requests yet.
2. Lock the pilot schema and expected outputs using the live process definitions; prepare a client-side request ledger without credentials in source or logs.
3. After separate acquisition approval, run one complete one-month pilot for both products, including hourly reference variables, a next-month 00 UTC record, daily-vs-hourly checks, district coverage, missingness classification, and actual disk/RAM measurement.
4. Review the pilot and choose the full-acquisition architecture. Recalculate storage and resume behavior from actual files. Separately test the 2024/2025 boundary before final historical production.
5. Build only the approved reproducible ingestion/quality workflow. Keep raw originals immutable and keep derivatives clearly separated.
6. In parallel, prepare a small rights-cleared LLM evaluation set with must-abstain cases. Select one model/provider from a paid, non-sensitive benchmark; start with simple retrieval and add vector/reranking only if measured.
7. Define and collect one task's labels before any ML training. Begin with a rules/statistical baseline, leakage-safe split, and independent review.
8. Integrate only passing data/model/LLM services behind explicit feature gates. Add monitoring, budget limits, rollback, and public-facing uncertainty before any release.

## Sources checked

- CDS live [daily-statistics process definition](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics) and [hourly process definition](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land).
- CDS [daily-statistics catalogue](https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics) and [hourly catalogue](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- ECMWF [ERA5-Land data documentation](https://confluence.ecmwf.int/spaces/CKB/pages/140385202/ERA5-Land+data+documentation), including CDS validity-time mapping, land mask, forecast steps, accumulations, and updates.
- CDS [API setup and use guide](https://cds.climate.copernicus.eu/how-to-api), including dataset Terms of Use and the status of the advanced datastore client.
- OpenAI [pricing](https://developers.openai.com/api/docs/pricing), [rate limits/usage tiers](https://developers.openai.com/api/docs/guides/rate-limits), and [API data controls](https://developers.openai.com/api/docs/guides/your-data).
- Provider [structured output documentation: OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs), [Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), and [Google](https://aistudio.google.com/docs/structured-output).
- Anthropic [model overview](https://platform.claude.com/docs/en/models/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing), and [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
- Google Gemini [model catalog](https://aistudio.google.com/docs/models), [pricing](https://aistudio.google.com/docs/pricing), [API terms](https://aistudio.google.com/docs/terms), and [embeddings](https://aistudio.google.com/docs/embeddings).
- Supabase [hybrid-search guide](https://supabase.com/docs/guides/ai/hybrid-search) (including its example's English text-search configuration).

This report is an independent planning review only. It does not change or supersede the four Stage 13 plans, approve a dataset request, or authorize implementation, provider use, model training, schema changes, or deployment.
