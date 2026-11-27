import { useEffect, useState } from "react";
import { RefreshCw, TrendingUp } from "lucide-react";
import { api, type Crop, type District, type MarketPricesResponse } from "../api";

type Props = {
  authenticated: boolean;
  fixedCommodity?: string;
  compact?: boolean;
  onRequestSignIn?: () => void;
};

function formatPrice(value: number | null, currency: string) {
  if (value === null) return "Not reported";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(value: string) {
  const parsed = new Date(`${value}T00:00:00Z`);
  return Number.isNaN(parsed.getTime())
    ? value
    : new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeZone: "UTC" }).format(parsed);
}

export default function MarketWorkspace({
  authenticated,
  fixedCommodity,
  compact = false,
  onRequestSignIn,
}: Props) {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [commodity, setCommodity] = useState(fixedCommodity ?? "");
  const [district, setDistrict] = useState("");
  const [catalogueError, setCatalogueError] = useState("");
  const [result, setResult] = useState<MarketPricesResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setCatalogueError("");
    const cropRequest = fixedCommodity ? Promise.resolve(null) : api.crops({ limit: 100 });
    void Promise.all([cropRequest, api.districts(100)])
      .then(([cropPage, districtPage]) => {
        if (!active) return;
        if (cropPage) setCrops(cropPage.items);
        setDistricts(districtPage.items);
      })
      .catch((reason: unknown) => {
        if (active) {
          setCatalogueError(reason instanceof Error ? reason.message : "Market filters could not be loaded.");
        }
      });
    return () => { active = false; };
  }, [fixedCommodity]);

  async function loadPrices() {
    if (!authenticated) {
      onRequestSignIn?.();
      return;
    }
    if (!commodity.trim()) {
      setError("Choose a crop to search for market prices.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.marketPrices(commodity.trim(), district || undefined));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Market prices could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className={`market-workspace ${compact ? "market-workspace-compact" : ""}`}>
      {!authenticated && (
        <div className="market-unavailable">
          <strong>Sign in to view market prices</strong>
          <span>Market requests are available to signed-in farmers.</span>
          {onRequestSignIn && <button className="text-link" type="button" onClick={onRequestSignIn}>Sign in</button>}
        </div>
      )}
      {catalogueError && <p className="market-error" role="alert">{catalogueError}</p>}
      <div className="market-filters">
        {!fixedCommodity ? (
          <label>
            Crop
            <select value={commodity} onChange={(event) => setCommodity(event.target.value)} disabled={crops.length === 0}>
              <option value="">{crops.length ? "Choose a crop" : "Crop catalogue unavailable"}</option>
              {crops.map((crop) => <option key={crop.id} value={crop.common_name}>{crop.common_name}</option>)}
            </select>
          </label>
        ) : (
          <div className="market-selected-crop"><span>Crop</span><strong>{fixedCommodity}</strong></div>
        )}
        <label>
          Market district
          <select value={district} onChange={(event) => setDistrict(event.target.value)}>
            <option value="">All Kerala markets</option>
            {districts.map((item) => <option key={item.id} value={item.name}>{item.name}</option>)}
          </select>
        </label>
        <button className="button button-secondary" type="button" onClick={() => void loadPrices()} disabled={loading || !authenticated || !commodity.trim()}>
          <RefreshCw size={14} className={loading ? "spin" : ""} />
          {loading ? "Checking daily prices…" : "Find market prices"}
        </button>
      </div>

      {loading && <p className="market-state" role="status">Checking the daily market-price feed…</p>}
      {error && (
        <div className="market-error" role="alert">
          <span>{error}</span>
          <button className="text-link" type="button" onClick={() => void loadPrices()} disabled={loading}>Retry</button>
        </div>
      )}
      {result && (
        <>
          <p className="market-attribution">
            {result.provider} · Daily reported prices, not real-time quotes · Retrieved {new Date(result.requested_at).toLocaleString()}
            {result.source_updated_at ? ` · Source updated ${result.source_updated_at}` : " · Source update time not provided"}
            {" · "}<a href={result.source_url} target="_blank" rel="noreferrer">Source</a>
          </p>
          <div className="market-price-list">
            {result.records.map((record) => (
              <article className="market-price-card" key={`${record.district}-${record.market}-${record.market_date}`}>
                <div className="market-price-heading">
                  <strong>{record.market}</strong>
                  <span>{record.district}, {record.state}</span>
                </div>
                <p>Market date: {formatDate(record.market_date)}{record.variety ? ` · ${record.variety}` : ""}</p>
                <dl>
                  <div><dt>Minimum</dt><dd>{formatPrice(record.prices.minimum, result.currency)}</dd></div>
                  <div><dt>Maximum</dt><dd>{formatPrice(record.prices.maximum, result.currency)}</dd></div>
                  <div><dt>Modal</dt><dd>{formatPrice(record.prices.modal, result.currency)}</dd></div>
                </dl>
                <small>Reported in {result.currency} {result.price_unit}</small>
              </article>
            ))}
            {result.records.length === 0 && (
              <div className="market-unavailable">
                <TrendingUp size={18} />
                <strong>No daily records returned for this crop and market selection.</strong>
                <span>Try another district or check again later; no prices are estimated.</span>
              </div>
            )}
          </div>
          <p className="market-attribution">{result.attribution} {result.license}</p>
        </>
      )}
      {!result && !error && !loading && authenticated && (
        <p className="market-state">Prices are shown only when the government feed returns records for the selected crop and market.</p>
      )}
      {!compact && (
        <p className="market-attribution">
          Market dates follow the source’s daily reporting cadence. Prices are displayed as reported; missing values are not estimated.
        </p>
      )}
    </section>
  );
}
