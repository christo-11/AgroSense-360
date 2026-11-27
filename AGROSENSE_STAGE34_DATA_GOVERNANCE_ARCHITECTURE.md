# AgroSense-360 Stage 34 — Database and Data Governance Architecture

**Status:** Architecture proposal only. No database was queried or changed; no migration or application behavior was modified.

## 1. Current-state review

The inspected application uses SQLAlchemy models with Alembic migrations and PostGIS geometry. Existing persisted structures cover:

- Users, farms and plots, including private farm/plot geometries.
- Crop categories, crops, nullable crop scientific names, crop profiles, crop varieties, Kerala district names, and district-crop-suitability associations.
- `AgriculturalSource` records with title, publisher, URL, nullable licence, access date, notes, and optional creator.
- Source links from crop profiles, varieties, and district-crop claims.

The crop profile and district suitability tables have simple verification statuses and source associations. They do not provide field-level claim evidence, exact dataset release/version, acquisition artifact lineage, terms snapshots, per-purpose permissions, quality-run history, or model-training lineage.

The machine-readable `data/metadata/source_inventory.json` is the current resource/commercial-review registry. `backend/scripts/dataset_governance.py` validates it and implements a fail-closed signed approval/provenance gate for training. Existing checks include resource IDs and URLs, licence/version and rights fields, allowlisted reviewer/signature, acquired status, quality/relevance, a provenance manifest, and matching SHA-256. `record_admin_review` can update the JSON inventory when run through its protected administrative process. Existing tests assert that unapproved project sources are rejected.

The inventory and associated JSON artifacts hold acquisition/quality status and ERA5-Land details. They are not relational acquisition, artifact, quality-run, feature, or model-run tables. No dedicated weather observations, weather feature values, dataset release, permission-response evidence, or ML run records appear in the inspected ORM model.

## 2. Target logical architecture

Keep the following entities separate. They can initially be represented by reviewed metadata/artifact records; any database schema change requires a separate approved implementation stage.

| Entity | Purpose and key relationships |
|---|---|
| **SourceOwner** | Publisher/legal owner identity and verified official URLs/contact-channel references; one owner can publish many sources. Do not invent contacts. |
| **SourceResource** | Exact resource/dataset, source ID, official page, access method, expected format, geographic/temporal scope, and responsible owner. Distinguish an owner/site from a licensed resource. |
| **DatasetRelease** | Immutable source product/version/run/schema and terms snapshot reference; `NOT_PINNED` is explicit and cannot be treated as “latest.” |
| **AcquisitionRecord** | Separately approved request/asset acquisition attempt, purpose, exact parameters, requested period/area/variables, request or ticket ID, status transitions, retrieval time, and reviewer references. |
| **Artifact** | Immutable file/member/object metadata: URI outside Git, size, SHA-256, media type, archive/member relationships, checksum state and retention class. Store raw bytes in access-controlled object storage, not relational rows. |
| **PermissionDecision** | Resource/release + purpose-specific status, scope, decision date, project-owner approval reference, source-owner evidence, reviewer, expiry/conditions, attribution and redistribution conditions. |
| **PermissionEvidence** | Original written terms/response or official URL snapshot, hash, received/accessed date, sender/source, and integrity. Restrict access to sensitive correspondence. |
| **QualityRun / QualityCheckResult** | Immutable evaluation version, inputs, scope, metrics, thresholds, result, failed/warned partitions, software version and report artifact. Does not grant permission. |
| **WeatherObservation / AgronomicClaim** | Normalized value/claim with source release, artifact/record reference, measured/estimated/derived/forecast type, unit, time interval, spatial support, quality status and verification evidence. |
| **FeatureDefinition / FeatureRun / FeatureValue** | Versioned formula, parameters, inputs, output units and lineage; each value points to input observation IDs and quality/permission context. |
| **TrainingRun / ModelArtifact** | Future training purpose, immutable dataset snapshot and splits, feature/label versions, code/environment, approvals, metrics, model checksums and deployment status. No run can proceed until all gates pass. |
| **AuditEvent** | Append-only actor/action/time/target/decision/evidence reference; supports changes to source, release, rights, quality, training and access records. |

Use stable IDs and foreign keys; avoid copying mutable licence/approval values into observations as the only evidence. Each use resolves the applicable release and decision at the time of use.

## 3. Dataset and source registry

### Source registry

Retain the existing JSON inventory as the authoritative signed approval record until a future, explicitly approved migration plan establishes a single canonical write path. Do not create an unsynchronized second “approval truth” in the database.

Each resource entry should include:

- Stable resource ID, owner, exact dataset title, official landing URL and access method.
- `dataset_version` and `version_status`; never populate an unverified version.
- File format, geographic/temporal coverage, variables and intended evidence type.
- Licence name/version/URL and attribution, modification, commercial, redistribution, share-alike and third-party conditions.
- Separate portfolio/research, pilot, commercial, redistribution and ML training decisions.
- Acquisition status, provenance/manifest reference, checksums per artifact, and quality/relevance status.
- Reviewer, decision date, reason, signature and unresolved concerns.

Publisher and resource identity are separate. A page URL alone is not a dataset release and does not establish a licence for every hosted item.

### Acquisition and release registry

Acquisition requests, successful retrievals, failed attempts, and dataset releases are different records. Keep request parameters and IDs distinct from receipt IDs and object-store IDs; record a content-based correlation as such if direct identifier mapping is unavailable. A release must have immutable raw artifacts, a checksum per file, terms snapshot and provenance manifest before quality assessment.

Existing ERA5-Land remains a single acquired source with two separate artifacts and checksums; its version is unpinned. Stage 28 statuses remain request 1 `ACCEPTABLE WITH LIMITATIONS` and request 2 `REJECTED`. Stage 27 records the Copernicus inquiry as NOT SUBMITTED and owner approval NOT RECORDED.

## 4. Permission and approval workflow

Track permissions as a vector, not one “approved” boolean:

1. Prepare draft inquiry.
2. Send inquiry to named owner.
3. Receive/store/review response.
4. Download public dataset.
5. Acquire restricted data with written permission.
6. Pilot/portfolio research use.
7. ML training, with research and commercial training distinct.
8. Commercial use and redistribution.

Each action requires its own applicable project-owner decision and evidence. Source-owner permission, licence rights, data quality, crop/geographic relevance and project-owner authorization are separate gates. Missing evidence defaults to **NOT AUTHORIZED**. An automated status cannot upgrade an approval; only the designated signed review process may do so.

Current Stage 23 project-owner authorization is pending/no for acquisition and use actions; no source-owner permission has been received; no source is approved for training. This architecture does not change those statuses.

## 5. Quality, feature and model lineage

- Quality results are immutable runs linked to exact artifact checksums, dataset release, check-suite/schema version, intended use and evaluated geography/period. New results supersede, but do not erase, prior findings.
- A “quality accepted” result is not a permission or training approval. The serving/training query must join and verify both.
- Feature definitions store formula, units, temporal window, boundary version, threshold provenance, imputation rule and code version. Feature runs point to every source release and raw observation contributing to output.
- Training runs reference a frozen dataset snapshot, label/feature definitions, temporal/spatial split, training permission, quality/relevance decisions, approval signature, code commit/environment and resulting model checksum.
- Separate model-development state from deployment state; a trained model does not become deployable by existence alone.

## 6. Audit and access controls

- Use role-based least privilege: source catalog editors, permission reviewers, acquisition operators, data stewards, scientific reviewers and model approvers have distinct responsibilities.
- Public-source metadata may be broadly readable; restricted data, personal/farm geometry and owner correspondence require scoped access and retention.
- Use append-only audit events for approvals, revocations, terms changes, source/version changes, acquisitions, artifact checks, quality releases, feature generation, training and access.
- Record actor/service identity, UTC time, action, before/after hashes or decision IDs, reason and evidence reference. Protect audit log integrity with append-only storage/periodic signed digests.
- Never store secrets, API tokens, passwords or private credentials in source inventory, database records, logs, manifests or reports.
- Store raw files in access-controlled object storage outside Git. Database stores metadata and references; backups and deletion/retention policies must respect source terms and privacy obligations.
- Separate duties: the requester/operator cannot be the sole reviewer of commercial/training permission; use the existing allowlisted, signed review approach or a separately approved equivalent.

## 7. Data model evolution and migration boundary

The current relational model is useful for crop catalogue and farm/plot geometry, but it is not sufficient as the full dataset governance ledger. Recommended target additions are conceptual only:

- Source/resource and release tables, with versioned term evidence.
- Acquisition and artifact tables, including request-to-receipt correlation and per-file checksums.
- Purpose-specific permission decisions/evidence.
- Quality-run/check-result tables.
- Weather observation and agronomic claim provenance references.
- Feature definitions/runs and model-training lineage.
- Append-only audit-event storage.

Before any migration: approve the canonical registry and data-retention model; map existing JSON and source associations without overwriting history; define nullable/unknown state semantics; plan backfill evidence and checksums; add FK/uniqueness constraints; create reversible migrations; test upgrade/downgrade and authorization failure paths; and provide a rollback plan. No Stage 34 migration or database write is authorized.

## 8. Current readiness and unresolved design decisions

- The source inventory JSON and signed governance gate exist, but the relational database has no unified release/acquisition/quality/feature/training lineage model.
- `AgriculturalSource` is a bibliographic link with a nullable licence, not a fully reviewed dataset-release record.
- Crop-profile and district-crop verification currently link sources at entity level, not to each field claim and applicable release.
- The project has no weather ingestion/persistence tables or production weather endpoint; current weather insight returns unavailable until verified services exist.
- The data model must preserve Idukki as provisional and keep research/portfolio, commercial and ML permissions separate.
- Remaining decisions: authoritative boundary version, raw-data storage/retention location, permission evidence access rules, canonical source inventory write path, reviewer separation, audit retention, and schema/backfill policy.

## 9. Decision

Adopt this as a planning architecture for future governance design, subject to project-owner and technical review. It does not authorize implementation, schema changes, data acquisition, source approval changes, research/pilot use, feature generation, ML training, commercial use, redistribution, or production deployment.
