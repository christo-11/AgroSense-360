# AgroSense-360 Stage 37 — Testing and Validation Plan

**Status:** Test strategy only; no tests were run in this stage.  
**Decision:** Existing application tests cover selected API, governance and frontend evidence states. They do not establish readiness of a weather ingestion pipeline or ML service that is not implemented.

## 1. Existing test setup and limitations

- **Backend:** Python tests live under `backend/tests/` and use `pytest`, `FastAPI TestClient`, SQLAlchemy fixtures and temporary files. `backend/requirements-test.txt` pins pytest/httpx/anyio.
- **Database fixture:** Unless `AGROSENSE_TEST_DATABASE_URL` is explicitly supplied, `conftest.py` uses in-memory SQLite and registers simplified spatial-function stubs. This does not test PostgreSQL query behavior, PostGIS geometry correctness, migrations, production networking, or database availability.
- **Optional PostGIS integration:** With a separately approved non-production `AGROSENSE_TEST_DATABASE_URL`, the fixture checks PostGIS availability and requires Alembic revision `5d3cbf283629`; it creates and removes test records. Do not point it at production or a personal data store.
- **Frontend:** `package.json` provides `npm test` (Vitest), `npm run build` (TypeScript project build plus Vite), and `npm run preview`. `vitest.config.ts` uses jsdom and includes `src/**/*.test.{ts,tsx}`.
- **Current test coverage includes:** API health/authentication, farm/plot ownership and boundaries, catalogue access, data-intelligence metadata reconciliation, quality/training eligibility separation, provenance checks, source-governance fail-closed behavior, black-pepper contract validation, and Data Intelligence Dashboard states.
- **Recorded result:** `AGROSENSE_TEST_RESULTS.md` records 33 backend tests passing and frontend type-check/build passing on 2026-11-20 under its stated environment. It is historical evidence, not a result of Stage 37 or a claim that the current tree has been retested. The report notes no live PostGIS/database or live API validation.

Do not treat fixture stubs, mocked provider responses, source metadata, or passing contract tests as proof of real-world source quality, permission, forecast accuracy, agricultural validity, or deployment behavior.

## 2. Validation principles

1. Define the requirement, supported use, geography, time period, denominator and pass/fail criteria before running a test.
2. Keep technical integrity, data quality, legal/source permission, project-owner authorization, model performance and production readiness as independent gates.
3. Use deterministic synthetic fixtures and pinned versions for routine tests; never require external provider calls or real credentials in unit/CI tests.
4. Preserve source evidence and original values. A test failure must be visible and attributable; do not silently skip required checks or convert failure into empty success.
5. Test no-data, missing, stale, malformed, conflict, unauthorized and partial outcomes—not only nominal success.
6. Avoid private farm geometry, credentials and real correspondence in test fixtures, logs and artifacts. Do not inspect `.env` or `.cdsapirc`.
7. Record the exact commit/revision, dependency set, command, environment, test selection, result and known skips for release evidence.

## 3. Test layers

### 3.1 Unit tests

Add focused tests when each future component is implemented:

- Provider request construction and response parsing against pinned, sanitized fixtures; product/version/schema mismatch and unsupported variables fail closed.
- Canonical variable mapping, conversion formulas, accumulation/rate semantics, fill values and missingness preservation; unknown units are rejected.
- UTC timestamp parsing, interval/cadence validation, DST/local-day conversion to `Asia/Kolkata`, leap days and forecast issue/valid/lead relationships.
- Spatial reference, axis order, coordinate bounds, grid spacing, versioned district overlay and coverage denominator; no plot-level precision inferred from grid data.
- Archive/member checksum, container CRC and format-specific message boundary checks as separate assertions.
- Idempotency, deterministic feature formulas, rolling windows, imputation masks, and explicit error-category/retry policy.
- Permission decision combinations, signed reviewer policy and transitions: quality success cannot grant acquisition, research, commercial, redistribution or ML permission.

### 3.2 Integration tests

Use isolated disposable services and synthetic/sample data only:

- Database/object-store/queue handoffs, transactions, immutable raw artifacts, release pointer updates, retry idempotency, quarantine and audit events.
- PostgreSQL/PostGIS schema and query behavior, geometry validation, spatial indexes, migration upgrade/downgrade and rollback on a non-production disposable database.
- Governance, source release, artifact checksum, quality report and feature/model lineage joined end-to-end. Reject missing or conflicting approvals before reading protected training inputs.
- Worker restart, partial chunk recovery, duplicate submission, bounded retry, timeout and dead-letter/quarantine behavior.
- No live provider/API endpoint should be required for ordinary CI. Any separately approved provider acceptance test must be manual/isolated and use an explicitly authorized test resource.

### 3.3 API and contract tests

- Validate FastAPI OpenAPI and versioned frontend/backend response schemas for successful, partial, unavailable, stale, quality-rejected and permission-blocked states.
- Exercise input validation, UTC/date bounds, pagination, request-size limits, timeouts, authentication, authorization, CORS and documented error envelopes.
- Test that private farm/plot data is only visible to the owning authenticated user; test object-level authorization on every new plot-scoped route.
- Verify public catalogue/status responses omit local filesystem paths, credentials, personal geometry and restricted correspondence.
- Ensure 503/unavailable is explicit when weather/model services are absent; prohibit zero-filled or fabricated successful insight payloads.
- Keep contract tests deterministic and backward-compatible; intentional breaking changes require a versioned API transition and frontend coordination.

### 3.4 Data-quality tests

Apply the Stage 32 framework to exact source release and intended geography/use. Test:

- Expected versus observed completeness, missing values/sentinels, duplicates/conflicting natural keys, timestamp continuity and longest gaps.
- Spatial coverage by district/cell/station with CRS, boundary/version, valid-area denominator and native support.
- Unit/type/schema compatibility, physical/range checks, outlier review flags, provenance/version pinning and request/receipt consistency.
- ZIP/archive integrity separately from internal GRIB/NetCDF/file validity; parser success must not override a raw-format conformance warning.
- Source estimate versus independent authorized observation validation, with sample count, station/gauge independence, temporal match, distance/elevation context, bias and uncertainty reported.

Thresholds must be approved for the exact variable, period, region and use. Existing Stage 32/weather-spec thresholds are provisional. Global missingness cannot be reported as a Kerala-specific rate without a Kerala-scoped denominator. No present archive should be retested or upgraded to approved use merely by adopting this plan.

### 3.5 Security tests

- Authentication/session expiry, password/JWT handling, authorization bypass, object ownership, role separation, CSRF/CORS policy and administrative review/signature tampering.
- Input/schema validation, SQL injection defenses through parameterized ORM queries, path traversal/archive extraction, decompression limits, malicious file upload and unsafe parser behavior.
- Secret scanning and log-redaction checks using synthetic canary values; ensure tokens, farm coordinates, source payloads and private correspondence do not leak.
- Dependency and container vulnerability review, secure headers/TLS configuration, least-privilege storage/service identities, audit-log integrity and rate limiting.
- Threat model and abuse cases for ingestion workers, public APIs, admin review path, dataset registry and model inference before external deployment.

Use authorized test environments and non-sensitive fixtures. This plan does not authorize penetration testing against external systems or providers.

### 3.6 ML validation

Blocked until a specific task has valid labels, approved source releases, explicit ML permission and signed governance clearance.

Before any future training/evaluation:

- Freeze the target definition, unit of analysis, label source, time horizon and intended inference population; verify label provenance, measurement/annotation quality and class balance.
- Freeze feature/source versions and decision-time availability. Exclude post-outcome or revised information unavailable at prediction time.
- Pre-register temporal and spatial/group holdouts; prevent records from the same farm/site/station, overlapping time windows, image session or derived target aggregate crossing splits.
- Keep transformations, imputation, scaling, feature selection and calibration inside training folds; retain a locked untouched test set.
- Compare with simple appropriate baselines; report uncertainty, calibration, per-district/season/cultivar subgroup performance, missing-input behavior and abstention.
- Evaluate external/geographic generalization and drift only with independently authorized labels; record sample counts and uncertainty. No metric is currently available.
- Require reproducible run metadata, code/dependency environment, dataset/feature/label checksums, model artifact checksum, reviewer sign-off and intended-use decision.

Weather reanalysis or satellite estimates are predictors, not direct weather ground truth or black-pepper outcome labels. The Stage 35 assessment remains **NOT READY FOR MODEL TRAINING OR DEPLOYMENT**.

### 3.7 Performance and resilience tests

- Establish service-level targets first; measure API latency/throughput, large-query behavior, pagination, geospatial query plans, ingestion throughput and model inference latency under representative synthetic loads.
- Test bounded concurrency/rate limiting, backpressure, queue saturation, large archives, memory/disk limits, timeouts, circuit breakers, transient provider errors and database/storage outages.
- Verify no stale or alternate data is served as current; check cache keys include source/release/permission context and that revocation invalidates access.
- Load and soak testing must use synthetic data and non-production infrastructure. No production farm data or external providers are required.

### 3.8 Regression and frontend tests

- Run backend unit/API/governance suites and frontend Vitest tests on changes to their respective contracts; run TypeScript/Vite production build before release.
- Add component tests for loading, retry, partial endpoint failure, inaccessible data, quality warnings, provenance/attribution display and explicit no-prediction states.
- Add end-to-end browser tests against a local seeded test stack for sign-in, ownership boundaries, catalogue navigation, data-intelligence evidence, unavailable weather/model states and responsive/accessibility behavior.
- Keep visual snapshots limited to stable components; assert user-visible behavior and accessibility roles rather than fragile implementation details.
- Repeat all critical permission and no-fabricated-data regression tests after source inventory, schema, API or model-gate changes.

## 4. CI and release gates

**Pull request checks (no provider or database secrets):**

1. Formatting/lint/type checks configured by the repository.
2. Backend unit/API/governance/contract tests using isolated SQLite and temporary paths.
3. Frontend Vitest, TypeScript build and Vite production build.
4. Static secret/dependency checks, schema/openapi consistency and migration graph checks.
5. Test report with exact command, passed/failed/skipped counts and coverage context.

**Separately approved pre-release checks:**

1. Disposable PostgreSQL/PostGIS integration and migration/rollback tests.
2. Full ingestion/quality contract tests on authorized synthetic or approved fixtures.
3. Security review, threat-model closure, load/resilience and restore tests.
4. For an ML service only: data rights and label gates, leakage-safe evaluation, locked holdout, review and model-risk acceptance.
5. Operations sign-off for alerts, runbooks, retention, access, backup/recovery and rollback.

No single green suite grants source permission, approves an archive, authorizes model training, or establishes production readiness.

## 5. Current gaps and decision

- Weather adapters, canonical observations, feature pipelines, weather-serving APIs and validated models are not implemented or tested end to end.
- No verified black-pepper target labels, representative Idukki evidence, class balance, or model metrics exist.
- No source is currently approved for ML training; Stage 23 authorization and source-owner permission boundaries remain unchanged.
- Request 1 remains **ACCEPTABLE WITH LIMITATIONS**; request 2 remains **REJECTED** pending GRIB1 clarification. Neither is authorized for production, decision support or training.
- Stage 14's recorded test results are historical; this strategy itself was not test-executed and makes no claim that repository tests pass today.

**Stage 37 decision:** This plan is a future validation checklist, not evidence that the planned pipeline or model passes any check. Implementation and test execution require their own approved stage and exact, authorized scope.
