import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  Cloud,
  Database,
  Leaf,
  LockKeyhole,
  Map,
  Server,
  ShieldCheck,
  Sprout,
} from "lucide-react";
import { api, type PlatformStatus } from "../api";
import sourceInventory from "../../data/metadata/source_inventory.json";

type Props = {
  status: PlatformStatus | null;
  statusError: string;
  onBrowseCatalog: () => void;
  onOpenArchitecture: () => void;
  onOpenSources: () => void;
};
type AvailabilityState = "available" | "unavailable" | "disabled" | "record_level" | "checking";

type PortfolioStatus =
  | "APPROVED_PORTFOLIO_AND_COMMERCIAL"
  | "APPROVED_PORTFOLIO_RESEARCH_ONLY"
  | "CONDITIONAL"
  | "BLOCKED"
  | "UNVERIFIED";

type SourceReview = {
  approval_status: string;
  license_name: string;
  attribution_obligations: string;
  access_status: string;
  evidence_urls: string[];
  remaining_concerns: string[];
};

const sourceReviews = sourceInventory.commercial_reviews as Record<string, SourceReview>;
const portfolioReviews = sourceInventory.portfolio_reviews as Record<
  string,
  { status: PortfolioStatus; rationale: string }
>;
const portfolioStatusLabels: Record<PortfolioStatus, string> = {
  APPROVED_PORTFOLIO_AND_COMMERCIAL: "Licence/terms review — not project authorization",
  APPROVED_PORTFOLIO_RESEARCH_ONLY: "Licence/terms review — not project authorization",
  CONDITIONAL: "Conditional",
  BLOCKED: "Blocked",
  UNVERIFIED: "Unverified",
};

function Availability({ label, state, detail }: { label: string; state: AvailabilityState; detail: string }) {
  const labels: Record<AvailabilityState, string> = {
    available: "Available",
    unavailable: "Unavailable",
    disabled: "Disabled in demo",
    record_level: "Per-record status",
    checking: "Checking",
  };
  return (
    <article className="portfolio-availability-card">
      <div className="portfolio-availability-heading">
        <strong>{label}</strong>
        <span className={`portfolio-state ${state === "available" ? "is-available" : ""}`}>
          {labels[state]}
        </span>
      </div>
      <p>{detail}</p>
    </article>
  );
}

export function PortfolioLanding({
  status,
  statusError,
  onBrowseCatalog,
  onOpenArchitecture,
  onOpenSources,
}: Props) {
  const demoModeConfirmed = status?.public_demo_mode === true;
  const [catalogueCheck, setCatalogueCheck] = useState<{
    state: AvailabilityState;
    detail: string;
  }>({
    state: "checking",
    detail: "Checking the district and crop catalogue endpoints.",
  });

  useEffect(() => {
    let active = true;
    if (!demoModeConfirmed || status?.api !== "online" || status.database !== "connected") {
      setCatalogueCheck({
        state: "unavailable",
        detail: "Requires a reachable backend that confirms the local read-only configuration.",
      });
      return () => { active = false; };
    }

    setCatalogueCheck({ state: "checking", detail: "Checking the district and crop catalogue endpoints." });
    void Promise.all([api.districts(1), api.crops({ limit: 1 })]).then(([districtPage, cropPage]) => {
      if (!active) return;
      const districtCount = districtPage.total;
      const cropCount = cropPage.total;
      const ready = districtCount === 14 && cropCount > 0;
      setCatalogueCheck({
        state: ready ? "available" : "unavailable",
        detail: ready
          ? `The local API reports ${districtCount} districts and ${cropCount} crop records. Individual verification remains visible per record.`
          : `The API reports ${districtCount} districts and ${cropCount} crops; the expected 14-district catalogue is incomplete.`,
      });
    }).catch((error: unknown) => {
      if (!active) return;
      setCatalogueCheck({
        state: "unavailable",
        detail: error instanceof Error ? error.message : "The local catalogue endpoints could not be checked.",
      });
    });

    return () => { active = false; };
  }, [demoModeConfirmed, status?.api, status?.database]);
  return (
    <div className="portfolio-page">
      <section className="portfolio-hero glass-card" aria-labelledby="portfolio-title">
        <div className="portfolio-hero-copy">
          <div className="eyebrow"><span className="live-dot" /> PROPOSED LOCAL PREVIEW · READ ONLY</div>
          <h2 id="portfolio-title">Agriculture intelligence, grounded in transparent data.</h2>
          <p>
            AgroSense-360 is a Kerala-focused technical preview for district and crop catalogue
            information. This interface is not authorization for a public demonstration or data distribution.
          </p>
          <div className="portfolio-actions">
            <button type="button" className="button button-primary" onClick={onBrowseCatalog}>
              <Map size={15} /> Explore districts & crops
            </button>
            <button type="button" className="button button-secondary" onClick={onOpenArchitecture}>
              <ArrowUpRight size={15} /> Project architecture
            </button>
          </div>
        </div>
        <div className="portfolio-hero-note">
          <ShieldCheck size={20} />
          <strong>Public demonstration and data distribution are NOT AUTHORIZED.</strong>
          <span>Technical read-only capability and internal licence classification do not grant source-owner permission or project-owner authorization.</span>
        </div>
      </section>

      <section className="portfolio-section" aria-labelledby="availability-title">
        <div className="portfolio-section-heading">
          <div><span className="eyebrow">FEATURE AVAILABILITY</span><h2 id="availability-title">What this local preview can do</h2></div>
          <button type="button" className="text-link" onClick={onOpenSources}>Sources & attribution <ArrowUpRight size={14} /></button>
        </div>
        {statusError && <p className="catalog-error" role="alert">{statusError}</p>}
        {status && !demoModeConfirmed && (
          <p className="catalog-error" role="alert">
            Backend configuration controls technical routes only; it does not authorize public demonstrations, data distribution, or deployment.
          </p>
        )}
        <div className="portfolio-availability-grid">
          <Availability
            label="Kerala district & crop catalogue"
            state={catalogueCheck.state}
            detail={catalogueCheck.detail}
          />
          <Availability
            label="Verified agronomic profiles"
            state="record_level"
            detail="Only profiles with recorded sources and a verified status may be treated as confirmed guidance; pending fields stay unverified."
          />
          <Availability
            label="Private farm records"
            state="disabled"
            detail="Authentication, registration, farm reads, and writes are disabled in this technical configuration."
          />
          <Availability
            label="Weather, market, soil & AI models"
            state="unavailable"
            detail="No live provider results, model predictions, or fabricated example metrics are shown."
          />
        </div>
      </section>

      <section className="portfolio-guardrail glass-card">
        <div className="portfolio-guardrail-icon"><LockKeyhole size={17} /></div>
        <div>
          <h2>Technical capability is not activity authorization.</h2>
          <p>
            Publisher terms and internal classifications do not establish source-owner permission or
            project-owner authorization. Each proposed activity requires its own applicable permission;
            public demonstration, research, redistribution, training, commercial use, and deployment remain NOT AUTHORIZED.
          </p>
        </div>
        <button type="button" className="button button-secondary" onClick={onOpenSources}>Review data status</button>
      </section>
    </div>
  );
}

export function ProjectArchitecture() {
  return (
    <div className="portfolio-page">
      <section className="portfolio-section">
        <div className="portfolio-section-heading">
          <div><span className="eyebrow">SYSTEM OVERVIEW</span><h2>Project architecture</h2></div>
          <span className="portfolio-state">Prototype · not production-ready</span>
        </div>
        <div className="architecture-grid">
          <article className="architecture-card glass-card">
            <Sprout size={19} /><h3>React + TypeScript + Vite</h3>
            <p>Catalogue UI and authenticated workspace share the existing client; this local preview hides private account features.</p>
          </article>
          <article className="architecture-card glass-card">
            <Server size={19} /><h3>FastAPI</h3>
            <p>Versioned read APIs serve districts and crop records. JWT-protected farm, plot, and administration APIs remain private.</p>
          </article>
          <article className="architecture-card glass-card">
            <Database size={19} /><h3>PostgreSQL + PostGIS</h3>
            <p>SQLAlchemy and Alembic manage catalogue and private spatial records. The local preview exposes no farmer-owned rows.</p>
          </article>
          <article className="architecture-card glass-card">
            <Leaf size={19} /><h3>Data and model services</h3>
            <p>Provider ingestion and inference are independent modules. Unapproved sources and unvalidated models remain unavailable.</p>
          </article>
        </div>
      </section>
      <section className="portfolio-section glass-card architecture-contracts">
        <h2>Catalogue API contract</h2>
        <ul>
          <li><code>GET /api/v1/districts</code> — paginated Kerala districts</li>
          <li><code>GET /api/v1/crop-categories</code>, <code>GET /api/v1/crops</code> — catalogue and category filters</li>
          <li><code>GET /api/v1/crops/{'{crop_id}'}</code>, profile, and varieties — record-level verification and sources</li>
          <li><code>GET /api/v1/districts/{'{district_id}'}/crops</code> — only recorded district associations</li>
        </ul>
        <p>All private farm and plot endpoints require authentication and are disabled in the local preview configuration. This technical setting does not grant authorization for external use.</p>
      </section>
      <section className="portfolio-section architecture-boundaries">
        <div><LockKeyhole size={16} /><strong>Authentication boundary</strong><p>Registration and login are disabled in demo mode. Local development keeps the existing JWT flow.</p></div>
        <div><Cloud size={16} /><strong>External services</strong><p>No external service is connected in this local preview. Credentials stay on the backend and are not part of the frontend bundle.</p></div>
      </section>
    </div>
  );
}

export function PortfolioDataSources() {
  return (
    <div className="portfolio-page">
      <section className="portfolio-section">
        <div className="portfolio-section-heading">
          <div><span className="eyebrow">PROVENANCE & RIGHTS</span><h2>Data sources and attribution</h2></div>
          <span className="portfolio-state">No source approved for model training</span>
        </div>
        <p className="portfolio-source-intro">
          Portfolio classifications are internal assessments of apparent publisher licence/terms compatibility only.
          They are not project-owner authorization, source-owner permission, or approval to access/acquire data,
          conduct research, train ML, publicly demonstrate, or deploy. Portfolio/demo and pilot research are
          separate project permission scopes; both are currently NOT AUTHORIZED. Public availability is not
          permission to redistribute, train, or commercialize.
        </p>
        <div className="portfolio-source-grid">
          {sourceInventory.datasets.map((source) => {
            const review = sourceReviews[source.id];
            const portfolioReview = portfolioReviews[source.id];
            const sourceStatus = portfolioReview?.status ?? "UNVERIFIED";
            const officialUrl = "official_url" in source && source.official_url
              ? source.official_url
              : "official_urls" in source
                ? source.official_urls?.[0]
                : undefined;
            return (
              <article className="portfolio-source-card glass-card" key={source.id}>
                <div className="portfolio-source-title">
                  <div><h3>{source.name}</h3><span>{source.publisher}</span></div>
                  <span className={`portfolio-state status-${sourceStatus.toLowerCase()}`}>
                    {portfolioStatusLabels[sourceStatus]}
                  </span>
                </div>
                <p>
                  <strong>Internal licence/terms assessment; not project authorization:</strong>{" "}
                  {portfolioReview?.rationale ?? "Portfolio use has not been reviewed."}
                </p>
                <p>{review?.license_name ?? source.license}</p>
                <dl>
                  <div><dt>Attribution</dt><dd>{review?.attribution_obligations ?? "Not verified"}</dd></div>
                  <div><dt>Access review</dt><dd>{review?.access_status ?? "Not reviewed"}</dd></div>
                  <div><dt>Training gate</dt><dd>{review?.approval_status ?? "UNVERIFIED"}</dd></div>
                  <div><dt>Dataset version</dt><dd>{source.dataset_version ?? source.version_status}</dd></div>
                </dl>
                {officialUrl && (
                  <a href={officialUrl} target="_blank" rel="noopener noreferrer">
                    Official source <ArrowUpRight size={13} />
                  </a>
                )}
                {review?.evidence_urls?.length > 0 && (
                  <details>
                    <summary>Review evidence and limitations</summary>
                    <ul>{review.evidence_urls.map((url) => <li key={url}><a href={url} target="_blank" rel="noopener noreferrer">{url}</a></li>)}</ul>
                    {review.remaining_concerns.length > 0 && <p>Open issues: {review.remaining_concerns.join("; ")}</p>}
                  </details>
                )}
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
