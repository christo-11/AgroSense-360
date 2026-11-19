import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  ArrowUpRight,
  Bell,
  BookOpen,
  ChevronDown,
  CircleHelp,
  Cloud,
  CloudSun,
  Command,
  Download,
  Droplets,
  ExternalLink,
  Eye,
  FileImage,
  FlaskConical,
  Gauge,
  Leaf,
  LockKeyhole,
  MapPin,
  Menu,
  MessageCircle,
  Moon,
  Plus,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Sprout,
  Sun,
  TrendingUp,
  X,
} from "lucide-react";
import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { api, ApiError, type DashboardSummary, type Farm, type PlatformStatus } from "./api";
import FarmWorkspace from "./components/FarmWorkspace";
import CropExplorer from "./components/CropExplorer";
import { PortfolioDataSources, PortfolioLanding, ProjectArchitecture } from "./components/PortfolioDemo";
import StatusPill from "./components/StatusPill";

const FarmTwin = lazy(() => import("./components/FarmTwin"));

function DeferredFarmTwin({ reducedMotion }: { reducedMotion: boolean }) {
  const [nearViewport, setNearViewport] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    if (!("IntersectionObserver" in window)) {
      setNearViewport(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setNearViewport(true);
          observer.disconnect();
        }
      },
      { rootMargin: "160px" },
    );
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef}>
      {nearViewport ? (
        <Suspense fallback={<div className="twin-stage twin-loading" role="status">Loading interactive farm scene…</div>}>
          <FarmTwin reducedMotion={reducedMotion} />
        </Suspense>
      ) : (
        <div className="twin-stage twin-loading" role="status">Interactive scene loads when nearby</div>
      )}
    </div>
  );
}

type Module = "Overview" | "Crop catalogue" | "Field intelligence" | "Weather" | "Crop health" | "Markets" | "Reports" | "AI copilot" | "Project architecture" | "Data sources";
const PORTFOLIO_DEMO = import.meta.env.VITE_PUBLIC_DEMO === "true";

const navigation: { name: Module; icon: typeof Activity }[] = [
  { name: "Overview", icon: Gauge },
  { name: "Crop catalogue", icon: BookOpen },
  { name: "Field intelligence", icon: FlaskConical },
  { name: "Weather", icon: CloudSun },
  { name: "Crop health", icon: Leaf },
  { name: "Markets", icon: TrendingUp },
  { name: "Reports", icon: Download },
  { name: "AI copilot", icon: MessageCircle },
];

const portfolioNavigation: { name: Module; icon: typeof Activity }[] = [
  { name: "Overview", icon: Gauge },
  { name: "Crop catalogue", icon: BookOpen },
  { name: "Project architecture", icon: Command },
  { name: "Data sources", icon: ShieldCheck },
];

const moduleInfo: Record<Exclude<Module, "Overview" | "Crop catalogue" | "Project architecture" | "Data sources">, { title: string; description: string; icon: typeof Activity; source: string; statusKey: string }> = {
  "Field intelligence": {
    title: "Satellite soil intelligence",
    description: "Field-level SOC, pH and NPK insights require connected satellite imagery and a validated model.",
    icon: FlaskConical,
    source: "Sentinel-2 · SoilGrids",
    statusKey: "sentinel_2",
  },
  Weather: {
    title: "Hyperlocal weather",
    description: "Local forecasts appear after a weather provider and a farm location are configured.",
    icon: CloudSun,
    source: "NASA GPM · ERA5-Land",
    statusKey: "weather",
  },
  "Crop health": {
    title: "Crop health & disease",
    description: "Upload an image only when a trained, validated inference model is available.",
    icon: Leaf,
    source: "Computer vision model",
    statusKey: "disease_model",
  },
  Markets: {
    title: "Market intelligence",
    description: "Verified mandi prices and recommendations appear when the market data feed is connected.",
    icon: TrendingUp,
    source: "AGMARKNET",
    statusKey: "agmarknet",
  },
  Reports: {
    title: "Farm reports",
    description: "Reports are generated from your connected farm records and verified observations.",
    icon: Download,
    source: "Farm records",
    statusKey: "soilgrids",
  },
  "AI copilot": {
    title: "Agriculture copilot",
    description: "Ask grounded questions about your farm once the retrieval and language-model service is configured.",
    icon: MessageCircle,
    source: "RAG service · regional voice",
    statusKey: "copilot",
  },
};

function MetricCard({ title, icon: Icon, detail }: { title: string; icon: typeof Activity; detail: string }) {
  return (
    <article className="metric-card glass-card">
      <div className="metric-heading">
        <span className="metric-icon"><Icon size={17} /></span>
        <span>{title}</span>
        <span className="metric-menu">···</span>
      </div>
      <div className="metric-value unavailable-value">— <span>Unavailable</span></div>
      <div className="metric-footnote">{detail}</div>
    </article>
  );
}

function EmptyChart({ label }: { label: string }) {
  return (
    <div className="empty-chart">
      <div className="chart-grid" aria-hidden="true"><span /><span /><span /><span /></div>
      <div className="empty-chart-message">
        <span className="empty-chart-icon"><Activity size={18} /></span>
        <strong>No verified {label.toLowerCase()} yet</strong>
        <span>Connect a data provider to see real farm observations here.</span>
      </div>
    </div>
  );
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  return (
    <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <motion.div className="modal glass-card" role="dialog" aria-modal="true" aria-labelledby="modal-title" initial={{ opacity: 0, y: 12, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }}>
        <div className="modal-heading"><h2 id="modal-title">{title}</h2><button className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={18} /></button></div>
        {children}
      </motion.div>
    </div>
  );
}

function App() {
  const [active, setActive] = useState<Module>("Overview");
  const [darkMode, setDarkMode] = useState(true);
  const [status, setStatus] = useState<PlatformStatus | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusError, setStatusError] = useState("");
  const [farmLoadError, setFarmLoadError] = useState("");
  const [summaryError, setSummaryError] = useState("");
  const [modal, setModal] = useState<"auth" | "sources" | null>(null);
  const [authMode, setAuthMode] = useState<"signin" | "register">("signin");
  const [authenticated, setAuthenticated] = useState(!PORTFOLIO_DEMO && Boolean(sessionStorage.getItem("agrosense_token")));
  const [notice, setNotice] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [query, setQuery] = useState("");
  const [reducedMotion, setReducedMotion] = useState(false);

  const refresh = useCallback(async () => {
    if (PORTFOLIO_DEMO) {
      api.signOut();
      setAuthenticated(false);
      setFarms([]);
      setSummary(null);
      setFarmLoadError("");
      setSummaryError("");
    }
    setLoading(true);
    try {
      setStatusError("");
      try {
        setStatus(await api.status());
      } catch (error) {
        setStatus(null);
        setStatusError(error instanceof Error ? error.message : "Could not reach the backend.");
      }

      if (PORTFOLIO_DEMO || !sessionStorage.getItem("agrosense_token")) {
        setAuthenticated(false);
        setFarms([]);
        setSummary(null);
        setFarmLoadError("");
        setSummaryError("");
        return;
      }

      setAuthenticated(true);
      try {
        setFarms(await api.farms());
        setFarmLoadError("");
      } catch (error) {
        setFarmLoadError(error instanceof Error ? error.message : "Could not load farms.");
        if (error instanceof ApiError && error.status === 401) {
          api.signOut();
          setAuthenticated(false);
          setFarms([]);
          setSummary(null);
          setNotice("Your session expired. Sign in again.");
        }
      }

      if (!sessionStorage.getItem("agrosense_token")) return;
      try {
        setSummary(await api.dashboardSummary());
        setSummaryError("");
      } catch (error) {
        setSummary(null);
        setSummaryError(error instanceof Error ? error.message : "Could not load farm totals.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    setReducedMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, [refresh]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(""), 3800);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const farmLabel = useMemo(() => farms[0]?.name ?? "Select a farm", [farms]);

  function showFarmWorkspace() {
    setActive("Overview");
    window.setTimeout(() => {
      document.getElementById("farm-workspace")?.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }, 0);
  }

  async function submitAuth(event: FormEvent) {
    event.preventDefault();
    try {
      if (authMode === "register") await api.register(email, password);
      await api.signIn(email, password);
      setAuthenticated(true);
      setModal(null);
      await refresh();
      setNotice("Signed in successfully.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Authentication failed.");
    }
  }

  function signOut() {
    api.signOut();
    setAuthenticated(false);
    setFarms([]);
    setSummary(null);
    setFarmLoadError("");
    setSummaryError("");
    setNotice("Signed out.");
  }

  const module = active === "Overview" || active === "Crop catalogue" || active === "Project architecture" || active === "Data sources"
    ? null
    : moduleInfo[active];
  const visibleNavigation = PORTFOLIO_DEMO ? portfolioNavigation : navigation;

  return (
    <div className={`app-shell ${darkMode ? "theme-dark" : "theme-light"}`}>
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); setActive("Overview"); }}>
          <span className="brand-mark"><Sprout size={21} strokeWidth={2.2} /></span>
          <span className="brand-name">AgroSense<span>360</span></span>
        </a>
        <div className="workspace-label">{PORTFOLIO_DEMO ? "PUBLIC DEMO" : "WORKSPACE"}</div>
        {PORTFOLIO_DEMO ? (
          <div className="farm-picker demo-workspace">
            <span className="farm-avatar"><MapPin size={16} /></span>
            <span className="farm-picker-copy"><strong>Kerala, India</strong><small>Read-only portfolio</small></span>
          </div>
        ) : (
          <button className="farm-picker" onClick={showFarmWorkspace}>
            <span className="farm-avatar"><Sprout size={16} /></span>
            <span className="farm-picker-copy"><strong>{farmLabel}</strong><small>{farms.length ? `${farms.length} connected farm${farms.length === 1 ? "" : "s"}` : "No farm connected"}</small></span>
            <ChevronDown size={15} />
          </button>
        )}
        <div className="nav-section-label">{PORTFOLIO_DEMO ? "PROJECT" : "FARM INTELLIGENCE"}</div>
        <nav className="main-nav" aria-label="Main navigation">
          {visibleNavigation.map(({ name, icon: Icon }) => (
            <button key={name} aria-label={name} aria-current={active === name ? "page" : undefined} onClick={() => setActive(name)} className={`nav-item ${active === name ? "active" : ""}`}>
              <Icon size={17} strokeWidth={1.8} /><span>{name}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-tip">
          <div className="tip-icon"><ShieldCheck size={17} /></div>
          <strong>{PORTFOLIO_DEMO ? "Read-only by design" : "Your data, clearly labeled"}</strong>
          <p>{PORTFOLIO_DEMO ? "No public farmer accounts or private farm boundaries." : "Unverified or disconnected insights are never shown as farm results."}</p>
          <button onClick={() => PORTFOLIO_DEMO ? setActive("Data sources") : setModal("sources")}>View data status <ArrowUpRight size={13} /></button>
        </div>
        {!PORTFOLIO_DEMO && <button className="nav-item settings-link" onClick={() => setModal("sources")}><Settings2 size={17} /><span>Data connections</span></button>}
        {PORTFOLIO_DEMO ? (
          <div className="sidebar-profile">
            <div className="profile-avatar"><LockKeyhole size={15} /></div>
            <div className="profile-copy"><strong>Read-only demo</strong><small>Farmer data disabled</small></div>
          </div>
        ) : (
          <div className="sidebar-profile">
            <div className="profile-avatar">{authenticated ? email.slice(0, 1).toUpperCase() : <CircleHelp size={17} />}</div>
            <div className="profile-copy"><strong>{authenticated ? email : "Guest workspace"}</strong><small>{authenticated ? "Farm account" : "Sign in to save farms"}</small></div>
            {authenticated ? <button className="profile-action" onClick={signOut} aria-label="Sign out"><ExternalLink size={15} /></button> : <button className="profile-action" onClick={() => setModal("auth")} aria-label="Sign in"><ArrowUpRight size={15} /></button>}
          </div>
        )}
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>{active}</strong></div>
          <div className="topbar-actions">
            <div className="location-chip"><MapPin size={14} /><span>{PORTFOLIO_DEMO ? "Kerala, India" : farms[0]?.location ?? "Location not set"}</span>{!PORTFOLIO_DEMO && <ChevronDown size={13} />}</div>
            {!PORTFOLIO_DEMO && <button className="icon-button top-search" aria-label="Search" onClick={() => setNotice("Search is available when farm records are connected.")}><Search size={17} /></button>}
            <button className="icon-button" aria-label="Toggle light and dark mode" onClick={() => setDarkMode((value) => !value)}>{darkMode ? <Sun size={17} /> : <Moon size={17} />}</button>
            {!PORTFOLIO_DEMO && <button className="icon-button notification-button" aria-label="Notifications" onClick={() => setNotice("No verified alerts are available yet.")}><Bell size={17} /><i /></button>}
            {!PORTFOLIO_DEMO && <button className="button button-primary top-add" onClick={() => authenticated ? showFarmWorkspace() : setModal("auth")}><Plus size={16} /> Add farm</button>}
            <button className="icon-button mobile-menu" aria-label="Open menu" onClick={() => setNotice("Choose a module from the navigation menu.")}><Menu size={19} /></button>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow"><span className="live-dot" />{PORTFOLIO_DEMO ? "AGROSENSE-360 · PUBLIC PORTFOLIO" : "FARM OPERATIONS"}<span className="heading-date">· {PORTFOLIO_DEMO ? "READ ONLY" : "DATA STATUS"}</span></div>
              <h1>{module?.title ?? (
                active === "Crop catalogue" ? "Kerala crop catalogue"
                  : active === "Project architecture" ? "Project architecture"
                    : active === "Data sources" ? "Data sources & attribution"
                      : PORTFOLIO_DEMO ? "Transparent agriculture intelligence for Kerala"
                        : "Good morning, farmer"
              )}<span className="heading-leaf">✳</span></h1>
              <p>{module?.description ?? (
                active === "Crop catalogue" ? "Explore districts, crops and agricultural profiles with clear source and verification status."
                  : active === "Project architecture" ? "How the current prototype separates public catalogue data from private farm records."
                    : active === "Data sources" ? "Resource-level licensing, provenance and readiness status."
                      : PORTFOLIO_DEMO ? "A read-only portfolio demonstration. No public registration, real farmer records, or model predictions."
                        : "A clear view of your land, conditions and what needs attention."
              )}</p>
            </div>
            <div className="heading-controls">
              <button className="button button-secondary" onClick={() => PORTFOLIO_DEMO ? setActive("Data sources") : setModal("sources")}><Command size={15} /> <span>Data sources</span></button>
              <button className="button button-primary" onClick={() => void refresh()} disabled={loading}><RefreshCw size={15} className={loading ? "spin" : ""} /> {loading ? "Checking" : "Refresh"}</button>
            </div>
          </div>

          {active === "Crop catalogue" ? (
            <CropExplorer />
          ) : active === "Project architecture" ? (
            <ProjectArchitecture />
          ) : active === "Data sources" ? (
            <PortfolioDataSources />
          ) : module ? (
            <section className="module-page glass-card">
              <div className="module-header">
                <div className="module-icon"><module.icon size={20} /></div>
                <div><h2>{module.title}</h2><p>{module.source}</p></div>
                <StatusPill item={status?.integrations[module.statusKey] ?? status?.models[module.statusKey]} />
              </div>
              {active === "Crop health" && (
                <label className="upload-zone">
                  <input type="file" accept="image/*" onChange={() => setNotice("Image inference is unavailable until a validated model is deployed.")} />
                  <FileImage size={24} /><strong>Select a crop image</strong><span>Image analysis stays unavailable until a validated model is deployed.</span>
                </label>
              )}
              {active === "AI copilot" && (
                <form className="copilot-input" onSubmit={(event) => { event.preventDefault(); setNotice("Copilot is unavailable until its grounded knowledge service is configured."); }}>
                  <MessageCircle size={18} />
                  <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask a question about your farm…" aria-label="Ask the agriculture copilot" />
                  <button className="button button-primary" type="submit" disabled={!query.trim()}>Ask copilot</button>
                </form>
              )}
              <EmptyChart label={active === "Weather" ? "weather observations" : active === "Markets" ? "market prices" : active === "Crop health" ? "crop health results" : "farm insights"} />
              <div className="module-note"><LockKeyhole size={15} /><span>Results are withheld until real data and required integrations are available. No demo predictions are used.</span></div>
            </section>
          ) : PORTFOLIO_DEMO ? (
            <PortfolioLanding
              status={status}
              statusError={statusError}
              onBrowseCatalog={() => setActive("Crop catalogue")}
              onOpenArchitecture={() => setActive("Project architecture")}
              onOpenSources={() => setActive("Data sources")}
            />
          ) : (
            <>
              <div className="connection-banner">
                <span className="banner-icon"><Eye size={16} /></span>
                <div>
                  <strong>{status?.api === "online" && status.database === "connected" ? "Workspace connected" : "Workspace connection needs attention"}</strong>
                  <span>{statusError || summaryError || (status?.api === "online"
                    ? `${summary ? `${summary.farm_count} farms · ${summary.plot_count} plots. ` : ""}Add a farm and connect a verified source to see agricultural insights.`
                    : "Backend not detected. Start the API to connect your farm and data sources.")}</span>
                </div>
                <button onClick={() => setModal("sources")}>Check connections <ArrowUpRight size={14} /></button>
              </div>

              <FarmWorkspace
                authenticated={authenticated}
                farms={farms}
                loading={loading && authenticated}
                loadError={farmLoadError}
                onRefresh={refresh}
                onNotice={setNotice}
                onRequestSignIn={() => setModal("auth")}
              />

              <section className="metric-grid" aria-label="Farm metrics">
                <MetricCard title="Soil organic carbon" icon={FlaskConical} detail="Connect satellite + soil model" />
                <MetricCard title="Soil moisture" icon={Droplets} detail="Connect verified field or satellite data" />
                <MetricCard title="Crop health" icon={Leaf} detail="Requires imagery + validated model" />
                <MetricCard title="Yield outlook" icon={TrendingUp} detail="Requires farm history + validated model" />
              </section>

              <div className="dashboard-grid">
                <section className="panel glass-card twin-panel">
                  <div className="panel-heading">
                    <div><div className="panel-title-row"><h2>Farm digital twin</h2><span className="scene-tag">SCHEMATIC</span></div><p>Explore the illustrative plot layout</p></div>
                    <button className="icon-button" aria-label="Farm digital twin information" onClick={() => setNotice("This scene is an illustrative schematic, not real terrain, satellite imagery or soil data.")}><CircleHelp size={16} /></button>
                  </div>
                  <DeferredFarmTwin reducedMotion={reducedMotion} />
                  <div className="twin-legend"><span><i className="legend-green" /> Plot boundary</span><span><i className="legend-yellow" /> Farm marker</span><span className="legend-unavailable">Soil & crop layers unavailable</span></div>
                </section>

                <section className="panel glass-card weather-panel">
                  <div className="panel-heading"><div><h2>Local conditions</h2><p>{farms[0]?.location ?? "Add a farm location for local data"}</p></div><span className="weather-icon"><CloudSun size={21} /></span></div>
                  <div className="weather-empty"><Cloud size={28} /><strong>Forecast unavailable</strong><span>Connect a weather data source and set a farm location to view forecasts.</span></div>
                  <div className="weather-days">
                    {["Today", "Tomorrow", "Day 3"].map((day) => <div key={day}><span>{day}</span><CloudSun size={16} /><b>—</b></div>)}
                  </div>
                  <button className="text-link" onClick={() => setActive("Weather")}>Open weather module <ArrowUpRight size={14} /></button>
                </section>
              </div>

              <div className="dashboard-grid lower-grid">
                <section className="panel glass-card trend-panel">
                  <div className="panel-heading"><div><h2>Field activity</h2><p>Verified observations across your fields</p></div><button className="period-button" onClick={() => setNotice("Date filters become available when field observations are connected.")}>Last 30 days <ChevronDown size={13} /></button></div>
                  <EmptyChart label="field activity" />
                </section>
                <section className="panel glass-card insights-panel">
                  <div className="panel-heading"><div><h2>Farm signals</h2><p>Evidence-backed actions and alerts</p></div><span className="signal-count">0</span></div>
                  <div className="signals-empty"><span className="signals-icon"><Activity size={17} /></span><strong>No verified signals</strong><p>Signals will appear here when connected sources return validated observations.</p></div>
                  <button className="text-link" onClick={() => setActive("Reports")}>View farm reports <ArrowUpRight size={14} /></button>
                </section>
              </div>
            </>
          )}

          <footer className="page-footer"><span>AgroSense-360 <span className="footer-separator">·</span> {PORTFOLIO_DEMO ? "Portfolio demonstration · Read only · not production-ready." : "Decision support, not a substitute for local agronomic advice."}</span><button onClick={() => PORTFOLIO_DEMO ? setActive("Data sources") : setModal("sources")}><ShieldCheck size={13} /> Data transparency</button></footer>
        </div>
      </main>

      <AnimatePresence>
        {!PORTFOLIO_DEMO && modal === "auth" && (
          <Modal title={authMode === "signin" ? "Welcome back" : "Create your account"} onClose={() => setModal(null)}>
            <form className="dialog-form" onSubmit={(event) => void submitAuth(event)}>
              <p className="form-description">Your farm data is private to your account.</p>
              <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
              <label>Password<input type="password" autoComplete={authMode === "signin" ? "current-password" : "new-password"} minLength={10} required value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 10 characters" /></label>
              <button className="button button-primary dialog-submit" type="submit">{authMode === "signin" ? "Sign in" : "Create account"}</button>
              <button className="text-link auth-switch" type="button" onClick={() => setAuthMode(authMode === "signin" ? "register" : "signin")}>{authMode === "signin" ? "New here? Create an account" : "Already have an account? Sign in"}</button>
            </form>
          </Modal>
        )}
        {modal === "sources" && (
          <Modal title="Data connections" onClose={() => setModal(null)}>
            <p className="form-description">Only configured providers and deployed models can supply results. Unavailable integrations are intentionally not simulated.</p>
            <div className="source-list">
              {[
                ["Sentinel-2 imagery", "sentinel_2", "Satellite"],
                ["SoilGrids", "soilgrids", "Soil"],
                ["NASA GPM / ERA5-Land", "weather", "Weather"],
                ["AGMARKNET", "agmarknet", "Markets"],
                ["Soil & yield models", "soil_model", "Models"],
                ["Crop disease model", "disease_model", "Models"],
              ].map(([label, key, kind]) => (
                <div className="source-row" key={key}><span className="source-kind">{kind === "Models" ? <Activity size={15} /> : kind === "Weather" ? <Cloud size={15} /> : <Leaf size={15} />}</span><div><strong>{label}</strong><small>{status?.integrations[key]?.detail ?? status?.models[key]?.detail ?? "API status unavailable. Start the backend to check configuration."}</small></div><StatusPill item={status?.integrations[key] ?? status?.models[key]} /></div>
              ))}
            </div>
            <div className="modal-actions"><button className="button button-secondary" onClick={() => void refresh()}><RefreshCw size={14} /> Recheck status</button><button className="button button-primary" onClick={() => setModal(null)}>Done</button></div>
          </Modal>
        )}
      </AnimatePresence>
      {notice && <div className="toast" role="status">{notice}<button onClick={() => setNotice("")} aria-label="Dismiss notification"><X size={14} /></button></div>}
    </div>
  );
}

export default App;
