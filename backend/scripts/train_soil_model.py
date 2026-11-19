"""Train an XGBoost soil model from a real, curated CSV dataset."""

import argparse
import json
from pathlib import Path

from dataset_governance import (
    DatasetEligibilityError,
    approval_key,
    require_training_dataset,
    reviewer_allowlist,
)

FEATURES = ["blue", "green", "red", "red_edge_1", "red_edge_2", "nir", "swir1", "swir2", "elevation", "slope"]
TARGETS = ["soc", "ph", "nitrogen", "phosphorus", "potassium"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="CSV with the documented feature and target columns.")
    parser.add_argument("--dataset-id", required=True, help="Approved source id from the dataset inventory.")
    parser.add_argument("--provenance", type=Path, required=True, help="Sidecar JSON provenance manifest.")
    parser.add_argument(
        "--inventory",
        type=Path,
        default=PROJECT_ROOT / "data" / "metadata" / "source_inventory.json",
    )
    parser.add_argument("--output", type=Path, default=Path("models/soil_xgb.joblib"))
    args = parser.parse_args()

    try:
        require_training_dataset(
            args.dataset_id,
            args.data,
            args.provenance,
            args.inventory,
            reviewer_allowlist(PROJECT_ROOT),
            approval_key(PROJECT_ROOT),
        )
    except DatasetEligibilityError as error:
        raise SystemExit(f"Dataset rejected by commercial eligibility gate: {error}") from None

    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.multioutput import MultiOutputRegressor
    from xgboost import XGBRegressor

    frame = pd.read_csv(args.data)
    required = FEATURES + TARGETS
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise SystemExit(f"Dataset is missing required columns: {', '.join(missing)}")
    values = frame[required].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise SystemExit("Dataset contains missing or non-finite feature/target values; clean it before training.")
    if len(values) < 20:
        raise SystemExit("At least 20 real, labeled samples are required for a train/validation split.")

    x_train, x_test, y_train, y_test = train_test_split(
        values[FEATURES], values[TARGETS], test_size=0.2, random_state=42
    )
    estimator = MultiOutputRegressor(
        XGBRegressor(
            n_estimators=400,
            max_depth=5,
            learning_rate=0.04,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="reg:squarederror",
            n_jobs=-1,
            random_state=42,
        )
    )
    estimator.fit(x_train, y_train)
    predictions = estimator.predict(x_test)
    metrics = {
        target: {
            "mae": float(mean_absolute_error(y_test[target], predictions[:, index])),
            "r2": float(r2_score(y_test[target], predictions[:, index])),
        }
        for index, target in enumerate(TARGETS)
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": estimator, "features": FEATURES, "targets": TARGETS}, args.output)
    metadata = {
        "model_type": "MultiOutputRegressor(XGBRegressor)",
        "training_samples": len(x_train),
        "validation_samples": len(x_test),
        "feature_columns": FEATURES,
        "target_columns": TARGETS,
        "validation_metrics": metrics,
        "source_dataset": args.data.name,
    }
    args.output.with_suffix(".metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
