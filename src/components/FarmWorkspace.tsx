import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Activity, CloudSun, MapPin, Pencil, Sprout, Trash2, TrendingUp } from "lucide-react";
import { api, ApiError, type Crop, type CropProfile, type Farm, type Plot, type WeatherResponse } from "../api";
import GeoBoundaryMap from "./GeoBoundaryMap";
import MarketWorkspace from "./MarketWorkspace";

type Props = {
  authenticated: boolean;
  farms: Farm[];
  loading: boolean;
  loadError: string;
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onRequestSignIn: () => void;
};

type FarmDraft = { id: string | null; name: string; location: string };
type PlotDraft = {
  id: string | null;
  cropId: string;
  areaValue: string;
  areaUnit: "acres" | "hectares";
  latitude: number | null;
  longitude: number | null;
};
type SelectedWeather = {
  title: string;
  provider: string;
  attribution: string;
  sourceUrl: string;
  timestamp: string;
  values: Record<string, number | null>;
  units: Record<string, string>;
  kind: "historical" | "forecast";
};

const emptyFarmDraft: FarmDraft = { id: null, name: "", location: "" };
const emptyPlotDraft: PlotDraft = {
  id: null,
  cropId: "",
  areaValue: "",
  areaUnit: "acres",
  latitude: null,
  longitude: null,
};

function weatherFacts(
  values: Record<string, number | null>,
  units: Record<string, string>,
  keys: { temperature: string; rainfall: string; humidity: string; wind: string },
) {
  return [
    { label: "Temperature", value: values[keys.temperature], unit: units[keys.temperature] },
    { label: "Rainfall", value: values[keys.rainfall], unit: units[keys.rainfall] },
    { label: "Humidity", value: values[keys.humidity], unit: units[keys.humidity] },
    { label: "Wind", value: values[keys.wind], unit: units[keys.wind] },
  ];
}

function formatUtcTimestamp(value: string) {
  const timestamp = new Date(value.endsWith("Z") ? value : `${value}Z`);
  return Number.isNaN(timestamp.getTime())
    ? value
    : `${timestamp.toISOString().slice(0, 16).replace("T", " ")} UTC`;
}

function WeatherFacts({ facts }: { facts: ReturnType<typeof weatherFacts> }) {
  return (
    <dl className="plot-weather-facts">
      {facts.map(({ label, value, unit }) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value === null || value === undefined ? "Not available" : `${value.toFixed(1)}${unit ? ` ${unit}` : ""}`}</dd>
        </div>
      ))}
    </dl>
  );
}

function PlotDashboardCard({
  plot,
  onEdit,
  onDelete,
}: {
  plot: Plot;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const [current, setCurrent] = useState<Awaited<ReturnType<typeof api.currentWeather>> | null>(null);
  const [currentError, setCurrentError] = useState("");
  const [currentLoading, setCurrentLoading] = useState(false);
  const [currentRevision, setCurrentRevision] = useState(0);
  const [forecast, setForecast] = useState<WeatherResponse | null>(null);
  const [forecastError, setForecastError] = useState("");
  const [forecastLoading, setForecastLoading] = useState(false);
  const [profile, setProfile] = useState<CropProfile | null>(null);
  const [profileError, setProfileError] = useState("");
  const [profileLoading, setProfileLoading] = useState(false);
  const [selectedDateTime, setSelectedDateTime] = useState("");
  const [selectedWeather, setSelectedWeather] = useState<SelectedWeather | null>(null);
  const [selectedError, setSelectedError] = useState("");
  const [selectedLoading, setSelectedLoading] = useState(false);
  const hasLocation = plot.latitude !== null && plot.longitude !== null;

  useEffect(() => {
    let active = true;
    setCurrent(null);
    setCurrentError("");
    if (!hasLocation) return () => { active = false; };
    setCurrentLoading(true);
    void api.currentWeather(plot.latitude!, plot.longitude!).then((result) => {
      if (active) setCurrent(result);
    }).catch((error: unknown) => {
      if (active) setCurrentError(error instanceof Error ? error.message : "Current weather is unavailable.");
    }).finally(() => {
      if (active) setCurrentLoading(false);
    });
    return () => { active = false; };
  }, [hasLocation, plot.id, plot.latitude, plot.longitude, currentRevision]);

  useEffect(() => {
    let active = true;
    setProfile(null);
    setProfileError("");
    if (!plot.crop_id) {
      setProfileLoading(false);
      return () => { active = false; };
    }
    setProfileLoading(true);
    void api.cropProfile(plot.crop_id).then((result) => {
      if (active) setProfile(result);
    }).catch((error: unknown) => {
      if (active) setProfileError(error instanceof Error ? error.message : "Crop information is unavailable.");
    }).finally(() => {
      if (active) setProfileLoading(false);
    });
    return () => { active = false; };
  }, [plot.crop_id]);

  async function loadForecast() {
    if (!hasLocation) return;
    setForecastLoading(true);
    setForecastError("");
    setForecast(null);
    try {
      setForecast(await api.weatherForecast(plot.latitude!, plot.longitude!));
    } catch (error) {
      setForecastError(error instanceof Error ? error.message : "The forecast is unavailable.");
    } finally {
      setForecastLoading(false);
    }
  }

  async function loadSelectedWeather() {
    if (!hasLocation || !selectedDateTime) {
      setSelectedError("Choose a date and time to check supported weather data.");
      return;
    }
    const requested = new Date(selectedDateTime);
    if (!Number.isFinite(requested.getTime())) {
      setSelectedError("Choose a valid date and time.");
      return;
    }
    setSelectedLoading(true);
    setSelectedError("");
    setSelectedWeather(null);
    try {
      const now = new Date();
      const date = selectedDateTime.slice(0, 10);
      if (requested > now) {
        if (requested.getTime() > now.getTime() + 7 * 24 * 60 * 60 * 1000) {
          throw new Error("Forecast data is available only for the next seven days.");
        }
        const result = await api.weatherForecast(plot.latitude!, plot.longitude!);
        const target = requested.getTime();
        const record = result.records.reduce<WeatherResponse["records"][number] | null>((nearest, item) => {
          const itemTimestamp = item.timestamp.endsWith("Z") ? item.timestamp : `${item.timestamp}Z`;
          if (!nearest) return item;
          const nearestTimestamp = nearest.timestamp.endsWith("Z") ? nearest.timestamp : `${nearest.timestamp}Z`;
          return Math.abs(Date.parse(itemTimestamp) - target) < Math.abs(Date.parse(nearestTimestamp) - target)
            ? item
            : nearest;
        }, null);
        if (!record || Math.abs(Date.parse(`${record.timestamp.replace(/Z$/, "")}Z`) - target) > 60 * 60 * 1000) {
          throw new Error("The provider has no forecast close to that selected time.");
        }
        setSelectedWeather({
          title: "Forecast model estimate",
          provider: result.provider,
          attribution: result.attribution,
          sourceUrl: result.source_url,
          timestamp: record.timestamp,
          values: record.values,
          units: result.units,
          kind: "forecast",
        });
        return;
      }

      const latestHistoricalDate = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
      if (date > latestHistoricalDate) {
        throw new Error("Historical daily estimates are available through two days ago; forecast times are available up to seven days ahead.");
      }
      const result = await api.historicalWeather(plot.latitude!, plot.longitude!, date, date);
      const record = result.records.find((item) => item.timestamp.slice(0, 10) === date);
      if (!record) throw new Error("No historical estimate is available for that date.");
      setSelectedWeather({
        title: "Historical daily estimate",
        provider: result.provider,
        attribution: result.attribution,
        sourceUrl: result.source_url,
        timestamp: record.timestamp,
        values: record.values,
        units: result.units,
        kind: "historical",
      });
    } catch (error) {
      setSelectedError(error instanceof Error ? error.message : "Weather data could not be loaded.");
    } finally {
      setSelectedLoading(false);
    }
  }

  const verifiedProfile = profile?.verification_status === "verified" && profile.sources.length > 0;
  const recommendationFacts = verifiedProfile
    ? [
      ["Cultivation", profile.cultivation_practices],
      ["Watering", profile.irrigation_requirements],
      ["Fertilizer", profile.fertilizer_recommendations],
    ].filter((item): item is [string, string] => Boolean(item[1]?.trim()))
    : [];

  return (
    <article className="plot-dashboard-card glass-card">
      <header className="plot-dashboard-heading">
        <span className="plot-dashboard-icon"><Sprout size={18} /></span>
        <div>
          <h3>{plot.crop || "Crop not selected"}</h3>
          <p>{plot.area_value !== null && plot.area_unit ? `${plot.area_value} ${plot.area_unit}` : "Plot area not recorded"} · {plot.name}</p>
        </div>
        <div className="plot-card-actions">
          <button type="button" className="icon-button" aria-label={`Edit ${plot.name}`} onClick={onEdit}><Pencil size={14} /></button>
          <button type="button" className="icon-button" aria-label={`Delete ${plot.name}`} onClick={onDelete}><Trash2 size={14} /></button>
        </div>
      </header>

      <section className="plot-card-section" aria-label={`Weather for ${plot.name}`}>
        <div className="plot-card-section-heading"><h4><CloudSun size={15} /> Current conditions</h4><span>Model estimate</span></div>
        {currentLoading && <p className="plot-dashboard-state" role="status">Loading weather for this plot…</p>}
        {!hasLocation && <p className="plot-dashboard-state">Add a saved plot location to check weather automatically.</p>}
        {currentError && <p className="plot-dashboard-error" role="alert">{currentError}</p>}
        {currentError && (
          <button type="button" className="text-link plot-weather-retry" onClick={() => setCurrentRevision((revision) => revision + 1)}>
            Retry current weather
          </button>
        )}
        {current && (
          <>
            <WeatherFacts facts={weatherFacts(current.values, current.units, {
              temperature: "temperature_2m",
              rainfall: "precipitation",
              humidity: "relative_humidity_2m",
              wind: "wind_speed_10m",
            })} />
            <p className="plot-weather-source">
              {current.provider} · Data time {formatUtcTimestamp(current.timestamp)}
              {" · Fetched "}{formatUtcTimestamp(current.requested_at)}
              {" · "}<a href={current.source_url} target="_blank" rel="noreferrer">Source</a>
            </p>
            <p className="plot-weather-attribution">{current.attribution}</p>
          </>
        )}
        {hasLocation && (
          <button
            type="button"
            className="button button-secondary plot-forecast-button"
            onClick={() => void loadForecast()}
            disabled={forecastLoading}
          >
            <CloudSun size={14} /> {forecastLoading ? "Loading 7-day forecast…" : forecast ? "Refresh 7-day forecast" : "Show 7-day forecast"}
          </button>
        )}
        {forecastError && (
          <div className="plot-dashboard-error" role="alert">
            {forecastError} <button type="button" className="text-link" onClick={() => void loadForecast()} disabled={forecastLoading}>Retry</button>
          </div>
        )}
        {forecast && (
          <div className="plot-forecast">
            <strong>7-day forecast · model estimates</strong>
            <div className="plot-forecast-grid">
              {(forecast.daily_records ?? []).map((day) => (
                <article key={day.date}>
                  <strong>{new Intl.DateTimeFormat("en", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" }).format(new Date(`${day.date}T00:00:00Z`))}</strong>
                  <span>{day.values.temperature_2m_min?.toFixed(0) ?? "—"}° / {day.values.temperature_2m_max?.toFixed(0) ?? "—"}°C</span>
                  <span>Rain {day.values.precipitation_sum?.toFixed(1) ?? "—"} mm</span>
                  <span>Wind {day.values.wind_speed_10m_max?.toFixed(1) ?? "—"} km/h</span>
                </article>
              ))}
            </div>
            <p className="plot-weather-source">
              {forecast.provider} · Updated {formatUtcTimestamp(forecast.requested_at)} · {forecast.timezone ?? "UTC"}
              {" · "}<a href={forecast.source_url} target="_blank" rel="noreferrer">Source</a>
            </p>
            <p className="plot-weather-attribution">{forecast.attribution}</p>
          </div>
        )}
      </section>

      <details className="plot-time-weather">
        <summary>Weather for another date and time</summary>
        <div className="plot-time-weather-controls">
          <label>
            Date and time
            <input type="datetime-local" value={selectedDateTime} onChange={(event) => setSelectedDateTime(event.target.value)} />
          </label>
          <button type="button" className="button button-secondary" onClick={() => void loadSelectedWeather()} disabled={!hasLocation || selectedLoading}>
            {selectedLoading ? "Checking…" : "Check weather"}
          </button>
        </div>
        <p className="plot-weather-attribution">Choose time in your device’s local timezone; provider update times are shown in UTC.</p>
        {selectedError && <p className="plot-dashboard-error" role="alert">{selectedError}</p>}
        {selectedWeather && (
          <div className="plot-selected-weather">
            <strong>{selectedWeather.title}</strong>
            <WeatherFacts facts={weatherFacts(selectedWeather.values, selectedWeather.units, selectedWeather.kind === "forecast"
              ? { temperature: "temperature_2m", rainfall: "precipitation", humidity: "relative_humidity_2m", wind: "wind_speed_10m" }
              : { temperature: "T2M", rainfall: "PRECTOTCORR", humidity: "RH2M", wind: "WS2M" })} />
            <p className="plot-weather-source">
              {selectedWeather.provider} · {formatUtcTimestamp(selectedWeather.timestamp)}
              {" · "}<a href={selectedWeather.sourceUrl} target="_blank" rel="noreferrer">Source</a>
            </p>
            <p className="plot-weather-attribution">{selectedWeather.attribution}</p>
            {selectedWeather.kind === "historical" && <p className="plot-weather-attribution">Historical values are daily gridded estimates; the provider does not supply an hourly past observation.</p>}
          </div>
        )}
      </details>

      <section className="plot-card-section">
        <div className="plot-card-section-heading"><h4><TrendingUp size={15} /> Daily market prices</h4></div>
        <MarketWorkspace authenticated fixedCommodity={plot.crop ?? ""} compact />
      </section>

      <section className="plot-card-section">
        <div className="plot-card-section-heading"><h4><Activity size={15} /> Crop information</h4></div>
        <p className="plot-dashboard-state">Crop health is not assessed; no verified plot-level health evidence is available.</p>
        {profileLoading && <p className="plot-dashboard-state" role="status">Checking verified crop information…</p>}
        {profileError && <p className="plot-dashboard-error" role="alert">{profileError} No recommendations are displayed.</p>}
        {!profileLoading && !profileError && recommendationFacts.length > 0 ? (
          <>
            <dl className="plot-recommendations">
              {recommendationFacts.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}
            </dl>
            <p className="plot-weather-source">
              Verified catalogue information · updated {new Date(profile!.last_updated_at).toLocaleDateString()}
              {profile!.sources.map((source) => <a key={source.id} href={source.url} target="_blank" rel="noreferrer"> · {source.title}</a>)}
            </p>
          </>
        ) : !profileLoading && !profileError ? (
          <p className="plot-dashboard-state">
            {verifiedProfile ? "No recommendations are recorded for this crop." : "No verified crop recommendations are available."}
          </p>
        ) : null}
      </section>
    </article>
  );
}

export default function FarmWorkspace({
  authenticated,
  farms,
  loading,
  loadError,
  onRefresh,
  onNotice,
  onRequestSignIn,
}: Props) {
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const [selectedPlotId, setSelectedPlotId] = useState<string | null>(null);
  const [plots, setPlots] = useState<Plot[]>([]);
  const [plotsLoading, setPlotsLoading] = useState(false);
  const [plotsError, setPlotsError] = useState("");
  const [plotRevision, setPlotRevision] = useState(0);
  const [farmDraft, setFarmDraft] = useState<FarmDraft | null>(null);
  const [plotDraft, setPlotDraft] = useState<PlotDraft | null>(null);
  const [actionError, setActionError] = useState("");
  const [cropLoadError, setCropLoadError] = useState("");
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropsLoading, setCropsLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);

  const selectedFarm = useMemo(
    () => farms.find((farm) => farm.id === selectedFarmId) ?? farms[0] ?? null,
    [farms, selectedFarmId],
  );

  useEffect(() => {
    if (selectedFarm?.id !== selectedFarmId) setSelectedFarmId(selectedFarm?.id ?? null);
  }, [selectedFarm, selectedFarmId]);

  useEffect(() => {
    if (!authenticated) {
      setCrops([]);
      setCropsLoading(false);
      return;
    }
    let active = true;
    setCropLoadError("");
    setCropsLoading(true);
    void api.crops({ limit: 100 }).then((page) => {
      if (active) setCrops(page.items);
    }).catch((error: unknown) => {
      if (active) setCropLoadError(error instanceof Error ? error.message : "The crop catalogue could not be loaded.");
    }).finally(() => {
      if (active) setCropsLoading(false);
    });
    return () => { active = false; };
  }, [authenticated]);

  useEffect(() => {
    setPlotsError("");
    if (!authenticated || !selectedFarm) {
      setPlots([]);
      setPlotsLoading(false);
      return;
    }
    let active = true;
    setPlotsLoading(true);
    void api.plots(selectedFarm.id).then((result) => {
      if (active) setPlots(result);
    }).catch((error: unknown) => {
      if (!active) return;
      setPlots([]);
      setPlotsError(error instanceof Error ? error.message : "Could not load plots.");
      if (error instanceof ApiError && error.status === 401) void onRefresh();
    }).finally(() => {
      if (active) setPlotsLoading(false);
    });
    return () => { active = false; };
  }, [authenticated, onRefresh, selectedFarm, plotRevision]);

  const reloadPlots = useCallback(() => setPlotRevision((revision) => revision + 1), []);

  function beginFarmForm(farm?: Farm) {
    setActionError("");
    setFarmDraft(farm
      ? { id: farm.id, name: farm.name, location: farm.location ?? "" }
      : { ...emptyFarmDraft });
    setPlotDraft(null);
  }

  function beginPlotForm(plot?: Plot) {
    setActionError("");
    setPlotDraft(plot
      ? {
        id: plot.id,
        cropId: plot.crop_id ?? crops.find((crop) => crop.common_name.toLowerCase() === plot.crop?.toLowerCase())?.id ?? "",
        areaValue: plot.area_value === null ? "" : String(plot.area_value),
        areaUnit: plot.area_unit ?? "acres",
        latitude: plot.latitude,
        longitude: plot.longitude,
      }
      : { ...emptyPlotDraft });
    setFarmDraft(null);
  }

  function reportActionError(error: unknown, fallback: string) {
    setActionError(error instanceof Error ? error.message : fallback);
    if (error instanceof ApiError && error.status === 401) void onRefresh();
  }

  async function submitFarm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!farmDraft) return;
    setSaving(true);
    setActionError("");
    try {
      const name = farmDraft.name.trim();
      const location = farmDraft.location.trim();
      if (farmDraft.id) {
        await api.updateFarm(farmDraft.id, { name, location: location || null });
      } else {
        const created = await api.createFarm(name, location);
        setSelectedFarmId(created.id);
      }
      setFarmDraft(null);
      await onRefresh();
      onNotice(farmDraft.id ? "Farm updated." : "Farm created.");
    } catch (error) {
      reportActionError(error, "Could not save farm.");
    } finally {
      setSaving(false);
    }
  }

  async function submitPlot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!plotDraft) return;
    if (!plotDraft.cropId || !Number.isFinite(Number(plotDraft.areaValue)) || Number(plotDraft.areaValue) <= 0) {
      setActionError("Choose a crop and enter a valid plot area.");
      return;
    }
    if (plotDraft.latitude === null || plotDraft.longitude === null) {
      setActionError("Select the plot location before saving.");
      return;
    }
    setSaving(true);
    setActionError("");
    try {
      let farm = selectedFarm;
      if (!farm) farm = await api.createFarm("My farm", "");
      const changes = {
        crop_id: plotDraft.cropId,
        area_value: Number(plotDraft.areaValue),
        area_unit: plotDraft.areaUnit,
        latitude: plotDraft.latitude,
        longitude: plotDraft.longitude,
      };
      if (plotDraft.id) {
        await api.updatePlot(farm.id, plotDraft.id, changes);
      } else {
        await api.createPlot(farm.id, changes);
        setSelectedFarmId(farm.id);
      }
      setPlotDraft(null);
      if (!selectedFarm) await onRefresh();
      reloadPlots();
      onNotice(plotDraft.id ? "Plot updated." : "Plot saved.");
    } catch (error) {
      reportActionError(error, "Could not save plot.");
    } finally {
      setSaving(false);
    }
  }

  function chooseLocation() {
    if (!navigator.geolocation) {
      setActionError("Location selection is not supported by this browser.");
      return;
    }
    setLocationLoading(true);
    setActionError("");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setPlotDraft((draft) => draft
          ? { ...draft, latitude: position.coords.latitude, longitude: position.coords.longitude }
          : draft);
        setLocationLoading(false);
      },
      (error) => {
        setActionError(error.code === error.PERMISSION_DENIED
          ? "Allow location access in your browser to select this plot."
          : "The plot location could not be read. Try again near the plot.");
        setLocationLoading(false);
      },
      { enableHighAccuracy: true, timeout: 15_000 },
    );
  }

  async function deletePlot(plot: Plot) {
    if (!selectedFarm || !window.confirm(`Delete "${plot.name}"? This cannot be undone.`)) return;
    setActionError("");
    setSaving(true);
    try {
      await api.deletePlot(selectedFarm.id, plot.id);
      reloadPlots();
      onNotice("Plot deleted.");
    } catch (error) {
      reportActionError(error, "Could not delete plot.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteFarm(farm: Farm) {
    if (!window.confirm(`Delete "${farm.name}" and all of its plots? This cannot be undone.`)) return;
    setActionError("");
    setSaving(true);
    try {
      await api.deleteFarm(farm.id);
      setSelectedFarmId(null);
      await onRefresh();
      onNotice("Farm and its plots deleted.");
    } catch (error) {
      reportActionError(error, "Could not delete farm.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="farm-workspace panel glass-card" id="farm-workspace" aria-labelledby="farm-workspace-title">
      <div className="panel-heading">
        <div>
          <h2 id="farm-workspace-title">My plots</h2>
          <p>Add a crop, area and saved location to see plot-specific information.</p>
        </div>
        {authenticated && (
          <div className="farm-workspace-actions">
            <button className="button button-secondary" type="button" onClick={() => beginFarmForm()}>
              Add another farm
            </button>
            <button className="button button-primary" type="button" onClick={() => beginPlotForm()}>
              Add plot
            </button>
          </div>
        )}
      </div>

      {!authenticated ? (
        <div className="workspace-empty">
          <strong>Sign in to manage your plots</strong>
          <span>Your farm and plot records are private to your account.</span>
          <button className="button button-secondary" type="button" onClick={onRequestSignIn}>Sign in</button>
        </div>
      ) : (
        <>
          {loadError && <div className="workspace-error" role="alert">{loadError}</div>}
          {actionError && <div className="workspace-error" role="alert">{actionError}</div>}
          {cropLoadError && <div className="workspace-error" role="alert">{cropLoadError}</div>}
          {loading && <p className="workspace-state" role="status">Loading your farms…</p>}
          {farms.length > 0 && (
            <div className="farm-records farm-records-compact">
              <label className="farm-select-label" htmlFor="farm-select">Farm</label>
              <select id="farm-select" value={selectedFarm?.id ?? ""} onChange={(event) => setSelectedFarmId(event.target.value)} disabled={saving}>
                {farms.map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}
              </select>
              {selectedFarm?.location && <span className="farm-location-label"><MapPin size={13} /> {selectedFarm.location}</span>}
              {selectedFarm && (
                <span className="farm-record-actions">
                  <button className="text-link" type="button" onClick={() => beginFarmForm(selectedFarm)}>Edit farm</button>
                  <button className="text-link danger-link" type="button" onClick={() => void deleteFarm(selectedFarm)} disabled={saving}>Delete farm</button>
                </span>
              )}
            </div>
          )}

          {plotsLoading && <p className="workspace-state" role="status">Loading plots…</p>}
          {plotsError && <div className="workspace-error" role="alert">{plotsError}</div>}
          {!plotsLoading && !plotsError && plots.length === 0 && (
            <div className="workspace-empty">
              <strong>No plots saved yet</strong>
              <span>Add your first plot using its crop, area and location.</span>
              <button className="button button-primary" type="button" onClick={() => beginPlotForm()}>Add a plot</button>
            </div>
          )}

          {plots.length > 0 && (
            <>
              <div className="plot-dashboard-grid">
                {plots.map((plot) => (
                  <PlotDashboardCard
                    key={plot.id}
                    plot={plot}
                    onEdit={() => { setSelectedPlotId(plot.id); beginPlotForm(plot); }}
                    onDelete={() => void deletePlot(plot)}
                  />
                ))}
              </div>
              {selectedFarm?.boundary || plots.some((plot) => plot.boundary) ? (
                <GeoBoundaryMap farm={selectedFarm!} plots={plots} selectedPlotId={selectedPlotId} onSelectPlot={setSelectedPlotId} />
              ) : (
                <p className="plot-map-note"><MapPin size={14} /> Plot locations are saved privately and used for weather. No external map service is required.</p>
              )}
            </>
          )}

          {farmDraft && (
            <form className="workspace-form" onSubmit={(event) => void submitFarm(event)}>
              <h3>{farmDraft.id ? "Edit farm details" : "Add another farm"}</h3>
              <label>Farm name<input required maxLength={120} value={farmDraft.name} onChange={(event) => setFarmDraft({ ...farmDraft, name: event.target.value })} /></label>
              <label>Farm location (optional)<input maxLength={200} value={farmDraft.location} onChange={(event) => setFarmDraft({ ...farmDraft, location: event.target.value })} placeholder="Village or district" /></label>
              <div className="workspace-form-actions">
                <button className="button button-secondary" type="button" onClick={() => setFarmDraft(null)} disabled={saving}>Cancel</button>
                <button className="button button-primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save farm"}</button>
              </div>
            </form>
          )}

          {plotDraft && (
            <form className="workspace-form plot-entry-form" onSubmit={(event) => void submitPlot(event)}>
              <h3>{plotDraft.id ? "Update plot" : "Add a plot"}</h3>
              <label>
                Crop
                <select required value={plotDraft.cropId} onChange={(event) => setPlotDraft({ ...plotDraft, cropId: event.target.value })} disabled={crops.length === 0}>
                  <option value="">{cropsLoading ? "Loading crops…" : crops.length ? "Choose a crop" : "Crop catalogue unavailable"}</option>
                  {crops.map((crop: Crop) => <option key={crop.id} value={crop.id}>{crop.common_name}</option>)}
                </select>
              </label>
              <label>
                Plot area
                <span className="plot-area-input">
                  <input type="number" min="0.0001" max="1000000" step="any" required value={plotDraft.areaValue} onChange={(event) => setPlotDraft({ ...plotDraft, areaValue: event.target.value })} placeholder="e.g. 2" />
                  <select aria-label="Area unit" value={plotDraft.areaUnit} onChange={(event) => setPlotDraft({ ...plotDraft, areaUnit: event.target.value as "acres" | "hectares" })}>
                    <option value="acres">Acres</option>
                    <option value="hectares">Hectares</option>
                  </select>
                </span>
              </label>
              <div className="plot-location-picker">
                <span>Plot location</span>
                <button className="button button-secondary" type="button" onClick={chooseLocation} disabled={locationLoading}>
                  <MapPin size={15} /> {locationLoading ? "Finding location…" : plotDraft.latitude === null ? "Use this device’s location" : "Update saved location"}
                </button>
                <small>
                  {plotDraft.latitude === null
                    ? "Allow location access while standing at the plot. The saved location is sent to enabled weather providers for its forecast."
                    : "Plot location selected and ready to save; weather is tied to this private plot record."}
                </small>
              </div>
              <div className="workspace-form-actions">
                <button className="button button-secondary" type="button" onClick={() => setPlotDraft(null)} disabled={saving}>Cancel</button>
                <button className="button button-primary" type="submit" disabled={saving || locationLoading || cropsLoading || crops.length === 0}>{saving ? "Saving…" : "Save plot"}</button>
              </div>
            </form>
          )}
        </>
      )}
    </section>
  );
}
