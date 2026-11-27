# AgroSense-360 LLM Architecture

**Status:** Proposed architecture only. No provider, API key, model or RAG integration has been configured.  
**Research checked:** 2026-11-20.

## Architecture principles

1. The LLM explains and organizes verified evidence; it does not create weather observations, soil measurements, crop suitability facts, disease diagnoses, fertilizer instructions or government-program facts.
2. Deterministic services and validated ML models own numeric outputs. The LLM may summarize these outputs with their source/version and uncertainty, but may not calculate or invent them.
3. Any factual answer must be traceable to approved source records or a clearly labelled, versioned model prediction. If evidence is absent or conflicting, abstain and say what is missing.
4. Provider use is server-side only. No provider key may appear in React/Vite, browser storage, logs, source control or prompts.
5. A provider adapter is not permission to silently route user data to another company. A provider fallback requires an explicit policy and privacy review.

## Proposed request flow

```text
React client
    |
    v
FastAPI auth + per-user rate limit + request validation
    |
    v
AgriAssistant orchestrator
    |-- verified district/crop context (read-only project services)
    |-- hybrid RAG: Postgres full-text + pgvector, filtered by evidence metadata
    |-- deterministic weather/soil/model result services
    |
    v
Provider-neutral LLM interface
    |-- OpenAI adapter
    |-- Anthropic adapter
    |-- Google Gemini adapter
    v
Pydantic response validation -> citation/evidence validator -> safe client response
```

The current README says RAG, inference endpoints and the copilot are not connected, and unavailable insight/copilot routes return 503. Keep those responses unavailable until the data, source rights, evaluation and operational gates below pass.

## Provider-independent integration

Define a narrow Python protocol in the backend boundary, not in application business logic:

- `generate_structured(messages, response_schema, model_config, timeout) -> ProviderResult`
- `embed(texts, embedding_config) -> EmbeddingResult`
- `health()` and provider capability metadata

`ProviderResult` should carry validated payload, provider/model/version, provider request ID, usage counts, latency, finish/refusal status, and safe error category. The service layer owns retries, deadlines, budget checks and fallback policy. Keep provider SDK objects out of domain models. Pin model IDs in server configuration and record model changes as reviewed releases.

### Response contract

Use Pydantic models for both request context and response validation. A proposed answer contract contains:

- `answer` and concise `next_steps`;
- `claims[]`, each with `claim_type` (`verified_source`, `model_prediction`, `user_provided`, or `unknown`), `evidence_ids[]`, `as_of`, and caveat/uncertainty;
- `citations[]` with source ID, publisher, title, version/effective date, URL and relevant passage/record ID;
- `abstained` and an explicit reason when evidence is insufficient;
- `safety_notice` when a plant image or recommendation needs expert field confirmation.

Validation rules beyond JSON Schema must verify that citation IDs exist in the retrieved context, that the claim's evidence type matches source status, and that prediction claims identify the model/version and calibrated uncertainty. A schema-valid response is not proof of factual correctness.

## Retrieval-Augmented Generation

### Ingestion and evidence store

Ingest only exact, reviewed resources whose use and redistribution terms permit the intended operation. The inventory currently leaves KAU structured data, SoilGrids product terms, yield/market records, and disease-image rights unresolved or conditional. Do not bulk-ingest a site because its page is public.

Each source document/record gets immutable metadata:

`source_id`, publisher, canonical URL, resource/version, license and scope, attribution text, retrieval time, effective date, language, district/crop/variety/season tags, evidence class, checksum, extraction pipeline version, and review status.

Use a document-aware chunking strategy that preserves headings, tables, units, footnotes and page/section references. Store source text and chunk provenance separately from embeddings. Do not discard original PDFs or machine-readable publisher files.

### Search and embeddings

Proposed first RAG index: Supabase Postgres with `pgvector` plus PostgreSQL full-text search, combined as hybrid retrieval. Apply hard metadata filters (license status, crop, district, language, source freshness) before ranking; then rerank a small candidate set. Store the embedding provider, model ID/version, dimensions and preprocessing version with every vector. Never compare vectors from different embedding models; a model change requires re-embedding and a separate index/version.

Evaluate multilingual embedding candidates on English and Malayalam agricultural queries before fixing a database vector dimension. Google documents `gemini-embedding-2` for over 100 languages; OpenAI documents `text-embedding-3-small`; neither vendor's published general multilingual support proves Kerala agricultural terminology recall. Keep lexical/BM25 retrieval as a useful fallback for scientific names, units and exact scheme names.

Potential source metadata filters: one of 14 districts, one of 31 crop profiles, crop category, season, source publisher, evidence status, publication date, and license. A missing or `pending` district-crop profile must be presented as unknown, not unsuitable.

## Grounding, prompt-injection defense and safety

- Treat user text, uploaded images, OCR, retrieved PDFs and every source passage as untrusted data, never as system instructions.
- Strip active content from documents; preserve original files separately. Retrieval returns quoted text and source IDs, not executable instructions.
- Do not provide the LLM with arbitrary SQL, shell, CDS, filesystem or write tools. Give narrowly typed read-only functions only; validate every argument against an allowlist and current-user authorization.
- Separate trusted policy/system instructions from retrieved evidence. Delimit evidence, explicitly state it cannot change system rules, and test indirect prompt injections in PDFs and web-sourced material.
- Do not rely on an injection classifier or prompt wording as the only defense. Tool permissions, source allowlists, output validation and server-side authorization are primary controls.
- Numeric weather/soil values, units, freshness and model predictions must come from typed application services. The LLM must not interpolate missing records.
- Require citations for externally verifiable factual claims. Reject/repair uncited claims only within a bounded retry; otherwise abstain.
- Never infer fertilizer dosage or chemical treatment from general text. Require a reviewed, crop/stage-specific source and label/measurement context; otherwise refer to local agricultural experts.
- Disease image outputs are model suggestions, not definitive diagnoses. Require a calibrated threshold, out-of-distribution handling and explicit expert/extension referral.

## Conversation context, privacy and budgets

Default to request-scoped context assembled from the current user question and relevant previous turns only. Keep a bounded token budget; summarize older turns into typed facts with provenance and user confirmation for high-impact details. Do not place raw farm coordinates, personal details, images or private records in provider prompts unless the user-facing purpose and provider agreement have been approved.

Proposed initial retention: do not persist transcripts by default. If product requirements later need saved conversations, require user consent, owner-scoped access, retention/deletion controls, encryption, and exclusion of secrets or unnecessary farm identifiers. Never log full prompts, images, retrieved private records or API keys.

Implement per-user and per-IP request limits, maximum input/output tokens, bounded retrieval size, provider concurrency limits, timeouts, exponential-backoff retries for retryable failures, circuit breakers, and a hard monthly spend cap/alert. Cache only deterministic, non-personal, versioned retrieval results or provider responses whose privacy and freshness policy allows caching. A cache key must include normalized query, district/crop filters, evidence/model version and authorization scope.

## Provider options and trade-offs

Model catalogs and prices change. These are candidates observed on official provider pages on 2026-11-20, not benchmark results or a purchase decision.

| Provider | Candidate options | Structured output / language | Free-tier and data cautions |
|---|---|---|---|
| OpenAI API | GPT-6 Luna for lower-cost routine grounded answers; GPT-6 Sol for more difficult reasoning. Official listed standard input/output prices were $0.10/$0.50 and $2/$10 per million tokens respectively at research time. | Official Responses API structured outputs support JSON Schema and Pydantic helpers. Latest models are described as multilingual, but Malayalam agricultural performance must be tested. | The rate-limits page lists a Free usage tier with a $100/month usage limit in eligible geographies; it is not a guarantee of permanent no-cost credits. API data is not used to train by default unless opted in; abuse-monitoring logs may retain content up to 30 days by default, subject to stated exceptions/controls. |
| Anthropic Claude API | Haiku 5.5 for cost-sensitive routing/classification; Sonnet 5.5 as a stronger answer-generation candidate. Official listed standard input/output prices were $0.10/$0.50 and $2/$10 per million tokens respectively at research time. | Current model overview describes multilingual capabilities; structured JSON output has a Pydantic parsing helper. Test Malayalam, citations and domain terminology. | No dependable free API tier was verified in the official pages reviewed. Data retention terms vary by feature/model; ZDR requires organization approval. Retained data is not used for training without express permission per official policy. |
| Google Gemini API | Gemini 4 Hydrogen/Neon are current model-catalog candidates; select the right cost/capability tier only after evaluation. `gemini-embedding-2` is an embedding candidate for multilingual retrieval. | Official docs support JSON Schema/Pydantic structured output. Embedding 2 documentation describes over 100 languages; test Malayalam crop terms, transliteration and code-switching. | The Developer API advertises free access to limited models/tokens. Unpaid-service content may be used to improve products and reviewed by people; do not submit sensitive, personal or confidential farm data on the free tier. Paid-service terms differ and should be rechecked before launch. |

### Proposed selection policy

1. Use synthetic or public, non-sensitive, license-cleared examples for provider comparisons. Measure citation precision, answer support, abstention, Malayalam quality, latency, errors and total cost.
2. Carry at least two adapters in test environments. Choose one paid production provider and one pinned model only after the benchmark, privacy review, supported-country/region review and budget approval.
3. Route routine questions to a lower-cost model only if quality gates pass; do not make high-impact agronomic claims more confident by choosing a larger model.
4. Do not silently fail over to another provider. If explicitly enabled later, disclose the policy, verify both providers' data terms, and include provider/model in audit logs.
5. Free tiers may be used only for synthetic, non-confidential testing with current terms acknowledged. Production cost planning assumes paid usage and hard caps.

## Fallback behavior

If retrieval has no approved evidence, the provider is unavailable, structured output validation fails, or citation validation fails:

1. Return deterministic verified data with source citations if available.
2. Otherwise return a clear `assistant_temporarily_unavailable` or `insufficient_verified_evidence` response and direct the user to the relevant Kerala Agricultural University/extension contact workflow once that source is approved.
3. Do not fabricate an answer, switch providers invisibly, or reuse stale cached weather/model values as current.

## Observability and evaluation

Record request ID, authenticated user ID in a privacy-safe form, provider/model, prompt-template version, retrieved source IDs, corpus snapshot, output schema version, token counts, latency, cache outcome, retry/error category, abstention and user feedback. Redact prompts and sensitive fields. Export metrics/traces through OpenTelemetry-compatible instrumentation; use dashboards for error rate, p95 latency, spend, token use, retrieval-empty rate, citation failures and abstentions.

Build an approved evaluation set before launch:

- English and Malayalam queries across all 14 districts, 31 crop profiles and four categories, with questions that deliberately have no verified answer.
- Gold source IDs/passages, expected evidence type, must-abstain labels, and expert-reviewed answers; avoid generated or inferred ground truth.
- Adversarial prompt injection in user text and retrieved documents; stale/conflicting sources; unit and date tests; numeric values that must match deterministic services.
- Retrieval metrics: Recall@k, MRR/nDCG and coverage by district/crop/language. Answer metrics: citation precision/recall, support rate, abstention correctness, unit/date correctness, harmful overclaim rate and human expert review.
- Run provider/model comparisons on the same versioned set. LLM-as-judge may help triage but never replaces expert review or deterministic assertions.

## Dependencies and unresolved decisions

- Approval of exact knowledge sources and licenses; KAU and several project sources remain conditional or unverified.
- Malayalam evaluation and translations for crop, disease, soil and scheme terminology.
- Privacy, retention, user consent, provider region, data processing agreement and production budget.
- Whether a licensed district boundary and current/corrected weather data can be ingested; the existing ERA5-Land archives remain rejected for training.
- A future approved migration to enable `pgvector` and add retrieval metadata/indexes. No schema change is proposed or made in this planning stage.
- The project has no validated model artifacts and no current inference integration; RAG must not imply that ML predictions already exist.

## Official references (checked 2026-11-20)

- OpenAI [models](https://developers.openai.com/api/docs/models), [pricing](https://developers.openai.com/api/docs/pricing), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [embeddings](https://developers.openai.com/api/docs/guides/embeddings), [data controls](https://developers.openai.com/api/docs/guides/your-data), and [rate limits](https://developers.openai.com/api/docs/guides/rate-limits).
- Anthropic [models](https://platform.claude.com/docs/en/models/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing), [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), and [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
- Google [Gemini models](https://aistudio.google.com/docs/models), [pricing](https://aistudio.google.com/docs/pricing), [structured outputs](https://aistudio.google.com/docs/structured-output), [embeddings](https://aistudio.google.com/docs/embeddings), and [API terms/data use](https://aistudio.google.com/docs/terms).
- Supabase [vector columns](https://supabase.com/docs/guides/ai/vector-columns) and [hybrid search](https://supabase.com/docs/guides/ai/hybrid-search).
- Project state: [README](./README.md), [inventory](./DATASET_INVENTORY.md), [licensing strategy](./DATASET_LICENSING_STRATEGY.md), [local development guide](./LOCAL_DEVELOPMENT_GUIDE.md).
