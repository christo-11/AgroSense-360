import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { BookOpen, FileText, Search, Trash2, Upload } from "lucide-react";
import { api, type IdukkiPepperReadiness, type ResearchDocument, type ResearchModelStatus } from "../api";

type PredictionRow = {
  target?: string;
  prediction?: number;
  predicted_at?: string;
  warning?: string;
};

export default function ResearchWorkspace({ authenticated }: { authenticated: boolean }) {
  const [documents, setDocuments] = useState<ResearchDocument[]>([]);
  const [model, setModel] = useState<ResearchModelStatus | null>(null);
  const [history, setHistory] = useState<PredictionRow[]>([]);
  const [pepperReadiness, setPepperReadiness] = useState<IdukkiPepperReadiness | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(true);
  const [readinessError, setReadinessError] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [ocrEnabled, setOcrEnabled] = useState(false);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [answerWarning, setAnswerWarning] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [featureColumns, setFeatureColumns] = useState("");
  const [splitColumn, setSplitColumn] = useState("");
  const [splitStrategy, setSplitStrategy] = useState<"group" | "temporal">("group");
  const [taskType, setTaskType] = useState<"regression" | "classification">("regression");
  const [datasetSource, setDatasetSource] = useState("");
  const [datasetLicense, setDatasetLicense] = useState("");
  const [trainingFile, setTrainingFile] = useState<File | null>(null);
  const [rightsConfirmed, setRightsConfirmed] = useState(false);
  const [predictionValues, setPredictionValues] = useState<Record<string, string>>({});
  const [prediction, setPrediction] = useState("");

  async function refreshPrivateData() {
    if (!authenticated) return;
    try {
      const [docs, status, predictions] = await Promise.all([
        api.researchDocuments(),
        api.researchModelStatus(),
        api.researchPredictionHistory(),
      ]);
      setDocuments(docs.items);
      setModel(status);
      setHistory(predictions.items as PredictionRow[]);
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Private research data could not be loaded.");
    }
  }

  useEffect(() => { void refreshPrivateData(); }, [authenticated]);

  useEffect(() => {
    let active = true;
    setReadinessLoading(true);
    api.idukkiBlackPepperReadiness()
      .then((result) => {
        if (active) setPepperReadiness(result);
      })
      .catch((reason: unknown) => {
        if (active) setReadinessError(reason instanceof Error ? reason.message : "Agricultural evidence status could not be loaded.");
      })
      .finally(() => {
        if (active) setReadinessLoading(false);
      });
    return () => { active = false; };
  }, []);

  async function uploadDocument(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    setBusy("upload");
    setError("");
    setSuccess("");
    try {
      const uploaded = await api.uploadResearchDocument(file, ocrEnabled);
      setSuccess(`Saved ${uploaded.filename} locally with ${uploaded.page_count} page(s) using ${uploaded.extraction_method === "text+ocr" ? "text extraction and OCR" : "text extraction"}.`);
      setFile(null);
      setOcrEnabled(false);
      await refreshPrivateData();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Document upload failed.");
    } finally {
      setBusy("");
    }
  }

  async function askResearch(event: FormEvent) {
    event.preventDefault();
    setSearchLoading(true);
    setError("");
    setAnswer("");
    setAnswerWarning("");
    try {
      const result = await api.answerResearch(query);
      setAnswer(result.answer);
      setAnswerWarning(result.warning ?? "");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Document search failed.");
    } finally {
      setSearchLoading(false);
    }
  }

  async function removeDocument(document: ResearchDocument) {
    setBusy(document.id);
    setError("");
    try {
      await api.deleteResearchDocument(document.id);
      setSuccess(`Deleted ${document.filename}.`);
      await refreshPrivateData();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Document deletion failed.");
    } finally {
      setBusy("");
    }
  }

  async function train(event: FormEvent) {
    event.preventDefault();
    if (!trainingFile) return;
    setBusy("training");
    setError("");
    setSuccess("");
    const body = new FormData();
    body.append("file", trainingFile);
    body.append("target_column", targetColumn);
    body.append("feature_columns", featureColumns);
    body.append("split_column", splitColumn);
    body.append("split_strategy", splitStrategy);
    body.append("task_type", taskType);
    body.append("dataset_source", datasetSource);
    body.append("dataset_license", datasetLicense);
    body.append("research_use_confirmed", String(rightsConfirmed));
    try {
      const trained = await api.trainResearchModel(body);
      setModel(trained);
      setPredictionValues({});
      setSuccess(`Trained ${trained.model_type} with ${trained.training_rows} training rows and evaluated ${trained.holdout_rows} holdout rows.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Model training failed.");
    } finally {
      setBusy("");
    }
  }

  async function predict(event: FormEvent) {
    event.preventDefault();
    if (!model?.feature_columns) return;
    setBusy("predict");
    setError("");
    setPrediction("");
    try {
      const result = await api.predictResearchModel(
        Object.fromEntries(model.feature_columns.map((column) => [column, predictionValues[column] ?? ""])),
      );
      setPrediction(`${result.target}: ${result.prediction}`);
      setSuccess(result.warning);
      await refreshPrivateData();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Prediction failed.");
    } finally {
      setBusy("");
    }
  }

  if (!authenticated) {
    return <section className="panel glass-card research-panel"><h2>Sign in to use private research tools</h2><p>Your uploaded documents and model files are stored per account on this backend host.</p></section>;
  }

  return (
    <section className="research-workspace">
      <div className="research-disclaimer">Research tools only. Upload documents and datasets only when you have rights to store and use them. Files stay on the backend host; do not use a public or shared server for private research material.</div>
      {error && <div role="alert" className="module-note research-error">{error}</div>}
      {success && <div role="status" className="module-note research-success">{success}</div>}

      <article className="panel glass-card research-panel">
        <div className="panel-heading"><div><h2>Idukki black pepper evidence check</h2><p>Live crop catalogue and source-verification status; no suitability score is inferred.</p></div></div>
        {readinessLoading && <p role="status" className="research-muted">Loading current agricultural evidence…</p>}
        {readinessError && <p role="alert" className="research-error">{readinessError}</p>}
        {pepperReadiness && (
          <>
            <p>
              Crop record: <strong>{pepperReadiness.crop?.name ?? "Unavailable"}</strong>
              {" · "}Idukki record: <strong>{pepperReadiness.district?.name ?? "Unavailable"}</strong>
              {" · "}assessment: <strong>Not computed</strong>
            </p>
            {pepperReadiness.crop_profile && (
              <p className="research-muted">
                Profile verification: {pepperReadiness.crop_profile.verification_status}
                {" · "}temperature range: {pepperReadiness.crop_profile.temperature_min_celsius ?? "—"}–{pepperReadiness.crop_profile.temperature_max_celsius ?? "—"} °C
                {" · "}annual rainfall range: {pepperReadiness.crop_profile.rainfall_min_mm_year ?? "—"}–{pepperReadiness.crop_profile.rainfall_max_mm_year ?? "—"} mm
              </p>
            )}
            <ul className="research-document-list">
              {pepperReadiness.readiness && Object.entries(pepperReadiness.readiness).map(([key, available]) => (
                <li key={key}><span><strong>{key.replace(/_/g, " ")}</strong><small>{available ? "Available" : "Not established"}</small></span></li>
              ))}
            </ul>
            {pepperReadiness.blockers.length > 0 && (
              <>
                <h3>Evidence still needed</h3>
                <ul>{pepperReadiness.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}</ul>
              </>
            )}
            {pepperReadiness.crop_profile?.sources.length ? (
              <p className="research-muted">Catalog sources: {pepperReadiness.crop_profile.sources.map((source) => (
                <a key={source.url} href={source.url} target="_blank" rel="noreferrer">{source.title} (licence: {source.license ?? "not recorded"}) </a>
              ))}</p>
            ) : <p className="research-muted">No crop-profile sources are recorded in the catalogue.</p>}
          </>
        )}
        <p className="research-muted">
          Candidate sources: <a href="https://ecostat.kerala.gov.in/page/EARAS" target="_blank" rel="noreferrer">Kerala Ecostat EARAS</a> (public reports; reuse terms not stated on the publication page);
          {" "}<a href="https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html" target="_blank" rel="noreferrer">SoilGrids</a> (CC BY 4.0 modeled soil estimates; REST API currently paused);
          {" "}<a href="https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html" target="_blank" rel="noreferrer">IMD gridded rainfall</a> (download page available; dataset reuse licence not stated).
        </p>
      </article>

      <div className="research-grid">
        <article className="panel glass-card research-panel">
          <div className="panel-heading"><div><h2>Local research library</h2><p>PDF, Markdown and UTF-8 text · up to 10 MiB each</p></div><BookOpen size={19} /></div>
          <form className="research-inline-form" onSubmit={(event) => void uploadDocument(event)}>
            <label className="research-file-label"><Upload size={15} /> Choose a document
              <input type="file" accept=".pdf,.md,.txt,application/pdf,text/plain,text/markdown" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>
            {file && <span className="research-muted">{file.name}</span>}
            {file?.name.toLowerCase().endsWith(".pdf") && (
              <label className="research-checkbox"><input type="checkbox" checked={ocrEnabled} onChange={(event) => setOcrEnabled(event.target.checked)} /> Try optional local OCR for scanned pages</label>
            )}
            <button className="button button-primary" disabled={!file || busy !== ""}>{busy === "upload" ? "Extracting…" : "Upload and index"}</button>
          </form>
          {documents.length === 0 ? <p className="research-empty">No documents uploaded yet.</p> : (
            <ul className="research-document-list">
              {documents.map((document) => (
                <li key={document.id}>
                  <FileText size={16} /><span><strong>{document.filename}</strong><small>{document.page_count} page(s) · {document.extraction_method === "text+ocr" ? "OCR used" : "text extraction"} · {new Date(document.uploaded_at).toLocaleString()}</small></span>
                  <button className="icon-button" aria-label={`Delete ${document.filename}`} disabled={busy !== ""} onClick={() => void removeDocument(document)}><Trash2 size={15} /></button>
                </li>
              ))}
            </ul>
          )}
          <p className="research-muted">OCR is opt-in. It requires the separate optional OCR dependencies and a local Tesseract executable; without them, standard text-PDF retrieval is unchanged.</p>
        </article>

        <article className="panel glass-card research-panel">
          <div className="panel-heading"><div><h2>Search and ask</h2><p>Local lexical retrieval returns source excerpts with page citations.</p></div><Search size={19} /></div>
          <form className="research-query-form" onSubmit={(event) => void askResearch(event)}>
            <label>Question or search terms<input required minLength={2} maxLength={500} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. rainfall and crop growth" /></label>
            <button className="button button-primary" disabled={!query.trim() || searchLoading}>{searchLoading ? "Searching…" : "Search documents"}</button>
          </form>
          {answer && <div className="research-answer"><h3>Retrieved evidence</h3><pre>{answer}</pre>{answerWarning && <p className="research-muted">{answerWarning}</p>}</div>}
        </article>
      </div>

      <article className="panel glass-card research-panel">
        <div className="panel-heading"><div><h2>Lightweight yield model</h2><p>Requires a rights-cleared CSV with observed numeric labels and a group or time column.</p></div></div>
        {model?.available ? (
          <div className="research-model-status">
            <p><strong>{model.model_type}</strong> · target: {model.target_column} · split: {model.split_strategy} · {model.training_rows} train / {model.holdout_rows} holdout rows</p>
            <p>Holdout MAE {model.metrics?.holdout_mae?.toPrecision(4) ?? "—"} · RMSE {model.metrics?.holdout_rmse?.toPrecision(4) ?? "—"} · R² {model.metrics?.holdout_r2?.toPrecision(4) ?? "—"}</p>
            <p className="research-muted">{model.limitations?.join(" ")}</p>
            <form className="research-form-grid" onSubmit={(event) => void predict(event)}>
              {model.feature_columns?.map((column) => (
                <label key={column}>{column}<input required value={predictionValues[column] ?? ""} onChange={(event) => setPredictionValues((values) => ({ ...values, [column]: event.target.value }))} /></label>
              ))}
              <button className="button button-primary" disabled={busy !== ""}>{busy === "predict" ? "Predicting…" : "Record research prediction"}</button>
            </form>
            {prediction && <p role="status" className="research-success">{prediction}</p>}
            <h3>Prediction history ({history.length})</h3>
            <ul className="research-document-list">
              {history.slice(0, 10).map((row, index) => <li key={`${row.predicted_at}-${index}`}><span><strong>{row.target}: {row.prediction}</strong><small>{row.predicted_at}</small></span></li>)}
            </ul>
          </div>
        ) : (
          <>
            <p className="research-muted">{model?.detail ?? "No model has been evaluated for this account."} No crop suitability/recommendation is inferred from the catalogue’s pending data.</p>
            <form className="research-model-form" onSubmit={(event) => void train(event)}>
              <label>Training CSV<input type="file" accept=".csv,text/csv" onChange={(event) => setTrainingFile(event.target.files?.[0] ?? null)} required /></label>
              <div className="research-form-grid">
                  <label>Model task<select value={taskType} onChange={(event) => setTaskType(event.target.value as "regression" | "classification")}><option value="regression">Yield / numeric regression</option><option value="classification">Crop suitability / recommendation classes</option></select></label>
                  <label>{taskType === "regression" ? "Numeric target column" : "Verified class label column"}<input value={targetColumn} onChange={(event) => setTargetColumn(event.target.value)} required /></label>
                <label>Feature columns (comma-separated)<input value={featureColumns} onChange={(event) => setFeatureColumns(event.target.value)} required /></label>
                <label>Split/group column<input value={splitColumn} onChange={(event) => setSplitColumn(event.target.value)} required /></label>
                <label>Leakage-aware split<select value={splitStrategy} onChange={(event) => setSplitStrategy(event.target.value as "group" | "temporal")}><option value="group">Hold out entire groups/farms</option><option value="temporal">Train past, test future</option></select></label>
                <label>Dataset/source citation<input value={datasetSource} onChange={(event) => setDatasetSource(event.target.value)} placeholder="Resource URL or owner/source reference" required /></label>
                <label>Dataset licence/terms<input value={datasetLicense} onChange={(event) => setDatasetLicense(event.target.value)} placeholder="Exact licence and version" required /></label>
              </div>
              <label className="research-checkbox"><input type="checkbox" checked={rightsConfirmed} onChange={(event) => setRightsConfirmed(event.target.checked)} required /> I have rights to use this exact dataset for non-commercial research and the labels are genuine observations.</label>
              <button className="button button-primary" disabled={!trainingFile || busy !== ""}>{busy === "training" ? "Training and evaluating…" : "Train and evaluate"}</button>
              <p className="research-muted">The model is stored locally for this account. A single held-out split is not proof of generalization or an agronomic recommendation. Do not upload ERA5 archives rejected by the project quality review.</p>
            </form>
          </>
        )}
      </article>
    </section>
  );
}
