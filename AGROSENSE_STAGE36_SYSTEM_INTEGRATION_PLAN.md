# AgroSense-360 Stage 36 — System Integration Plan

**Status:** Planning only; implementation requires separate project-owner and technical approval.  
**Decision:** The system is **not ready for end-to-end agricultural weather or ML integration**. Existing data, permission, and model gates remain in force.

## 1. Purpose and boundaries

This plan describes how the existing React frontend, FastAPI backend, relational database, proposed weather pipeline, future feature computation and future ML services could integrate. It does not implement routes, acquire data, change database schemas, call providers, generate features, train models, or authorize any use.

Current Stage 23 authorization and source-owner permission statuses remain unchanged. ERA5-Land request 1 remains **ACCEPTABLE WITH LIMITATIONS** and request 2 remains **REJECTED** under Stage 28. Neither is approved for production, agricultural decision support, or training. Idukki remains provisional.

## 2. Current system and component responsibilities

| Component | Current observed responsibility | Planned integration responsibility |
|---|---|---|
| React + TypeScript frontend (`src/`) | Presents the catalogue, farm/plot workspace and read-only data-intelligence dashboard. Uses a shared API client and typed responses. | Render explicit quality, freshness, evidence type and unavailable/blocked states; never calculate agronomic recommendations from unverified values. |
| Shared frontend API client (`src/api.ts`) | Uses `VITE_API_URL` (default `http://localhost:8000`), attaches a session token when present, parses JSON and raises `ApiError` for non-success responses. | Add typed methods only alongside an approved and versioned backend contract; handle timeouts/cancellation, stale data and authorization errors explicitly. |
| FastAPI backend (`backend/app/main.py`) | Exposes health/status, authentication, user-owned farm/plot CRUD, catalogue routers, and unavailable insight routes. Weather insight currently returns HTTP 503. | Remain the authorization and contract boundary; expose only released, provenance-bearing data after applicable approval gates pass. |
| Data-intelligence router | Reads and validates source inventory, acquisition manifest, quality metadata and catalogue records. Read-only endpoints report provenance and training eligibility; the eligibility endpoint explicitly does not grant training clearance. | Continue reporting evidence/status separately from serving measurements or granting use permission. |
| SQLAlchemy/PostGIS database | Persists users, farms/plots, crop catalogue and related associations. Farm/plot routes require the current-user dependency and enforce ownership. | If separately approved, store normalized records and versioned lineage; keep source artifacts outside relational rows and do not create an alternate approval truth. |
| Weather source adapters and raw landing | Proposed only by Stage 31; no provider adapter is currently approved or wired. | Fetch only after source-specific owner authorization, preserve immutable source payloads and request/release evidence, and stop on permission, integrity or quality failures. |
| Quality and normalization pipeline | Design in Stage 32; no new Stage 36 implementation. | Validate source schema, units, time, spatial coverage, completeness and provenance before release; quarantine failures. |
| Feature service | Candidate definitions documented in Stage 33 only. | Compute reproducible, versioned weather/agricultural features from approved inputs; preserve missingness and input lineage. |
| ML/inference service | No validated crop/weather model is deployed; insight routes return 503 and image analysis is unavailable. | Consume only separately approved datasets/features/models; maintain model and label lineage, validation, monitoring and rollback. |
| Operations and audit | Health/status routes exist; no complete production monitoring or ingestion audit service is evidenced. | Correlate requests and pipeline runs with non-sensitive IDs; alert operators without exposing secrets or farm data. |

## 3. Target data flow

```text
Project-owner authorization + source-owner terms/permission
        |
        v
Versioned source/release registry and approved request specification
        |
        v
Authorized provider adapter --> immutable raw artifact + request evidence
        |
        v
Integrity/parser/schema checks --> normalization --> quality evaluation
        | failure                                  | pass (reviewable release)
        v                                          v
Quarantine + explicit audit status       Versioned observation release
                                                   |
                                    approved feature definition/run
                                                   |
                                 optional validated model/inference
                                                   |
                         authorized FastAPI read contract --> React UI
```

Each derived object must retain links to exact source release and artifact checksums, parser/normalization version, quality run, intended-purpose decision and (for features/models) formula, code, label and split versions. A technical quality pass cannot grant legal permission or project-owner authorization. No layer may silently replace one provider/product with another.

## 4. API contract plan

### Existing contract

- `/health` reports API process status; `/health/database` reports database availability.
- `/api/v1/status` reports API/database state and integration/model readiness.
- `/api/v1/data-intelligence/*` exposes read-only source, acquisition, quality, provenance, catalogue and eligibility evidence. Several list endpoints use bounded `limit`/`offset`; the training response explicitly says it does not grant clearance.
- `/api/v1/districts`, `/api/v1/crop-categories`, `/api/v1/crops`, crop profile/variety, and district-crop endpoints expose catalogue records.
- `/api/v1/farms*` requires a current user and enforces ownership; farm/plot create/update/delete endpoints mutate user-owned records.
- `/api/v1/insights/{insight_type}` currently returns 503 for supported insights because verified data/model services are not deployed. `/api/v1/crop-health/analyze` similarly returns 503 after validating upload media type.

These are observations of existing behavior, not an endorsement of current source-use statuses or a guarantee of production compatibility.

### Future weather and feature read contract (proposed, not implemented)

Before any endpoint is designed in code, approve a versioned OpenAPI contract and intended consumer. A possible read-only contract should define:

- Resource and query scope (authorized district/site or authenticated owner-scoped plot), variable IDs, and a bounded time range.
- Response values with canonical unit, interval start/end in UTC, source evidence type (`MEASURED`, `REANALYSIS_ESTIMATE`, `SATELLITE_ESTIMATE`, `FORECAST`, or `DERIVED`), native spatial support/resolution and quality flags.
- Dataset/release ID, product version, retrieval/issue time as applicable, quality-run reference, lineage/provenance reference and attribution.
- Explicit `AVAILABLE`, `PARTIAL`, `STALE`, `UNAVAILABLE`, `QUALITY_REJECTED`, or `PERMISSION_BLOCKED` outcome; missing values are not zero and no fallback is silent.
- Pagination or bounded response windows for large time series, stable schemas, UTC semantics and a documented error envelope.
- Forecast issue time and valid interval, so clients can distinguish forecasts from observations/reanalysis and prevent future-information leakage.

Do not expose a plot-level value from a coarse grid as a farm measurement. Do not expose private farm geometry or locations through public catalogue/status endpoints. Any user-specific weather response must require authentication, ownership checks and a separately approved purpose.

## 5. Component handoffs and data contracts

1. **Governance to ingestion:** resolve exact source, release/version, terms, attribution, approved purpose, project-owner decision and any written source-owner permission. Default missing evidence to blocked.
2. **Adapter to raw landing:** persist request specification, provider/task reference, retrieval time, original metadata and per-artifact checksum. Do not log request secrets or payloads.
3. **Parser to canonical model:** preserve original value/unit/time/coordinates; map only verified parameter semantics. Reject unknown versions, units, calendars, or coordinates.
4. **Quality to release:** produce immutable check suite/version, thresholds, metrics, partitions and warnings. Separate source integrity from message validity, and estimates from direct measurements.
5. **Release to feature computation:** require a specific feature definition, input release IDs, time windows, spatial mapping/boundary version and approved transform/imputation policy.
6. **Features to ML:** require valid authorized labels, sample review, leakage-safe splits, source training permission and signed governance clearance; otherwise no run is allowed.
7. **Backend to frontend:** return typed, bounded responses with provenance and quality state. The UI displays unavailable/partial states and limitations without converting them into predictions.
8. **Operations to governance:** retain auditable approval, request, receipt, validation, quarantine, release, access and revocation events with reviewer identity and evidence reference.

## 6. Security and privacy

- Preserve least privilege and existing current-user/ownership checks for farm and plot resources. Any new private-data endpoint must enforce the same ownership boundary.
- Keep secrets outside source control, metadata files, logs, browser bundles and API responses. No credentials were accessed or introduced for this plan.
- Apply authentication/authorization per operation, server-side input validation, bounded date/geography/pagination parameters, upload limits, rate limits and CSRF/CORS controls appropriate to the deployment model.
- Minimize precise farm geometry and personal information in telemetry. Avoid including coordinates, tokens, raw provider payloads, or correspondence in routine logs.
- Use TLS in deployment, protected secret management, encrypted backups/object storage, scoped service identities and retention/access policies compatible with source terms and privacy obligations.
- Do not let a frontend flag, public status endpoint, or client-supplied source ID bypass the server-side signed governance gate.
- Threat-model provider payload parsing, archive extraction, image upload, dependency supply chain and administrative approval actions before implementation.

## 7. Error handling and consistency

- Use stable error categories and HTTP status mapping: invalid request (4xx), unauthenticated/forbidden (401/403), not found (404), rate limited (429), and unavailable/quality/permission blocked (503 or a documented domain status where appropriate).
- Preserve the existing explicit unavailable behavior until verified services exist. Do not respond with fabricated zeros, cached success-shaped data, demo predictions, or a silent alternate dataset.
- Distinguish retryable transport/time-limit errors from non-retryable authorization, licence, checksum, schema and quality errors. Apply bounded backoff only to retryable provider failures, and use idempotent request IDs.
- Make ingestion stages resumable and idempotent; use a transactional release pointer only after all required validation and approval checks pass.
- Keep original artifacts and failed-run diagnostics for review under approved retention. Report sanitized, actionable errors to UI and operators; keep detailed stack traces and sensitive metadata server-side.
- Revoke or quarantine a release if its terms, source version, integrity or permission state changes; invalidate dependent features/models through explicit lineage rather than silently mutating them.

## 8. Monitoring and audit

Track service availability/latency, request/error rates, database readiness, provider job duration/failure, chunk retries, source freshness, missing periods, archive/member integrity, parser errors, quality failures, queue depth, feature-run completeness and model inference health. Alert on stale/unavailable data and authorization/quality gate failures.

Every event should include UTC timestamp, correlation/request ID, actor or service identity, action, resource/release/run IDs, outcome, error category and evidence reference. Audit approval and permission changes append-only. Logs must not contain credentials, full request secrets, personal details, exact farm geometry or unbounded provider content.

Health endpoints should distinguish process liveness from dependency readiness; a running API must not imply that weather data or a model is available. Model monitoring, once relevant, should include input drift, missingness, out-of-distribution rates, calibrated performance against newly verified labels, subgroup/geographic performance and safe abstention. No monitoring service is claimed to exist beyond current health/status routes.

## 9. Scalability and resilience

- Partition historical acquisition by provider-supported time/geographic chunks; apply bounded concurrency and rate limits.
- Use a queue/worker architecture only when justified by workload; separate acquisition, parsing, quality, feature and inference resource pools.
- Store immutable large raw data in access-controlled object storage; use relational storage for indexed metadata, permissions, status and lineage.
- Use spatial indexes for PostGIS queries and versioned boundary sets for regional aggregations. Do not overstate grid resolution or precision.
- Support pagination, caching only for approved public metadata or versioned immutable releases, explicit freshness, and invalidation on source/permission changes.
- Add timeouts, circuit breakers, bounded retries, backpressure and operator-visible dead-letter/quarantine queues. Never fall back to an unapproved provider.
- Define recovery point/time objectives, backups, restore tests, retention and deletion behavior before production; no targets are specified by this planning document.

## 10. Testing and release strategy

Build validation in layers after implementation is separately approved:

1. Unit tests for provider adapters, parser/schema, units, UTC intervals, spatial mapping, missingness, authorization decisions and domain error mapping.
2. Contract tests against pinned OpenAPI schemas and representative, non-sensitive fixtures; provider mocks must not be mistaken for real validation.
3. Integration tests for database, object-store, queue, governance gate, idempotency, quarantine and lineage.
4. API tests for authentication, ownership isolation, validation, pagination, status/error semantics and privacy filtering.
5. Data-quality tests for completeness, continuity, duplicates, coverage, outliers, checksum and version identity.
6. Feature tests for formula reproducibility, window boundaries, missingness propagation and no future-data leakage.
7. ML evaluation tests for label validity, group/time splits, calibration, geographic holdout and locked test discipline before any model approval.
8. Security, load, resilience, migration/rollback and frontend accessibility/regression tests.

Release gates must be independent: legal/use authorization, source quality, technical readiness, model validation, security and operations. A pass in one is not approval in another. Maintain the current 503/unavailable UX until all gates for an exact service and use case are satisfied.

## 11. Implementation prerequisites and decision

Before implementation, obtain explicit project-owner approval for the scope; resolve Stage 23 source inquiry/acquisition/use permissions; decide exact product/version and licensed purpose; close the Stage 28 request 2 technical issue or exclude that archive; define authoritative Kerala/Idukki boundaries and representative observations; approve the Stage 32 scientific thresholds; define canonical schemas, retention, storage, deployment security, operational ownership, API contracts and rollback; and complete design/security review.

**No implementation is authorized by this plan.** Existing route behavior, source inventory, database schema, permission statuses, dataset decisions, ML status and deployment state remain unchanged.
