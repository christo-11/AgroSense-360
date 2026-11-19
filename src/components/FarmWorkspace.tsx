import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { api, ApiError, type Farm, type Plot } from "../api";
import { formatBoundary, parseBoundaryJson } from "../geojson";
import GeoBoundaryMap from "./GeoBoundaryMap";

type Props = {
  authenticated: boolean;
  farms: Farm[];
  loading: boolean;
  loadError: string;
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onRequestSignIn: () => void;
};

type FarmDraft = {
  id: string | null;
  name: string;
  location: string;
  boundary: string;
};

type PlotDraft = {
  id: string | null;
  name: string;
  crop: string;
  boundary: string;
};

const emptyFarmDraft: FarmDraft = { id: null, name: "", location: "", boundary: "" };
const emptyPlotDraft: PlotDraft = { id: null, name: "", crop: "", boundary: "" };

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
  const [plots, setPlots] = useState<Plot[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<string | null>(null);
  const [plotsLoading, setPlotsLoading] = useState(false);
  const [plotsError, setPlotsError] = useState("");
  const [plotRevision, setPlotRevision] = useState(0);
  const [farmDraft, setFarmDraft] = useState<FarmDraft | null>(null);
  const [plotDraft, setPlotDraft] = useState<PlotDraft | null>(null);
  const [actionError, setActionError] = useState("");
  const [saving, setSaving] = useState(false);

  const selectedFarm = useMemo(
    () => farms.find((farm) => farm.id === selectedFarmId) ?? farms[0] ?? null,
    [farms, selectedFarmId],
  );
  const selectedPlot = plots.find((plot) => plot.id === selectedPlotId) ?? null;

  useEffect(() => {
    if (selectedFarm?.id !== selectedFarmId) setSelectedFarmId(selectedFarm?.id ?? null);
  }, [selectedFarm, selectedFarmId]);

  useEffect(() => {
    setSelectedPlotId(null);
  }, [selectedFarm?.id]);

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
      if (active) {
        setPlots(result);
        setPlotsError("");
      }
    }).catch((error: unknown) => {
      if (active) {
        setPlots([]);
        setPlotsError(error instanceof Error ? error.message : "Could not load plots.");
        if (error instanceof ApiError && error.status === 401) void onRefresh();
      }
    }).finally(() => {
      if (active) setPlotsLoading(false);
    });

    return () => { active = false; };
  }, [authenticated, onRefresh, selectedFarm, plotRevision]);

  const reloadPlots = useCallback(() => setPlotRevision((revision) => revision + 1), []);

  function beginFarmForm(farm?: Farm) {
    setActionError("");
    setFarmDraft(farm
      ? { id: farm.id, name: farm.name, location: farm.location ?? "", boundary: formatBoundary(farm.boundary) }
      : { ...emptyFarmDraft });
    setPlotDraft(null);
  }

  function beginPlotForm(plot?: Plot) {
    setActionError("");
    setPlotDraft(plot
      ? { id: plot.id, name: plot.name, crop: plot.crop ?? "", boundary: formatBoundary(plot.boundary) }
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
      const boundary = parseBoundaryJson(farmDraft.boundary, false);
      const changes = {
        name: farmDraft.name.trim(),
        location: farmDraft.location.trim() || null,
        boundary,
      };
      if (farmDraft.id) {
        await api.updateFarm(farmDraft.id, changes);
      } else {
        const created = await api.createFarm(changes.name, changes.location ?? "", changes.boundary);
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

  async function deleteFarm(farm: Farm) {
    if (!window.confirm(`Delete "${farm.name}" and all of its plots? This cannot be undone.`)) return;
    setActionError("");
    setSaving(true);
    try {
      await api.deleteFarm(farm.id);
      await onRefresh();
      onNotice("Farm and its plots deleted.");
    } catch (error) {
      reportActionError(error, "Could not delete farm.");
    } finally {
      setSaving(false);
    }
  }

  async function submitPlot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!plotDraft || !selectedFarm) return;
    setSaving(true);
    setActionError("");
    try {
      const boundary = parseBoundaryJson(plotDraft.boundary, true);
      if (!boundary) throw new Error("A GeoJSON plot boundary is required.");
      const changes = { name: plotDraft.name.trim(), crop: plotDraft.crop.trim() || null, boundary };
      if (plotDraft.id) {
        await api.updatePlot(selectedFarm.id, plotDraft.id, changes);
      } else {
        const created = await api.createPlot(selectedFarm.id, changes);
        setSelectedPlotId(created.id);
      }
      setPlotDraft(null);
      reloadPlots();
      onNotice(plotDraft.id ? "Plot updated." : "Plot created.");
    } catch (error) {
      reportActionError(error, "Could not save plot.");
    } finally {
      setSaving(false);
    }
  }

  async function deletePlot(plot: Plot) {
    if (!selectedFarm || !window.confirm(`Delete plot "${plot.name}"? This cannot be undone.`)) return;
    setActionError("");
    setSaving(true);
    try {
      await api.deletePlot(selectedFarm.id, plot.id);
      setSelectedPlotId(null);
      reloadPlots();
      onNotice("Plot deleted.");
    } catch (error) {
      reportActionError(error, "Could not delete plot.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="farm-workspace panel glass-card" id="farm-workspace" aria-labelledby="farm-workspace-title">
      <div className="panel-heading">
        <div>
          <h2 id="farm-workspace-title">Farms & plots</h2>
          <p>Manage saved farm records and their WGS84 plot boundaries.</p>
        </div>
        {authenticated && (
          <button className="button button-primary" type="button" onClick={() => beginFarmForm()}>
            Add farm
          </button>
        )}
      </div>

      {!authenticated ? (
        <div className="workspace-empty">
          <strong>Sign in to manage farms and plots</strong>
          <span>Farm records are private to your account.</span>
          <button className="button button-secondary" type="button" onClick={onRequestSignIn}>Sign in</button>
        </div>
      ) : (
        <>
          {loadError && <div className="workspace-error" role="alert">{loadError}</div>}
          {actionError && <div className="workspace-error" role="alert">{actionError}</div>}
          {loading && <p className="workspace-state" role="status">Loading farms…</p>}
          {!loading && !loadError && farms.length === 0 && (
            <div className="workspace-empty">
              <strong>No farms saved yet</strong>
              <span>Create a farm record to begin adding real plot boundaries.</span>
            </div>
          )}

          {farms.length > 0 && (
            <div className="farm-workspace-layout">
              <div className="farm-records">
                <label className="farm-select-label" htmlFor="farm-select">Selected farm</label>
                <select
                  id="farm-select"
                  value={selectedFarm?.id ?? ""}
                  onChange={(event) => {
                    setSelectedFarmId(event.target.value);
                    setPlotDraft(null);
                  }}
                  disabled={saving}
                >
                  {farms.map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}
                </select>
                {selectedFarm && (
                  <div className="selected-farm-card">
                    <span>{selectedFarm.location || "Location not set"}</span>
                    <div className="record-actions">
                      <button type="button" className="text-link" onClick={() => beginFarmForm(selectedFarm)}>Edit farm</button>
                      <button type="button" className="text-link danger-link" onClick={() => void deleteFarm(selectedFarm)} disabled={saving}>Delete</button>
                    </div>
                  </div>
                )}
                <div className="plot-list-heading">
                  <strong>Plots</strong>
                  {selectedFarm && <button className="text-link" type="button" onClick={() => beginPlotForm()}>Add plot</button>}
                </div>
                {plotsLoading && <p className="workspace-state" role="status">Loading plots…</p>}
                {plotsError && <div className="workspace-error" role="alert">{plotsError}</div>}
                {!plotsLoading && !plotsError && plots.length === 0 && (
                  <p className="workspace-state">No plots saved for this farm.</p>
                )}
                <ul className="plot-record-list">
                  {plots.map((plot) => (
                    <li key={plot.id} className={plot.id === selectedPlotId ? "is-selected" : ""}>
                      <button type="button" className="plot-select" onClick={() => setSelectedPlotId(plot.id)}>
                        <strong>{plot.name}</strong><span>{plot.crop || "Crop not set"}</span>
                      </button>
                      <button type="button" className="text-link" onClick={() => beginPlotForm(plot)}>Edit</button>
                      <button type="button" className="text-link danger-link" onClick={() => void deletePlot(plot)} disabled={saving}>Delete</button>
                    </li>
                  ))}
                </ul>
              </div>

              {selectedFarm && (
                <GeoBoundaryMap
                  farm={selectedFarm}
                  plots={plots}
                  selectedPlotId={selectedPlot?.id ?? null}
                  onSelectPlot={setSelectedPlotId}
                />
              )}
            </div>
          )}

          {farmDraft && (
            <form className="workspace-form" onSubmit={(event) => void submitFarm(event)}>
              <h3>{farmDraft.id ? "Edit farm" : "Create farm"}</h3>
              <label>Farm name<input required maxLength={120} value={farmDraft.name} onChange={(event) => setFarmDraft({ ...farmDraft, name: event.target.value })} /></label>
              <label>Location<input maxLength={200} value={farmDraft.location} onChange={(event) => setFarmDraft({ ...farmDraft, location: event.target.value })} placeholder="Village, district or region" /></label>
              <label>
                Farm boundary GeoJSON (optional)
                <textarea rows={5} spellCheck={false} value={farmDraft.boundary} onChange={(event) => setFarmDraft({ ...farmDraft, boundary: event.target.value })} placeholder='{"type":"Polygon","coordinates":[...]}' />
              </label>
              <p className="field-help">Paste a closed WGS84 Polygon or MultiPolygon. Coordinates use [longitude, latitude]. Leave blank to save without a farm outline.</p>
              <div className="workspace-form-actions">
                <button className="button button-secondary" type="button" onClick={() => setFarmDraft(null)} disabled={saving}>Cancel</button>
                <button className="button button-primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save farm"}</button>
              </div>
            </form>
          )}

          {plotDraft && selectedFarm && (
            <form className="workspace-form" onSubmit={(event) => void submitPlot(event)}>
              <h3>{plotDraft.id ? "Edit plot" : "Add plot"}</h3>
              <label>Plot name<input required maxLength={120} value={plotDraft.name} onChange={(event) => setPlotDraft({ ...plotDraft, name: event.target.value })} /></label>
              <label>Crop<input maxLength={120} value={plotDraft.crop} onChange={(event) => setPlotDraft({ ...plotDraft, crop: event.target.value })} placeholder="e.g. Cardamom" /></label>
              <label>
                Plot boundary GeoJSON (required)
                <textarea required rows={6} spellCheck={false} value={plotDraft.boundary} onChange={(event) => setPlotDraft({ ...plotDraft, boundary: event.target.value })} placeholder='{"type":"Polygon","coordinates":[...]}' />
              </label>
              <p className="field-help">Use a closed WGS84 Polygon or MultiPolygon with [longitude, latitude] coordinate pairs.</p>
              <div className="workspace-form-actions">
                <button className="button button-secondary" type="button" onClick={() => setPlotDraft(null)} disabled={saving}>Cancel</button>
                <button className="button button-primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save plot"}</button>
              </div>
            </form>
          )}
        </>
      )}
    </section>
  );
}
