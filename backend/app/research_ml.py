"""User-scoped, low-memory ML workflow for labeled agricultural CSV files."""

import hashlib
import io
import json
import logging
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings
from app.models import User
from app.security import current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/research/ml", tags=["research ML"])
MAX_CSV_BYTES = 20 * 1024 * 1024
MAX_ROWS = 50_000
MAX_FEATURES = 30


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: dict[str, float | str | None] = Field(min_length=1, max_length=MAX_FEATURES)


def _storage_root() -> Path:
    configured = get_settings().research_document_dir
    root = configured if configured.is_absolute() else Path(__file__).resolve().parents[2] / configured
    return root.resolve().parent / "research_models"


def _owner_dir(user: User, create: bool = False) -> Path:
    directory = _storage_root() / str(user.id)
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink():
        raise HTTPException(status_code=500, detail="Research model storage cannot use symbolic links.")
    return directory


def _artifact_paths(user: User) -> tuple[Path, Path, Path]:
    directory = _owner_dir(user)
    return directory / "model.joblib", directory / "model.json", directory / "prediction_history.jsonl"


def _read_model_metadata(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise HTTPException(status_code=404, detail="No research model is trained for this account.")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        logger.exception("Research model metadata could not be read.")
        raise HTTPException(status_code=500, detail="Stored model metadata is unavailable.") from error
    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Stored model metadata is invalid.")
    return result


def _split_indices(frame, strategy: str, split_column: str):
    import pandas as pd
    from sklearn.model_selection import GroupShuffleSplit

    if split_column not in frame.columns:
        raise ValueError(f"Split column '{split_column}' is missing.")
    if strategy == "group":
        groups = frame[split_column]
        if groups.isna().any() or groups.nunique() < 5:
            raise ValueError("Group splitting requires at least five non-empty unique groups.")
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_indices, test_indices = next(splitter.split(frame, groups=groups))
        if set(groups.iloc[train_indices]) & set(groups.iloc[test_indices]):
            raise ValueError("Group split leaked a group across the train/test boundary.")
        return train_indices, test_indices
    if strategy == "temporal":
        timestamps = pd.to_datetime(frame[split_column], errors="coerce", utc=True)
        if timestamps.isna().any():
            raise ValueError("Temporal splitting requires valid timestamps in the split column.")
        order = timestamps.sort_values(kind="stable").index.to_numpy()
        cutoff = int(len(order) * 0.8)
        if cutoff < 1 or cutoff >= len(order):
            raise ValueError("Temporal split does not provide both training and test rows.")
        return order[:cutoff], order[cutoff:]
    raise ValueError("split_strategy must be 'group' or 'temporal'.")


def _build_estimator(frame, feature_columns: list[str], task_type: str):
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    numeric = [
        column for column in feature_columns
        if __import__("pandas").api.types.is_numeric_dtype(frame[column])
    ]
    categorical = [column for column in feature_columns if column not in numeric]
    for column in categorical:
        if frame[column].nunique(dropna=True) > 200:
            raise ValueError(f"Categorical feature '{column}' exceeds the 200-category limit.")
    transforms = []
    if numeric:
        transforms.append(
            ("numeric", SimpleImputer(strategy="median", add_indicator=True), numeric)
        )
    if categorical:
        transforms.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", max_categories=50)),
                    ]
                ),
                categorical,
            )
        )
    preprocessing = ColumnTransformer(transforms, remainder="drop", sparse_threshold=1.0)
    # A bounded tree ensemble keeps single-user CPU and memory use predictable.
    estimator_class = RandomForestClassifier if task_type == "classification" else RandomForestRegressor
    estimator = estimator_class(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=2,
        max_features=1.0,
        n_jobs=1,
        random_state=42,
    )
    return Pipeline([("preprocessing", preprocessing), ("model", estimator)])


def _train(
    raw: bytes,
    filename: str,
    target_column: str,
    feature_columns: list[str],
    split_column: str,
    split_strategy: str,
    task_type: str,
):
    try:
        import pandas as pd
    except ImportError as error:
        raise ValueError("Install the optional research dependencies before training: requirements-research.txt.") from error
    try:
        import numpy as np

        header = pd.read_csv(io.BytesIO(raw), nrows=0)
    except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
        raise ValueError("CSV could not be parsed; use a UTF-8 comma-separated file.") from error
    columns = [target_column, split_column, *feature_columns]
    if len(feature_columns) > MAX_FEATURES or len(set(columns)) != len(columns):
        raise ValueError(f"Select 1–{MAX_FEATURES} distinct feature columns and separate target/split columns.")
    missing = sorted(set(columns) - set(header.columns))
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(missing)}.")
    try:
        frame = pd.read_csv(io.BytesIO(raw), usecols=columns, nrows=MAX_ROWS + 1, low_memory=True)
    except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
        raise ValueError("CSV could not be parsed; use a UTF-8 comma-separated file.") from error
    if len(frame) > MAX_ROWS:
        raise ValueError(f"Training CSV is limited to {MAX_ROWS} rows.")
    if len(frame) < 30:
        raise ValueError("At least 30 labeled rows are required before the holdout evaluation.")
    if frame[target_column].isna().any():
        raise ValueError("The target column must contain a label for every row.")
    if task_type == "regression":
        targets = pd.to_numeric(frame[target_column], errors="coerce")
        if targets.isna().any() or not np.isfinite(targets.to_numpy(dtype=float)).all():
            raise ValueError("Regression targets must be finite numeric labels for every row.")
    elif task_type == "classification":
        targets = frame[target_column].astype(str)
        if targets.nunique() < 2:
            raise ValueError("Classification requires at least two distinct labeled classes.")
    else:
        raise ValueError("task_type must be 'regression' or 'classification'.")
    train_indices, test_indices = _split_indices(frame, split_strategy, split_column)
    if len(test_indices) < 5:
        raise ValueError("The holdout set must contain at least five rows.")
    if task_type == "classification":
        all_classes = set(targets)
        if set(targets.iloc[train_indices]) != all_classes or set(targets.iloc[test_indices]) != all_classes:
            raise ValueError("Every class must appear in both train and holdout sets; add representative labeled groups.")
    features = frame[feature_columns].copy()
    for column in feature_columns:
        if features[column].isna().all():
            raise ValueError(f"Feature '{column}' contains no usable values.")
        if pd.api.types.is_numeric_dtype(features[column]):
            numeric_values = pd.to_numeric(features[column], errors="coerce")
            if not np.isfinite(numeric_values.dropna().to_numpy(dtype=float)).all():
                raise ValueError(f"Feature '{column}' contains non-finite numeric values.")
            features[column] = numeric_values
        else:
            features[column] = features[column].astype("string")
    if all(features[column].isna().all() for column in feature_columns):
        raise ValueError("Selected feature columns contain no usable values.")

    model = _build_estimator(features, feature_columns, task_type)
    model.fit(features.iloc[train_indices], targets.iloc[train_indices])
    predicted = model.predict(features.iloc[test_indices])
    if task_type == "regression":
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        measured = targets.iloc[test_indices].to_numpy(dtype=float)
        metrics = {
            "holdout_mae": float(mean_absolute_error(measured, predicted)),
            "holdout_rmse": float(np.sqrt(mean_squared_error(measured, predicted))),
            "holdout_r2": float(r2_score(measured, predicted)) if len(measured) > 1 else None,
        }
    else:
        from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

        measured = targets.iloc[test_indices].astype(str).to_numpy()
        metrics = {
            "holdout_accuracy": float(accuracy_score(measured, predicted)),
            "holdout_balanced_accuracy": float(balanced_accuracy_score(measured, predicted)),
            "holdout_macro_f1": float(f1_score(measured, predicted, average="macro", zero_division=0)),
        }
    return model, {
        "model_id": uuid.uuid4().hex,
        "model_type": "RandomForestRegressor" if task_type == "regression" else "RandomForestClassifier",
        "task_type": task_type,
        "feature_columns": feature_columns,
        "numeric_feature_columns": [
            column for column in feature_columns if pd.api.types.is_numeric_dtype(features[column])
        ],
        "categorical_feature_columns": [
            column for column in feature_columns if not pd.api.types.is_numeric_dtype(features[column])
        ],
        "target_column": target_column,
        "split_column": split_column,
        "split_strategy": split_strategy,
        "training_rows": len(train_indices),
        "holdout_rows": len(test_indices),
        "metrics": metrics,
        "dataset_filename": Path(filename).name[:255],
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Metrics describe one holdout split only; they are not independent validation or evidence of agronomic suitability.",
            "Predictions are research outputs and require domain review before interpretation.",
        ],
    }


@router.get("/status")
def model_status(user: User = Depends(current_user)) -> dict:
    _, metadata_path, _ = _artifact_paths(user)
    if not metadata_path.is_file():
        return {
            "available": False,
            "detail": "No model is trained. Supply a rights-cleared, labeled dataset and complete a holdout evaluation.",
        }
    metadata = _read_model_metadata(metadata_path)
    return {"available": True, **metadata}


@router.post("/train")
async def train_model(
    file: UploadFile = File(...),
    target_column: str = Form(min_length=1, max_length=120),
    feature_columns: str = Form(min_length=1, max_length=2000),
    split_column: str = Form(min_length=1, max_length=120),
    split_strategy: str = Form(pattern="^(group|temporal)$"),
    task_type: str = Form(default="regression", pattern="^(regression|classification)$"),
    dataset_source: str = Form(min_length=4, max_length=500),
    dataset_license: str = Form(min_length=2, max_length=200),
    research_use_confirmed: bool = Form(...),
    user: User = Depends(current_user),
) -> dict:
    if not research_use_confirmed:
        raise HTTPException(status_code=403, detail="Confirm that you have rights to use this dataset for research.")
    if Path(file.filename or "").suffix.lower() != ".csv":
        raise HTTPException(status_code=415, detail="Upload a UTF-8 CSV with real labeled observations.")
    raw = await file.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="Training CSV uploads are limited to 20 MiB.")
    columns = [column.strip() for column in feature_columns.split(",") if column.strip()]
    try:
        import joblib

        model, metadata = _train(
            raw,
            file.filename or "training.csv",
            target_column.strip(),
            columns,
            split_column.strip(),
            split_strategy,
            task_type,
        )
    except (ValueError, ImportError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    metadata["dataset_source"] = dataset_source.strip()
    metadata["dataset_license"] = dataset_license.strip()
    metadata["research_use_confirmed"] = True
    metadata["trained_by"] = user.email
    directory = _owner_dir(user, create=True)
    model_path, metadata_path, _ = _artifact_paths(user)
    temporary_model = directory / "model.joblib.tmp"
    temporary_metadata = directory / "model.json.tmp"
    try:
        joblib.dump(model, temporary_model, compress=3)
        temporary_metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        temporary_model.replace(model_path)
        temporary_metadata.replace(metadata_path)
    except OSError as error:
        temporary_model.unlink(missing_ok=True)
        temporary_metadata.unlink(missing_ok=True)
        logger.exception("Research model could not be persisted.")
        raise HTTPException(status_code=500, detail="The trained model could not be saved locally.") from error
    return metadata


@router.post("/predict")
def predict(
    payload: PredictionRequest,
    user: User = Depends(current_user),
) -> dict:
    model_path, metadata_path, history_path = _artifact_paths(user)
    metadata = _read_model_metadata(metadata_path)
    if not model_path.is_file():
        raise HTTPException(status_code=500, detail="The model metadata exists but its artifact is missing.")
    if model_path.is_symlink():
        raise HTTPException(status_code=500, detail="Research model artifacts cannot be symbolic links.")
    features = metadata.get("feature_columns")
    if not isinstance(features, list) or set(payload.features) != set(features):
        raise HTTPException(
            status_code=422,
            detail=f"Provide exactly these feature fields: {', '.join(features or [])}.",
        )
    try:
        import joblib
        import pandas as pd

        model = joblib.load(model_path)
        numeric_features = set(metadata.get("numeric_feature_columns", []))
        values = {
            key: (
                pd.to_numeric(payload.features[key], errors="raise")
                if key in numeric_features and payload.features[key] is not None
                else payload.features[key]
            )
            for key in features
        }
        row = pd.DataFrame([values], columns=features)
        predicted = model.predict(row)[0]
        prediction_value = (
            float(predicted)
            if metadata.get("task_type", "regression") == "regression"
            else str(predicted)
        )
    except (ImportError, OSError, ValueError, TypeError) as error:
        logger.exception("Research prediction failed.")
        raise HTTPException(status_code=500, detail="The saved model could not produce a prediction.") from error
    if isinstance(prediction_value, float) and not math.isfinite(prediction_value):
        raise HTTPException(status_code=500, detail="The model returned a non-finite prediction.")
    result = {
        "model_id": metadata["model_id"],
        "target": metadata["target_column"],
        "prediction": prediction_value,
        "predicted_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": hashlib.sha256(
            json.dumps(payload.features, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "warning": "Research estimate only; not a recommendation or validated farm-level prediction.",
    }
    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with history_path.open("a", encoding="utf-8") as history:
            history.write(json.dumps(result, separators=(",", ":")) + "\n")
    except OSError as error:
        logger.exception("Prediction history could not be saved.")
        raise HTTPException(status_code=500, detail="Prediction succeeded but its history could not be saved.") from error
    return result


@router.get("/history")
def prediction_history(
    limit: int = 20,
    user: User = Depends(current_user),
) -> dict:
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100.")
    _, _, history_path = _artifact_paths(user)
    if not history_path.is_file():
        return {"items": [], "total": 0}
    try:
        with history_path.open("r", encoding="utf-8") as history:
            rows = [json.loads(line) for line in history if line.strip()]
    except (OSError, json.JSONDecodeError) as error:
        logger.exception("Prediction history could not be read.")
        raise HTTPException(status_code=500, detail="Prediction history is unavailable.") from error
    return {"items": rows[-limit:][::-1], "total": len(rows)}
