import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  ChevronDown,
  CircleHelp,
  Cloud,
  Command,
  Database,
  Eye,
  FlaskConical,
  Gauge,
  Leaf,
  LockKeyhole,
  LogOut,
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
import { api, ApiError, type AdminSummary, type DashboardSummary, type Farm, type PlatformStatus } from "./api";
import AdminWorkspace from "./components/AdminWorkspace";
import FarmWorkspace from "./components/FarmWorkspace";
import CropExplorer from "./components/CropExplorer";
import DataIntelligenceDashboard from "./components/DataIntelligenceDashboard";
import MarketWorkspace from "./components/MarketWorkspace";
import ResearchWorkspace from "./components/ResearchWorkspace";
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

type Module = "Overview" | "Crop catalogue" | "Data intelligence" | "Field intelligence" | "Crop health" | "Markets" | "AI copilot" | "Research assistant" | "Project architecture" | "Data sources" | "Admin";
const PORTFOLIO_DEMO = import.meta.env.VITE_PUBLIC_DEMO === "true";

const navigation: { name: Module; icon: typeof Activity }[] = [
  { name: "Overview", icon: Gauge },
  { name: "Crop catalogue", icon: BookOpen },
  { name: "Data intelligence", icon: Database },
  { name: "Field intelligence", icon: FlaskConical },
  { name: "Crop health", icon: Leaf },
  { name: "Markets", icon: TrendingUp },
  { name: "AI copilot", icon: MessageCircle },
  { name: "Research assistant", icon: BookOpen },
];

const portfolioNavigation: { name: Module; icon: typeof Activity }[] = [
  { name: "Overview", icon: Gauge },
  { name: "Crop catalogue", icon: BookOpen },
  { name: "Data intelligence", icon: Database },
  { name: "Project architecture", icon: Command },
  { name: "Data sources", icon: ShieldCheck },
];

const moduleInfo: Record<Exclude<Module, "Overview" | "Crop catalogue" | "Data intelligence" | "Research assistant" | "Project architecture" | "Data sources" | "Admin">, { title: string; description: string; icon: typeof Activity; source: string; statusKey: string }> = {
  "Field intelligence": {
    title: "Satellite soil intelligence",
    description: "Field-level SOC, pH and NPK insights require connected satellite imagery and a validated model.",
    icon: FlaskConical,
    source: "Sentinel-2 · SoilGrids",
    statusKey: "sentinel_2",
  },
  "Crop health": {
    title: "Crop health & disease",
    description: "Upload an image only when a trained, validated inference model is available.",
    icon: Leaf,
    source: "Computer vision model",
    statusKey: "disease_model",
  },
  Markets: {
    title: "Daily market prices",
    description: "Check source-reported mandi prices by crop and Kerala district.",
    icon: TrendingUp,
    source: "AGMARKNET",
    statusKey: "agmarknet",
  },
  "AI copilot": {
    title: "Agriculture copilot",
    description: "Ask grounded questions about your farm once the retrieval and language-model service is configured.",
    icon: MessageCircle,
    source: "RAG service · regional voice",
    statusKey: "copilot",
  },
};

function MetricCard({ title, icon: Icon, detail, value }: { title: string; icon: typeof Activity; detail: string; value: number | null }) {
  return (
    <article className="metric-card glass-card">
      <div className="metric-heading">
        <span className="metric-icon"><Icon size={17} /></span>
        <span>{title}</span>
      </div>
      <div className={`metric-value ${value === null ? "unavailable-value" : ""}`}>
        {value === null ? <>— <span>Unavailable</span></> : <>{value}<span>{value === 1 ? "record" : "records"}</span></>}
      </div>
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

function authFailureMessage(error: unknown) {
  if (error instanceof ApiError) return error.message;
  return "Could not connect to AgroSense. Check the API connection and try again.";
}

function App() {
  const [active, setActive] = useState<Module>("Overview");
  const [darkMode, setDarkMode] = useState(true);
  const [status, setStatus] = useState<PlatformStatus | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [adminSummary, setAdminSummary] = useState<AdminSummary | null>(null);
  const [adminLoadError, setAdminLoadError] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusError, setStatusError] = useState("");
  const [farmLoadError, setFarmLoadError] = useState("");
  const [summaryError, setSummaryError] = useState("");
  const [modal, setModal] = useState<"sources" | null>(null);
  const [authMode, setAuthMode] = useState<"signin" | "register">("signin");
  const [authenticated, setAuthenticated] = useState(false);
  const [sessionChecking, setSessionChecking] = useState(!PORTFOLIO_DEMO && Boolean(sessionStorage.getItem("agrosense_token")));
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [authError, setAuthError] = useState("");
  const [sessionError, setSessionError] = useState("");
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordChangeRequired, setPasswordChangeRequired] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [reducedMotion, setReducedMotion] = useState(false);

  const refresh = useCallback(async () => {
    const storedToken = sessionStorage.getItem("agrosense_token");
    if (PORTFOLIO_DEMO) {
      api.signOut();
      setAuthenticated(false);
      setFarms([]);
      setSummary(null);
      setAdminSummary(null);
      setAdminLoadError("");
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

      if (PORTFOLIO_DEMO || !storedToken) {
        setAuthenticated(false);
        setFarms([]);
        setSummary(null);
        setAdminSummary(null);
        setAdminLoadError("");
        setFarmLoadError("");
        setSummaryError("");
        setSessionChecking(false);
        return;
      }

      let loadedFarms: Farm[];
      try {
        loadedFarms = await api.farms();
      } catch (error) {
        if (sessionStorage.getItem("agrosense_token") !== storedToken) return;
        setFarmLoadError(error instanceof Error ? error.message : "Could not load farms.");
        if (error instanceof ApiError && error.status === 403 && error.message === "Change your temporary password before using AgroSense.") {
          setAuthenticated(false);
          setPasswordChangeRequired(true);
          setAuthError("");
          setSessionError("");
          return;
        }
        if (error instanceof ApiError && error.status === 401) {
          api.signOut();
          setAuthenticated(false);
          setFarms([]);
          setSummary(null);
          setAuthError("Your session expired. Sign in again.");
        } else {
          setAuthenticated(false);
          setSessionError("Could not verify your saved session. Check the API connection and try again.");
        }
        return;
      }

      if (sessionStorage.getItem("agrosense_token") !== storedToken) return;
      setAuthenticated(true);
      setAuthError("");
      setSessionError("");
      setFarms(loadedFarms);
      setFarmLoadError("");

      try {
        setSummary(await api.dashboardSummary());
        setSummaryError("");
      } catch (error) {
        setSummary(null);
        setSummaryError(error instanceof Error ? error.message : "Could not load farm totals.");
      }
      setAdminSummary(null);
      setAdminLoadError("");
      try {
        setAdminSummary(await api.adminSummary());
      } catch (error) {
        if (!(error instanceof ApiError && error.status === 403)) {
          setAdminLoadError(error instanceof Error ? error.message : "Could not load the admin dashboard.");
        }
      }
    } finally {
      setLoading(false);
      setSessionChecking(false);
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
    setMobileNavOpen(false);
    window.setTimeout(() => {
      document.getElementById("farm-workspace")?.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }, 0);
  }

  function openCatalogueSearch() {
    setActive("Crop catalogue");
    setMobileNavOpen(false);
    window.setTimeout(() => document.getElementById("crop-search")?.focus(), 0);
  }

  async function submitAuth(event: FormEvent) {
    event.preventDefault();
    setAuthError("");
    setAuthSubmitting(true);
    try {
      if (authMode === "register") await api.register(email, password);
      if (await api.signIn(email, password)) {
        setPasswordChangeRequired(true);
        setPassword("");
        return;
      }
      setPasswordChangeRequired(false);
      setAuthMode("signin");
      setAuthenticated(true);
      setSessionChecking(true);
      setActive("Overview");
      await refresh();
      setNotice("Signed in successfully.");
    } catch (error) {
      setAuthError(authFailureMessage(error));
    } finally {
      setAuthSubmitting(false);
    }
  }

  async function submitNewPassword(event: FormEvent) {
    event.preventDefault();
    if (newPassword !== newPasswordConfirm) {
      setAuthError("The new passwords do not match.");
      return;
    }
    setAuthError("");
    setAuthSubmitting(true);
    try {
      await api.changePassword(newPassword);
      setPasswordChangeRequired(false);
      setNewPassword("");
      setNewPasswordConfirm("");
      setAuthenticated(true);
      setSessionChecking(true);
      setActive("Overview");
      await refresh();
      setNotice("Password updated. You are signed in.");
    } catch (error) {
      setAuthError(authFailureMessage(error));
    } finally {
      setAuthSubmitting(false);
    }
  }

  function signOut() {
    api.signOut();
    setMobileNavOpen(false);
    setAuthenticated(false);
    setSessionChecking(false);
    setFarms([]);
    setSummary(null);
    setAdminSummary(null);
    setAdminLoadError("");
    setFarmLoadError("");
    setSummaryError("");
    setPasswordChangeRequired(false);
    setAuthMode("signin");
    setAuthError("");
    setSessionError("");
    setEmail("");
    setPassword("");
    setNewPassword("");
    setNewPasswordConfirm("");
    setActive("Overview");
  }

  const module = active === "Overview" || active === "Crop catalogue" || active === "Data intelligence" || active === "Research assistant" || active === "Project architecture" || active === "Data sources" || active === "Admin"
    ? null
    : moduleInfo[active];
  const visibleNavigation = PORTFOLIO_DEMO
    ? portfolioNavigation
    : adminSummary
      ? [...navigation, { name: "Admin" as const, icon: ShieldCheck }]
      : navigation;

  if (!PORTFOLIO_DEMO && (sessionChecking || !authenticated)) {
    return (
      <div className={`app-shell auth-screen ${darkMode ? "theme-dark" : "theme-light"}`}>
        <main className="auth-card glass-card">
          <div className="auth-brand">
            <span className="brand-mark"><Sprout size={21} strokeWidth={2.2} /></span>
            <span className="brand-name">AgroSense<span>360</span></span>
          </div>
          {sessionChecking ? (
            <p className="auth-loading" role="status">Checking your saved session…</p>
          ) : (
            <>
              <div className="auth-page-heading">
                <span className="eyebrow">FARMER WORKSPACE</span>
                <h1>{passwordChangeRequired ? "Set a new password" : authMode === "signin" ? "Welcome to AgroSense" : "Create your farmer account"}</h1>
                <p>{passwordChangeRequired ? "Choose a new password before accessing your farm data." : "Sign in to securely view and manage your farms and plots."}</p>
              </div>
              {passwordChangeRequired ? (
                <form className="dialog-form auth-page-form" onSubmit={(event) => void submitNewPassword(event)}>
                  <label>New password<input type="password" autoComplete="new-password" minLength={10} required value={newPassword} onChange={(event) => setNewPassword(event.target.value)} placeholder="At least 10 characters" /></label>
                  <label>Confirm new password<input type="password" autoComplete="new-password" minLength={10} required value={newPasswordConfirm} onChange={(event) => setNewPasswordConfirm(event.target.value)} placeholder="Enter the new password again" /></label>
                  {authError && <p className="auth-error" role="alert">{authError}</p>}
                  <button className="button button-primary auth-submit" type="submit" disabled={authSubmitting}>{authSubmitting ? "Updating password…" : "Update password"}</button>
                </form>
              ) : (
                <form className="dialog-form auth-page-form" onSubmit={(event) => void submitAuth(event)}>
                  <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
                  <label>Password<input type="password" autoComplete={authMode === "signin" ? "current-password" : "new-password"} minLength={10} required value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 10 characters" /></label>
                  {(authError || sessionError) && <p className="auth-error" role="alert">{authError || sessionError}</p>}
                  {sessionError && <button className="text-link auth-retry" type="button" onClick={() => { setSessionError(""); setSessionChecking(true); void refresh(); }} disabled={loading}>Retry saved session</button>}
                  <button className="button button-primary auth-submit" type="submit" disabled={authSubmitting}>{authSubmitting ? "Please wait…" : authMode === "signin" ? "Sign in" : "Create account"}</button>
                  <button className="text-link auth-switch" type="button" onClick={() => { setAuthMode(authMode === "signin" ? "register" : "signin"); setAuthError(""); setPassword(""); }}>{authMode === "signin" ? "New here? Create an account" : "Already have an account? Sign in"}</button>
                </form>
              )}
            </>
          )}
        </main>
      </div>
    );
  }

  return (
    <div className={`app-shell ${darkMode ? "theme-dark" : "theme-light"} ${mobileNavOpen ? "mobile-nav-open" : ""}`}>
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); setActive("Overview"); setMobileNavOpen(false); }}>
          <span className="brand-mark"><Sprout size={21} strokeWidth={2.2} /></span>
          <span className="brand-name">AgroSense<span>360</span></span>
        </a>
        <div className="workspace-label">{PORTFOLIO_DEMO ? "LOCAL PREVIEW" : "WORKSPACE"}</div>
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
        <nav id="main-nav" className="main-nav" aria-label="Main navigation">
          {visibleNavigation.map(({ name, icon: Icon }) => (
            <button key={name} aria-label={name} aria-current={active === name ? "page" : undefined} onClick={() => { setActive(name); setMobileNavOpen(false); }} className={`nav-item ${active === name ? "active" : ""}`}>
              <Icon size={17} strokeWidth={1.8} /><span>{name}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-tip">
          <div className="tip-icon"><ShieldCheck size={17} /></div>
          <strong>{PORTFOLIO_DEMO ? "Technical preview only" : "Your data, clearly labeled"}</strong>
          <p>{PORTFOLIO_DEMO ? "Read-only capability does not authorize public use or data release." : "Unverified or disconnected insights are never shown as farm results."}</p>
          <button onClick={() => PORTFOLIO_DEMO ? setActive("Data sources") : setModal("sources")}>View data status <ArrowUpRight size={13} /></button>
        </div>
        {!PORTFOLIO_DEMO && <button className="nav-item settings-link" onClick={() => { setMobileNavOpen(false); setModal("sources"); }}><Settings2 size={17} /><span>Data connections</span></button>}
        {PORTFOLIO_DEMO ? (
          <div className="sidebar-profile">
            <div className="profile-avatar"><LockKeyhole size={15} /></div>
            <div className="profile-copy"><strong>Local preview</strong><small>Public use not authorized</small></div>
          </div>
        ) : (
          <div className="sidebar-profile">
            <div className="profile-avatar">{authenticated ? email.slice(0, 1).toUpperCase() : <CircleHelp size={17} />}</div>
            <div className="profile-copy"><strong>{authenticated ? email : "Guest workspace"}</strong><small>{authenticated ? "Farm account" : "Sign in to save farms"}</small></div>
          </div>
        )}
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>{active}</strong></div>
          <div className="topbar-actions">
            <div className="location-chip"><MapPin size={14} /><span>{PORTFOLIO_DEMO ? "Kerala, India" : farms[0]?.location ?? "Location not set"}</span>{!PORTFOLIO_DEMO && <ChevronDown size={13} />}</div>
            {!PORTFOLIO_DEMO && <button className="icon-button top-search" aria-label="Search crop catalogue" onClick={openCatalogueSearch}><Search size={17} /></button>}
            <button className="icon-button" aria-label="Toggle light and dark mode" onClick={() => setDarkMode((value) => !value)}>{darkMode ? <Sun size={17} /> : <Moon size={17} />}</button>
            {!PORTFOLIO_DEMO && authenticated && <button className="button button-secondary top-logout" onClick={signOut}><LogOut size={15} /><span>Log out</span></button>}
            {!PORTFOLIO_DEMO && <button className="button button-primary top-add" onClick={showFarmWorkspace}><Plus size={16} /> Add plot</button>}
            <button className="icon-button mobile-menu" aria-label={mobileNavOpen ? "Close menu" : "Open menu"} aria-expanded={mobileNavOpen} aria-controls="main-nav" onClick={() => setMobileNavOpen((open) => !open)}>{mobileNavOpen ? <X size={19} /> : <Menu size={19} />}</button>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow"><span className="live-dot" />{PORTFOLIO_DEMO ? "AGROSENSE-360 · PROPOSED LOCAL PREVIEW" : "FARM OPERATIONS"}<span className="heading-date">· {PORTFOLIO_DEMO ? "NOT AUTHORIZED FOR PUBLIC USE" : "DATA STATUS"}</span></div>
              <h1>{module?.title ?? (
                active === "Crop catalogue" ? "Kerala crop catalogue"
                  : active === "Data intelligence" ? "Agricultural data intelligence"
                  : active === "Project architecture" ? "Project architecture"
                    : active === "Data sources" ? "Data sources & attribution"
                      : active === "Admin" ? "Admin dashboard"
                      : PORTFOLIO_DEMO ? "Transparent agriculture intelligence for Kerala"
                        : "Good morning, farmer"
              )}<span className="heading-leaf">✳</span></h1>
              <p>{module?.description ?? (
                active === "Crop catalogue" ? "Explore districts, crops and agricultural profiles with clear source and verification status."
                  : active === "Data intelligence" ? "Inspect registered sources, data quality, catalogue coverage and training eligibility from verified project metadata."
                  : active === "Project architecture" ? "How the current prototype separates public catalogue data from private farm records."
                    : active === "Data sources" ? "Resource-level licensing, provenance and readiness status."
                      : active === "Admin" ? "Review account totals, source connections and evidence verification status."
                      : PORTFOLIO_DEMO ? "A proposed local technical preview. Public demonstration, data distribution, and deployment are not authorized."
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
          ) : active === "Data intelligence" ? (
            <DataIntelligenceDashboard />
          ) : active === "Project architecture" ? (
            <ProjectArchitecture />
          ) : active === "Data sources" ? (
            <PortfolioDataSources />
          ) : active === "Research assistant" ? (
            <ResearchWorkspace authenticated={authenticated} />
          ) : active === "Markets" ? (
            <section className="module-page glass-card">
              <div className="module-header">
                <div className="module-icon"><TrendingUp size={20} /></div>
                <div><h2>Daily market prices</h2><p>AGMARKNET via data.gov.in · market-reported values, not real-time quotes</p></div>
                <StatusPill item={status?.integrations.agmarknet} />
              </div>
              <MarketWorkspace authenticated={authenticated} onRequestSignIn={signOut} />
            </section>
          ) : active === "Admin" ? (
            <AdminWorkspace
              summary={adminSummary}
              status={status}
              error={adminLoadError}
              onOpenCatalogue={() => setActive("Crop catalogue")}
              onOpenDataIntelligence={() => setActive("Data intelligence")}
            />
          ) : module ? (
            <section className="module-page glass-card">
              <div className="module-header">
                <div className="module-icon"><module.icon size={20} /></div>
                <div><h2>{module.title}</h2><p>{module.source}</p></div>
                <StatusPill item={status?.integrations[module.statusKey] ?? status?.models[module.statusKey]} />
              </div>
              {active === "Crop health" && (
                <div className="module-note" role="note"><LockKeyhole size={15} /><span>Image upload is disabled until a validated model and authorized image data are available.</span></div>
              )}
              {active === "AI copilot" && (
                <div className="module-note" role="note"><LockKeyhole size={15} /><span>Copilot questions are disabled until its grounded knowledge service and verified sources are configured.</span></div>
              )}
              <EmptyChart label={active === "Crop health" ? "crop health results" : "farm insights"} />
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
                    ? `${summary ? `${summary.farm_count} farms · ${summary.plot_count} plots. ` : ""}Add a plot to see its saved crop, location and available weather.`
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
                onRequestSignIn={signOut}
              />

              <section className="metric-grid" aria-label="Farm metrics">
                <MetricCard title="Saved farms" icon={Sprout} value={authenticated ? summary?.farm_count ?? null : null} detail={authenticated ? summary ? "Private farm records in your account." : loading ? "Loading your farm summary…" : summaryError || "Farm count unavailable." : "Sign in to load your private farm records."} />
                <MetricCard title="Recorded plots" icon={MapPin} value={authenticated ? summary?.plot_count ?? null : null} detail={authenticated ? summary ? "Plots saved in your account." : loading ? "Loading your plot summary…" : summaryError || "Plot count unavailable." : "Sign in to load your private plot records."} />
                <MetricCard title="Validated crop predictions" icon={TrendingUp} value={null} detail={status?.models.soil_model?.detail ?? "No validated crop prediction model is deployed."} />
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

              </div>

              <div className="dashboard-grid lower-grid">
                <section className="panel glass-card trend-panel">
                  <div className="panel-heading"><div><h2>Field activity</h2><p>Verified observations across your fields</p></div><span className="period-button">No observation series</span></div>
                  <EmptyChart label="field activity" />
                </section>
                <section className="panel glass-card insights-panel">
                  <div className="panel-heading"><div><h2>Farm signals</h2><p>Evidence-backed actions and alerts</p></div><span className="signal-count">—</span></div>
                  <div className="signals-empty"><span className="signals-icon"><Activity size={17} /></span><strong>No verified signals</strong><p>Signals will appear here when connected sources return validated observations.</p></div>
                  <button className="text-link" onClick={() => setActive("Data intelligence")}>View data status <ArrowUpRight size={14} /></button>
                </section>
              </div>
            </>
          )}

          <footer className="page-footer"><span>AgroSense-360 <span className="footer-separator">·</span> {PORTFOLIO_DEMO ? "Proposed local technical preview · public use not authorized." : "Decision support, not a substitute for local agronomic advice."}</span><button onClick={() => PORTFOLIO_DEMO ? setActive("Data sources") : setModal("sources")}><ShieldCheck size={13} /> Data transparency</button></footer>
        </div>
      </main>

      {mobileNavOpen && <button className="mobile-nav-backdrop" type="button" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}

      <AnimatePresence>
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
