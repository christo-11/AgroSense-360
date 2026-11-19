# Future Product Roadmap

## Product intent

AgroSense-360 is currently a portfolio project with a possible future commercial direction. It is not launched, not production-ready, and must not collect public farmer data until security, legal, operational, and product requirements are approved.

## Verified current state

- **Stage 6A:** additive Kerala agricultural catalogue and public read APIs exist. Seeded crop profiles and district suitability are pending until cited and verified.
- **Stage 6B:** resource-level licensing/provenance inventory and fail-closed training gate exist. No commercial training source is approved or acquired. Open-Meteo is portfolio/research-only and is not integrated.
- **Stages 7, 8, 9:** **STOPPED**. No download, preprocessing for training, training, prediction, or validated model registry is authorized.
- **Existing private workspace:** JWT authentication, owner-scoped farm/plot CRUD, PostGIS boundaries, admin catalog routes, and tests exist. Local demo mode defaults off.
- **Public portfolio mode:** frontend read-only presentation and backend mode guard exist. The public deployment itself has not been tested or performed.
- **Unavailable:** weather/soil/market ingestion, disease/yield inference, RAG, SHAP, reporting, and notification services. Do not treat UI labels as implementation.

## Gated milestones

### A. Portfolio demo — current implementation

Maintain a public read-only district/crop catalogue, architecture and availability pages. Require backend and frontend demo flags together. Show source citations and verification state; expose no farmer rows or authentication.

### B. Data governance and acquisition — Stage 6B

Resolve each dataset's rights for the intended separate scopes. Obtain permission and representative, versioned data only after review. Keep non-commercial-only resources out of commercial work. This milestone is incomplete and is a prerequisite for the following stages.

### C. Stage 7 — preprocessing (blocked)

After explicit dataset approval, create reproducible source-specific ingestion, units/metadata normalization, quality checks, deduplication, and immutable group/spatial/time split manifests. Do not leak duplicate fields, farms, leaves, or time windows across evaluation splits.

### D. Stage 8 — model training/evaluation (blocked)

Train only for tasks with suitable labels and rights. Compare simple baselines; use spatial/group/time holdouts and region-specific external evaluation. Report confidence intervals, per-class/region performance, calibration, limitations, and drift. Do not promote based on training metrics alone.

### E. Stage 9 — model serving (blocked)

Register only validated, versioned model artifacts with feature schemas, training-data provenance, split definitions, evaluation, limitations, and rollback references. Add inference API/UI only after independent model and security review.

### F. Stages 10–12 — integration, advanced features, assurance

Build weather/soil/market interfaces only on verified provider data; add RAG with licensed agricultural references and citations; add SHAP only for validated models; generate reports with provenance; build real-data farm visualization only from consented geometry. Then add comprehensive security testing, performance measurement, monitoring, recovery drills, and deployment validation.

## Target architecture boundaries

- **Public:** static portfolio frontend; public, paginated district/crop catalogue GET APIs; source metadata and availability status. No authenticated user information.
- **Private API:** future user accounts, farms, plots, boundaries, and reports. JWT authorization and owner checks are mandatory for every private read/write.
- **Administration:** allowlisted catalog/data reviewers with audit history; never expose reviewer secrets or admin APIs publicly in demo mode.
- **Database:** PostgreSQL/PostGIS with Alembic-controlled changes. Preserve ownership constraints and add database-level Row Level Security before relying on direct client access. Browser clients never receive database credentials.
- **Data services:** provider-specific ingestion and normalization modules, separate from API/UI. Keep provider credentials and licensing constraints at backend boundaries.
- **Model services:** independent versioned artifacts, schemas, inference interfaces, and monitoring. No model is currently registered or validated.

## Data ownership and API contracts

Current public contracts include `GET /api/v1/districts`, `GET /api/v1/crop-categories`, `GET /api/v1/crops`, crop profile/variety reads, and district-crop reads. These return paginated public catalogue data with source and verification state.

Farm and plot endpoints are JWT-protected and scoped by `owner_id`. Future commercial use requires documented data ownership/consent, purpose limitation, retention/deletion/export policies, incident response, and rules for derived data. No farmer data should be used for training without explicit, documented rights and an approved dataset record.

Any future API contract change should update Pydantic response schemas, TypeScript types, OpenAPI documentation, authorization tests, and version/deprecation policy together.

## Future model versioning record

For each model release, retain model identifier/version and artifact digest; source dataset IDs, versions, licenses, and hashes; preprocessing code revision; feature/label schemas and units; train/validation/test grouping; metrics by task, class, district, and time; calibration/uncertainty; intended-use limits; approvals; inference dependencies; and rollback target. Do not store or expose a model artifact without its model card and provenance.

## Commercial readiness gates

Before any launch: resolve rights and provider agreements; complete privacy/threat assessment; review authentication/session lifecycle, rate limits, file-upload scanning, and abuse controls; implement data ownership and deletion workflows; validate production database policies/backups; set up monitoring/alerts/on-call; test restore and rollback; measure performance and costs; and obtain human agronomic review for recommendations. No paid infrastructure or API is included in the current portfolio implementation.
