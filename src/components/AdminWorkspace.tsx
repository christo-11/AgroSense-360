import { ArrowUpRight, Database, Leaf, ShieldCheck, Users } from "lucide-react";
import type { AdminSummary, PlatformStatus } from "../api";

type Props = {
  summary: AdminSummary | null;
  status: PlatformStatus | null;
  error: string;
  onOpenCatalogue: () => void;
  onOpenDataIntelligence: () => void;
};

function AdminMetric({ label, value, icon: Icon }: { label: string; value: number; icon: typeof Users }) {
  return (
    <article className="admin-metric glass-card">
      <Icon size={17} />
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

export default function AdminWorkspace({
  summary,
  status,
  error,
  onOpenCatalogue,
  onOpenDataIntelligence,
}: Props) {
  if (!summary) {
    return <div className="workspace-error" role="alert">{error || "Admin overview is unavailable. Refresh to try again."}</div>;
  }

  const integrations = Object.entries(summary.integrations);
  const models = Object.entries(summary.models);

  return (
    <section className="admin-workspace">
      {error && <div className="workspace-error" role="alert">{error}</div>}
      <div className="admin-metric-grid">
        <AdminMetric label="Accounts" value={summary.users} icon={Users} />
        <AdminMetric label="Farms" value={summary.farms} icon={Database} />
        <AdminMetric label="Plots" value={summary.plots} icon={Leaf} />
        <AdminMetric label="Kerala districts" value={summary.districts} icon={ShieldCheck} />
        <AdminMetric label="Catalogue crops" value={summary.crops} icon={Leaf} />
        <AdminMetric label="Verified crop profiles" value={summary.verified_crop_profiles} icon={ShieldCheck} />
        <AdminMetric label="Verified district associations" value={summary.verified_district_associations} icon={ShieldCheck} />
        <AdminMetric label="Source references" value={summary.source_references} icon={Database} />
      </div>
      <div className="admin-section-grid">
        <article className="panel glass-card">
          <div className="panel-heading"><div><h2>Data integrations</h2><p>Configuration status only; no secrets are exposed.</p></div></div>
          <ul className="admin-status-list">
            {integrations.map(([key, item]) => (
              <li key={key}>
                <strong>{key.replace(/_/g, " ")}</strong>
                <span className={item.configured ? "admin-status-ready" : "admin-status-unavailable"}>{item.status}</span>
                <small>{item.detail}</small>
              </li>
            ))}
            {status?.database === "unavailable" && (
              <li><strong>database</strong><span className="admin-status-unavailable">unavailable</span><small>Database health check failed.</small></li>
            )}
          </ul>
        </article>
        <article className="panel glass-card">
          <div className="panel-heading"><div><h2>Model services</h2><p>Predictions are not shown unless a validated model is deployed.</p></div></div>
          <ul className="admin-status-list">
            {models.map(([key, item]) => (
              <li key={key}>
                <strong>{key.replace(/_/g, " ")}</strong>
                <span className={item.configured ? "admin-status-ready" : "admin-status-unavailable"}>{item.status}</span>
                <small>{item.detail}</small>
              </li>
            ))}
          </ul>
        </article>
      </div>
      <div className="admin-actions">
        <button className="button button-secondary" type="button" onClick={onOpenCatalogue}>Review crop catalogue <ArrowUpRight size={14} /></button>
        <button className="button button-secondary" type="button" onClick={onOpenDataIntelligence}>Review data provenance <ArrowUpRight size={14} /></button>
      </div>
      <p className="market-attribution">Administrative access is enforced by the server-side email allowlist. Initial accounts and password resets are handled by the secure bootstrap command.</p>
    </section>
  );
}
