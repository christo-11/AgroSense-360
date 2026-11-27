import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Database,
  FileCheck2,
  MapPinned,
  ShieldAlert,
  Sprout,
  ThermometerSun,
} from "lucide-react";
import {
  api,
  type CatalogueCompletenessResponse,
  type DataIntelligenceSummary,
  type DataProvenanceItem,
  type DataQualityResponse,
  type DataSourceAcquisition,
  type DataSourceSummary,
  type TrainingEligibilityResponse,
} from "../api";

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    APPROVED_PORTFOLIO_RESEARCH_ONLY: "Licence compatibility classification — not project authorization",
    APPROVED_PORTFOLIO_AND_COMMERCIAL: "Portfolio + commercial licence/terms classification — not project authorization",
    CONDITIONAL: "Conditional",
    BLOCKED: "Blocked",
    UNVERIFIED: "Unverified",
    not_downloaded: "Not recorded as downloaded",
    acquired: "Acquired (inventory)",
    metadata_verified_only: "Metadata verified only",
    blocked_pending_commercial_use_decision: "Blocked pending commercial decision",
    ACQUIRED_VERIFIED: "Acquired and verified",
    ACQUIRED_UNVERIFIED: "Acquired; verification incomplete",
    MISSING_ARCHIVE: "Archive missing",
    PROVENANCE_CONFLICT: "Provenance conflict",
    NOT_DOWNLOADED: "Not downloaded",
    VERIFIED: "Integrity verified",
    FAILED: "Integrity failed",
    NOT_ASSESSED: "Not assessed",
    QUALITY_REJECTED: "Quality rejected",
    NEEDS_MORE_DATA: "Insufficient data",
    REJECT_FOR_TRAINING: "Rejected for training",
    ACQUIRED_VERSION_UNPINNED: "Acquired; product version unpinned",
    INELIGIBLE: "Ineligible",
    GOVERNANCE_CHECK_REQUIRED: "Governance check required",
    NOT_ACQUIRED: "Not acquired",
  };
  return labels[status] ?? status.replace(/_/g, " ");
}

function statusClass(status: string) {
  return status.toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

function formatBytes(bytes: number | null) {
  if (bytes === null) return "Size not recorded";
  if (bytes >= 1_000_000_000) return `${(bytes / 1_000_000_000).toFixed(2)} GB`;
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`;
  return `${bytes.toLocaleString()} bytes`;
}

function formatUtc(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : `${date.toISOString().slice(0, 16).replace("T", " ")} UTC`;
}

function loadErrorMessage(reason: unknown) {
  return reason instanceof Error ? reason.message : "The API returned an unexpected error.";
}

function SourceStatus({ value }: { value: string }) {
  return <span className={`di-status di-status-${statusClass(value)}`}>{statusLabel(value)}</span>;
}

function LoadingPanel() {
  return (
    <div className="di-state" role="status">
      <Activity size={18} className="spin" />
      <span>Loading data intelligence evidence…</span>
    </div>
  );
}

export default function DataIntelligenceDashboard() {
  const [summary, setSummary] = useState<DataIntelligenceSummary | null>(null);
  const [sources, setSources] = useState<DataSourceSummary[]>([]);
  const [acquisitions, setAcquisitions] = useState<DataSourceAcquisition[]>([]);
  const [acquisitionWarnings, setAcquisitionWarnings] = useState<string[]>([]);
  const [quality, setQuality] = useState<DataQualityResponse | null>(null);
  const [eligibility, setEligibility] = useState<TrainingEligibilityResponse | null>(null);
  const [catalogue, setCatalogue] = useState<CatalogueCompletenessResponse | null>(null);
  const [provenance, setProvenance] = useState<DataProvenanceItem[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAcquisitionStatus, setSelectedAcquisitionStatus] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    const results = await Promise.allSettled([
      api.dataIntelligenceSummary(),
      api.dataIntelligenceSources(100, 0),
      api.dataIntelligenceAcquisitions(100, 0),
      api.dataIntelligenceQuality(),
      api.dataIntelligenceTrainingEligibility(100, 0),
      api.dataIntelligenceCatalogue(),
      api.dataIntelligenceProvenance(100, 0),
    ]);
    const nextErrors: string[] = [];
    const [summaryResult, sourcesResult, acquisitionResult, qualityResult, eligibilityResult, catalogueResult, provenanceResult] = results;

    if (summaryResult.status === "fulfilled") setSummary(summaryResult.value);
    else nextErrors.push(`Summary: ${loadErrorMessage(summaryResult.reason)}`);
    if (sourcesResult.status === "fulfilled") setSources(sourcesResult.value.items);
    else nextErrors.push(`Source inventory: ${loadErrorMessage(sourcesResult.reason)}`);
    if (acquisitionResult.status === "fulfilled") {
      setAcquisitions(acquisitionResult.value.items);
      setAcquisitionWarnings(acquisitionResult.value.validation_warnings);
    }
    else nextErrors.push(`Acquisition status: ${loadErrorMessage(acquisitionResult.reason)}`);
    if (qualityResult.status === "fulfilled") setQuality(qualityResult.value);
    else nextErrors.push(`Data quality: ${loadErrorMessage(qualityResult.reason)}`);
    if (eligibilityResult.status === "fulfilled") setEligibility(eligibilityResult.value);
    else nextErrors.push(`Training eligibility: ${loadErrorMessage(eligibilityResult.reason)}`);
    if (catalogueResult.status === "fulfilled") setCatalogue(catalogueResult.value);
    else nextErrors.push(`Catalogue coverage: ${loadErrorMessage(catalogueResult.reason)}`);
    if (provenanceResult.status === "fulfilled") setProvenance(provenanceResult.value.items);
    else nextErrors.push(`Provenance: ${loadErrorMessage(provenanceResult.reason)}`);

    setErrors(nextErrors);
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const hasData = Boolean(summary || sources.length || acquisitions.length || quality || eligibility || catalogue || provenance.length);
  if (loading && !hasData) return <LoadingPanel />;
  if (!loading && !hasData) {
    return (
      <section className="di-dashboard">
        <div className="di-error" role="alert">
          <strong>Data intelligence could not be loaded.</strong>
          <span>{errors.join(" ") || "No dashboard data is available."}</span>
          <button className="button button-secondary" onClick={() => void refresh()}>Retry</button>
        </div>
      </section>
    );
  }

  const approvedPortfolio = summary?.portfolio_status_counts.APPROVED_PORTFOLIO_RESEARCH_ONLY ?? 0;
  const portfolioConditional = summary?.portfolio_status_counts.CONDITIONAL ?? 0;
  const portfolioBlocked = summary?.portfolio_status_counts.BLOCKED ?? 0;
  const portfolioUnverified = summary?.portfolio_status_counts.UNVERIFIED ?? 0;
  const commerciallyApproved = summary?.commercial_approval_counts.APPROVED ?? 0;
  const conditional = summary?.commercial_approval_counts.CONDITIONAL ?? 0;
  const blocked = summary?.commercial_approval_counts.BLOCKED ?? 0;
  const verifiedSources = summary?.acquisition_status_counts.ACQUIRED_VERIFIED ?? 0;
  const validationWarnings = [...new Set([
    ...(summary?.validation_warnings ?? summary?.metadata_warnings ?? []),
    ...acquisitionWarnings,
  ])];
  const acquisitionStatusRows = Object.entries(summary?.acquisition_status_counts ?? {})
    .filter(([, count]) => Number.isFinite(count) && count > 0)
    .sort(([left], [right]) => statusLabel(left).localeCompare(statusLabel(right)));
  const largestAcquisitionCount = Math.max(1, ...acquisitionStatusRows.map(([, count]) => count));
  const visibleSources = selectedAcquisitionStatus
    ? sources.filter((source) => source.acquisition_status === selectedAcquisitionStatus)
    : sources;

  return (
    <section className="di-dashboard" aria-label="Agricultural data intelligence dashboard">
      <div className="di-toolbar">
        <div>
          <p className="di-kicker">READ-ONLY EVIDENCE</p>
          <p className="di-intro">This dashboard reports registered metadata and catalogue records. It does not generate crop predictions or recommendations.</p>
        </div>
        <button className="button button-secondary" onClick={() => void refresh()} disabled={loading}>
          <Activity size={15} className={loading ? "spin" : ""} />
          {loading ? "Refreshing" : "Refresh"}
        </button>
      </div>

      {errors.length > 0 && (
        <div className="di-error" role="alert">
          <strong>Some dashboard sections are unavailable.</strong>
          <span>{errors.join(" ")}</span>
        </div>
      )}
      {validationWarnings.map((warning) => (
        <div className="di-warning" role="note" key={warning}>
          <ShieldAlert size={18} />
          <span>{warning}</span>
        </div>
      ))}

      <div className="di-metric-grid">
        <article className="di-metric-card">
          <Database size={18} />
          <span>Registered data sources</span>
          <strong>{summary?.total_sources ?? "—"}</strong>
          <small>{summary?.manifest_request_count ?? 0} requests recorded; {summary?.manifest_reported_success_count ?? 0} marked successful in the manifest. {verifiedSources} source(s) have verified archives.</small>
        </article>
        <article className="di-metric-card">
          <FileCheck2 size={18} />
          <span>Portfolio licence/terms classifications</span>
          <strong>{approvedPortfolio}</strong>
          <small>{portfolioConditional} conditional · {portfolioBlocked} blocked · {portfolioUnverified} unverified. These are internal inventory classifications, not project-owner authorization or source-owner permission.</small>
        </article>
        <article className="di-metric-card">
          <ShieldAlert size={18} />
          <span>Sources marked commercially approved</span>
          <strong>{commerciallyApproved}</strong>
          <small>Portfolio classifications do not authorize commercial use; commercial review status is not project authorization.</small>
        </article>
        <article className="di-metric-card">
          <ShieldAlert size={18} />
          <span>Conditional / blocked commercial reviews</span>
          <strong>{conditional} / {blocked}</strong>
          <small>Commercial approval statuses in the source inventory</small>
        </article>
        <article className="di-metric-card">
          <ThermometerSun size={18} />
          <span>Training-eligible sources</span>
          <strong>{summary?.training_eligible_count ?? eligibility?.eligible_count ?? "—"}</strong>
          <small>Clearance requires the signed provenance governance gate</small>
        </article>
      </div>

      <section className="di-panel">
        <div className="di-panel-heading">
          <div><p className="di-kicker">INVENTORY VISUALIZATION</p><h2>Acquisition status counts</h2></div>
          {selectedAcquisitionStatus && (
            <button className="text-link" onClick={() => setSelectedAcquisitionStatus(null)}>Clear filter</button>
          )}
        </div>
        <p className="di-panel-copy">Counts describe registered source metadata only; they do not establish permission or project authorization. Select a status to filter the source inventory.</p>
        {!summary ? (
          <p className="di-empty">Acquisition status counts are unavailable.</p>
        ) : acquisitionStatusRows.length === 0 ? (
          <p className="di-empty">No acquisition status counts are recorded.</p>
        ) : (
          <div className="di-status-chart" role="group" aria-label="Filter source inventory by acquisition status">
            {acquisitionStatusRows.map(([status, count]) => (
              <button
                className={`di-chart-row ${selectedAcquisitionStatus === status ? "is-selected" : ""}`}
                type="button"
                key={status}
                aria-label={`Filter inventory by ${statusLabel(status)} (${count})`}
                aria-pressed={selectedAcquisitionStatus === status}
                onClick={() => setSelectedAcquisitionStatus((current) => current === status ? null : status)}
              >
                <span className="di-chart-label">{statusLabel(status)}</span>
                <span className="di-chart-track" aria-hidden="true">
                  <span style={{ width: `${(count / largestAcquisitionCount) * 100}%` }} />
                </span>
                <strong>{count}</strong>
              </button>
            ))}
          </div>
        )}
      </section>

      <div className="di-section-grid">
        <section className="di-panel">
          <div className="di-panel-heading">
            <div><p className="di-kicker">WEATHER EVIDENCE</p><h2>ERA5-Land quality</h2></div>
            <SourceStatus value={summary?.weather_decision ?? quality?.overall_decision ?? "Unavailable"} />
          </div>
          <p className="di-panel-copy">
            Overall training status: <SourceStatus value={summary?.weather_training_status ?? quality?.overall_training_status ?? "Unavailable"} />
          </p>
          {quality ? (
            <div className="di-archive-grid">
              {quality.archives.map((archive) => (
                <article className="di-archive-card" key={archive.request_number}>
                  <div className="di-card-title">
                    <strong>Archive request {archive.request_number}</strong>
                    <SourceStatus value={archive.training_status} />
                  </div>
                  <p>{archive.dynamic_timestamp_count} dynamic weather timestamps</p>
                  {archive.coverage_start_utc && archive.coverage_end_utc && (
                    <p>Coverage: {formatUtc(archive.coverage_start_utc)} to {formatUtc(archive.coverage_end_utc)}</p>
                  )}
                  <p>Global-grid missingness: {(archive.global_grid_missing_fraction * 100).toFixed(2)}%</p>
                  {archive.observed_gap_hours.length > 0 && (
                    <p>Observed intervals / gaps: {archive.observed_gap_hours.map((hours) => `${hours}h`).join(", ")}</p>
                  )}
                  <small>{archive.missingness_scope}</small>
                  <strong className="di-warning-text">{archive.warning}</strong>
                </article>
              ))}
            </div>
          ) : <p className="di-empty">Weather quality report is unavailable.</p>}
        </section>

        <section className="di-panel">
          <div className="di-panel-heading">
            <div><p className="di-kicker">CATALOGUE COVERAGE</p><h2>Districts and crops</h2></div>
            <Sprout size={19} />
          </div>
          {catalogue ? (
            <>
              <div className="di-coverage-grid">
                <div><strong>{catalogue.districts_total}</strong><span>Districts</span></div>
                <div><strong>{catalogue.crops_total}</strong><span>Crops</span></div>
                <div><strong>{catalogue.crop_categories_total}</strong><span>Crop categories</span></div>
                <div><strong>{catalogue.district_crop_associations_total}</strong><span>District-crop associations</span></div>
              </div>
              <ul className="di-facts">
                <li>{catalogue.crop_profiles_total} crop profiles; {catalogue.verified_crop_profiles} verified</li>
                <li>{catalogue.crop_varieties_total} registered varieties</li>
                <li>{catalogue.districts_with_suitability} districts have suitability associations</li>
                <li>Profile record coverage: {catalogue.crop_profile_coverage_percent === null ? "not measurable" : `${catalogue.crop_profile_coverage_percent}%`}</li>
                <li>District suitability coverage: {catalogue.district_suitability_coverage_percent === null ? "not measurable" : `${catalogue.district_suitability_coverage_percent}%`}</li>
              </ul>
              <p className="di-panel-copy">Profile coverage counts existing rows only; it does not measure profile-field completeness or agronomic verification.</p>
            </>
          ) : <p className="di-empty">Catalogue completeness is unavailable because the database query did not succeed.</p>}
        </section>
      </div>

      <section className="di-panel">
        <div className="di-panel-heading">
          <div><p className="di-kicker">SOURCE GOVERNANCE</p><h2>Dataset source inventory</h2></div>
          <span className="di-muted">{visibleSources.length}{selectedAcquisitionStatus ? ` of ${sources.length}` : ""} records shown</span>
        </div>
        {sources.length === 0 ? (
          <p className="di-empty">{loading ? "Loading source records…" : "No dataset sources are registered."}</p>
        ) : visibleSources.length === 0 ? (
          <p className="di-empty">No source records match the selected acquisition status.</p>
        ) : (
          <div className="di-table-wrap">
            <table className="di-table">
              <thead><tr><th>Dataset</th><th>Portfolio licence/terms classification</th><th>Commercial review status</th><th>Inventory acquisition</th><th>Archive integrity</th><th>Data quality</th><th>Version</th></tr></thead>
              <tbody>
                {visibleSources.map((source) => (
                  <tr key={source.id}>
                    <td><strong>{source.name}</strong><small>{source.publisher}</small></td>
                    <td><SourceStatus value={source.portfolio_status} /></td>
                    <td><SourceStatus value={source.commercial_approval_status} /></td>
                    <td><SourceStatus value={source.inventory_acquisition_status} /></td>
                    <td><SourceStatus value={source.archive_integrity_status} /></td>
                    <td><SourceStatus value={source.data_quality_status} /></td>
                    <td>{source.dataset_version ?? statusLabel(source.version_status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="di-section-grid">
        <section className="di-panel">
          <div className="di-panel-heading">
            <div><p className="di-kicker">ACQUISITION STATUS</p><h2>Manifest records</h2></div>
            <FileCheck2 size={19} />
          </div>
          {acquisitions.length === 0 ? <p className="di-empty">No acquisition entries are available.</p> : (
            <div className="di-record-list">
              {acquisitions.filter((entry) => entry.artifacts.length > 0).map((entry) => (
                <article className="di-record" key={entry.id}>
                  <div className="di-card-title"><strong>{entry.name}</strong><SourceStatus value={entry.acquisition_status} /></div>
                  <p className="di-panel-copy">
                    Inventory: <SourceStatus value={entry.inventory_status} /> · Archive integrity: <SourceStatus value={entry.archive_integrity_status} /> · Data quality: <SourceStatus value={entry.data_quality_status} />
                  </p>
                  <p className="di-panel-copy">{entry.status_explanation}</p>
                  {entry.validation_warnings.map((warning) => (
                    <div className="di-warning" role="note" key={warning}>
                      <ShieldAlert size={16} /><span>{warning}</span>
                    </div>
                  ))}
                  {entry.artifacts.map((artifact) => (
                    <div className="di-artifact" key={artifact.request_number}>
                      <div className="di-card-title"><strong>{artifact.filename}</strong><SourceStatus value={artifact.acquisition_status} /></div>
                      <span>{artifact.request_status}</span>
                      <span>Archive integrity: <SourceStatus value={artifact.archive_integrity_status} /> · Data quality: <SourceStatus value={artifact.data_quality_status} /></span>
                      <small>Recorded size: {formatBytes(artifact.size_bytes)} · observed size: {formatBytes(artifact.actual_size_bytes)} · {artifact.retrieved_at ? formatUtc(artifact.retrieved_at) : "retrieval time not recorded"}</small>
                      {artifact.validation_warnings.map((warning) => <small className="di-warning-text" key={warning}>{warning}</small>)}
                    </div>
                  ))}
                </article>
              ))}
              {acquisitions.every((entry) => entry.artifacts.length === 0) && (
                <p className="di-empty">The manifest contains no archive artifacts.</p>
              )}
            </div>
          )}
        </section>

        <section className="di-panel">
          <div className="di-panel-heading">
            <div><p className="di-kicker">TRAINING GATE</p><h2>Eligibility assessment</h2></div>
            <ShieldAlert size={19} />
          </div>
          {eligibility ? (
            <>
              <p className="di-panel-copy">{eligibility.eligible_count} of {eligibility.total_sources} sources are eligible. {eligibility.note}</p>
              <div className="di-eligibility-list">
                {eligibility.items.items.map((item) => (
                  <details key={item.id}>
                    <summary><span>{item.name}</span><SourceStatus value={item.status} /></summary>
                    <ul>{item.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
                  </details>
                ))}
              </div>
            </>
          ) : <p className="di-empty">Training eligibility metadata is unavailable.</p>}
        </section>
      </div>

      <section className="di-panel">
        <div className="di-panel-heading">
          <div><p className="di-kicker">PROVENANCE</p><h2>Version and artifact evidence</h2></div>
          <MapPinned size={19} />
        </div>
        {provenance.length === 0 ? <p className="di-empty">No provenance entries are available.</p> : (
          <div className="di-provenance-grid">
            {provenance.map((item) => (
              <article className="di-provenance-card" key={item.id}>
                <strong>{item.name}</strong>
                <span>{item.publisher}</span>
                <small>{item.license ?? "License not recorded"} · {item.dataset_version ?? statusLabel(item.version_status)}</small>
                <small>Inventory checked: {item.last_checked ?? "date not recorded"}</small>
                <small>Acquisition: <SourceStatus value={item.acquisition_status} /> · Integrity: <SourceStatus value={item.archive_integrity_status} /> · Data quality: <SourceStatus value={item.data_quality_status} /></small>
                {item.validation_warnings.map((warning) => <small className="di-warning-text" key={warning}>{warning}</small>)}
                {item.artifacts.map((artifact) => (
                  <details key={artifact.request_number}>
                    <summary>Request {artifact.request_number} provenance evidence</summary>
                    <code>{artifact.sha256 ?? "SHA-256 not recorded"}</code>
                    <span>Checksum comparison {artifact.checksum_verified ? "matched" : "unverified"} · ZIP CRC {artifact.zip_crc_valid === null ? "not checked" : artifact.zip_crc_valid ? "valid" : "invalid"} · format {artifact.zip_format_valid === null ? "not checked" : artifact.zip_format_valid ? "valid" : "invalid"}</span>
                    <span>{artifact.status_explanation}</span>
                  </details>
                ))}
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}
