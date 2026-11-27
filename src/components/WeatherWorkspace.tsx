import { useState } from "react";
import { Activity, CloudSun, RefreshCw } from "lucide-react";
import { api, type MonthlyClimateResponse, type WeatherResponse } from "../api";

function daysAgo(days: number) {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() - days);
  return date.toISOString().slice(0, 10);
}

function defaultClimateYears() {
  const endYear = new Date().getUTCFullYear() - 1;
  return { startYear: String(endYear - 29), endYear: String(endYear) };
}

const MONTH_NAMES = Array.from({ length: 12 }, (_, index) =>
  new Intl.DateTimeFormat("en", { month: "long", timeZone: "UTC" }).format(new Date(Date.UTC(2024, index, 1))),
);

function formatValue(value: number | null, unit: string) {
  return value === null ? "—" : unit ? `${value.toFixed(1)} ${unit}` : value.toFixed(1);
}

export default function WeatherWorkspace({
  authenticated,
  onRequestSignIn,
}: {
  authenticated: boolean;
  onRequestSignIn: () => void;
}) {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [startDate, setStartDate] = useState(daysAgo(33));
  const [endDate, setEndDate] = useState(daysAgo(3));
  const [climateYears, setClimateYears] = useState(defaultClimateYears);
  const [history, setHistory] = useState<WeatherResponse | null>(null);
  const [forecast, setForecast] = useState<WeatherResponse | null>(null);
  const [climate, setClimate] = useState<MonthlyClimateResponse | null>(null);
  const [loading, setLoading] = useState<"history" | "forecast" | "monthly" | null>(null);
  const [error, setError] = useState("");

  async function load(kind: "history" | "forecast" | "monthly") {
    const lat = Number(latitude);
    const lon = Number(longitude);
    if (!latitude.trim() || !longitude.trim() || !Number.isFinite(lat) || !Number.isFinite(lon)) {
      setError("Enter valid latitude and longitude coordinates.");
      return;
    }
    if (kind === "monthly") {
      const startYear = Number(climateYears.startYear);
      const endYear = Number(climateYears.endYear);
      if (!Number.isInteger(startYear) || !Number.isInteger(endYear) || startYear < 1981 || endYear < startYear || endYear - startYear > 29) {
        setError("Enter a valid NASA POWER climate period of up to 30 years, starting no earlier than 1981.");
        return;
      }
    }
    setLoading(kind);
    setError("");
    try {
      if (kind === "history") {
        setHistory(await api.historicalWeather(lat, lon, startDate, endDate));
      } else if (kind === "forecast") {
        setForecast(await api.weatherForecast(lat, lon));
      } else {
        setClimate(await api.monthlyClimate(lat, lon, Number(climateYears.startYear), Number(climateYears.endYear)));
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Weather data could not be loaded.");
      if (kind === "history") setHistory(null);
      else if (kind === "forecast") setForecast(null);
      else setClimate(null);
    } finally {
      setLoading(null);
    }
  }

  function readings(result: WeatherResponse, showFirst = false) {
    const visibleRecords = showFirst ? result.records.slice(0, 30) : result.records.slice(-30);
    return (
      <div className="research-table-wrap">
        <table className="research-table">
          <thead><tr><th>Timestamp (UTC)</th>{Object.keys(result.units).map((key) => <th key={key}>{key} ({result.units[key]})</th>)}</tr></thead>
          <tbody>
            {visibleRecords.map((record) => (
              <tr key={record.timestamp}>
                <td>{record.timestamp.replace("T", " ").replace("Z", "")}</td>
                {Object.keys(result.units).map((key) => (
                  <td key={key}>{formatValue(record.values[key] ?? null, "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {result.records.length > 30 && <p className="research-muted">Showing the latest 30 of {result.records.length} records.</p>}
      </div>
    );
  }

  return (
    <section className="research-workspace">
      {!authenticated && (
        <div className="research-disclaimer">Sign in before requesting weather; your coordinates will be sent to NASA POWER or, if enabled, Open-Meteo. <button className="text-link" onClick={onRequestSignIn}>Sign in</button></div>
      )}
      <article className="panel glass-card research-panel">
        <div className="panel-heading">
          <div><h2>Location-specific weather</h2><p>Coordinates are sent to the selected external provider.</p></div>
          <span className="weather-icon"><CloudSun size={20} /></span>
        </div>
        <div className="research-form-grid">
          <label>Latitude<input type="number" min="-90" max="90" step="any" value={latitude} onChange={(event) => setLatitude(event.target.value)} placeholder="e.g. 10.1" required /></label>
          <label>Longitude<input type="number" min="-180" max="180" step="any" value={longitude} onChange={(event) => setLongitude(event.target.value)} placeholder="e.g. 76.2" required /></label>
          <label>Historical start<input type="date" min="1981-01-01" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label>
          <label>Historical end<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label>
          <label>Climate start year<input type="number" min="1981" max={new Date().getUTCFullYear() - 1} value={climateYears.startYear} onChange={(event) => setClimateYears((years) => ({ ...years, startYear: event.target.value }))} /></label>
          <label>Climate end year<input type="number" min="1981" max={new Date().getUTCFullYear() - 1} value={climateYears.endYear} onChange={(event) => setClimateYears((years) => ({ ...years, endYear: event.target.value }))} /></label>
        </div>
        <div className="research-actions">
          <button className="button button-primary" disabled={!authenticated || loading !== null} onClick={() => void load("history")}>
            <RefreshCw size={15} className={loading === "history" ? "spin" : ""} /> {loading === "history" ? "Loading history…" : "Load NASA POWER history"}
          </button>
          <button className="button button-secondary" disabled={!authenticated || loading !== null} onClick={() => void load("monthly")}>
            <RefreshCw size={15} className={loading === "monthly" ? "spin" : ""} /> {loading === "monthly" ? "Loading climate…" : "Load monthly climate"}
          </button>
          <button className="button button-secondary" disabled={!authenticated || loading !== null} onClick={() => void load("forecast")}>
            <CloudSun size={15} /> {loading === "forecast" ? "Loading forecast…" : "Load Open-Meteo forecast"}
          </button>
        </div>
        {error && <div role="alert" className="module-note research-error">{error}</div>}
        {!history && !forecast && !loading && !error && (
          <div className="research-empty"><Activity size={19} /><span>Choose a location and request historical data or an eligible forecast.</span></div>
        )}
      </article>

      {history && (
        <article className="panel glass-card research-panel">
          <div className="panel-heading"><div><h2>Historical daily estimates</h2><p>{history.provider} · {history.data_kind.replace(/_/g, " ")} · {history.records.length} records</p></div></div>
          <p className="research-attribution">{history.attribution} <a href={history.source_url} target="_blank" rel="noreferrer">Source</a></p>
          {readings(history)}
        </article>
      )}

      {climate && (
        <article className="panel glass-card research-panel">
          <div className="panel-heading"><div><h2>Monthly climate context</h2><p>{climate.provider}{climate.source_datasets.length ? ` · ${climate.source_datasets.join(", ")}` : ""} · multi-year monthly means · {climate.start_year}–{climate.end_year}</p></div></div>
          <p className="research-attribution">{climate.attribution} <a href={climate.source_url} target="_blank" rel="noreferrer">Source</a></p>
          <div className="research-table-wrap">
            <table className="research-table">
              <thead><tr><th>Month</th>{Object.keys(climate.units).map((key) => <th key={key}>{key} ({climate.units[key]})</th>)}</tr></thead>
              <tbody>
                {climate.records.map((record) => (
                  <tr key={record.month}>
                    <td>{MONTH_NAMES[record.month - 1]}</td>
                    {Object.keys(climate.units).map((key) => (
                      <td key={key} title={`${record.years_with_data[key] ?? 0} years with data`}>
                        {formatValue(record.values[key] ?? null, "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="research-muted">{climate.limitation}</p>
        </article>
      )}

      {forecast && (
        <article className="panel glass-card research-panel">
          <div className="panel-heading"><div><h2>Hourly forecast</h2><p>{forecast.provider} · {forecast.data_kind.replace(/_/g, " ")}</p></div></div>
          <p className="research-attribution">{forecast.attribution} <a href={forecast.source_url} target="_blank" rel="noreferrer">Source</a></p>
          {readings(forecast, true)}
        </article>
      )}
      <p className="research-muted">NASA POWER values are gridded estimates, not direct weather-station observations. Forecast access is disabled by default; enable it only for qualifying non-commercial use under Open-Meteo’s terms.</p>
    </section>
  );
}
