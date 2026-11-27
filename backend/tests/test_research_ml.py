import json
from uuid import uuid4

import pandas as pd
import joblib
import numpy as np

from app import research_ml


def _register_and_login(client, test_emails):
    email = f"ml-research-{uuid4().hex}@example.com"
    test_emails.append(email)
    assert client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "research-test-password"},
    ).status_code == 201
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "research-test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_group_split_keeps_groups_separate():
    frame = pd.DataFrame(
        {"farm_id": [f"farm-{index}" for index in range(10) for _ in range(3)]}
    )

    training, holdout = research_ml._split_indices(frame, "group", "farm_id")

    assert set(frame.iloc[training]["farm_id"]).isdisjoint(set(frame.iloc[holdout]["farm_id"]))


def test_ml_status_and_prediction_history_are_available_without_a_trained_model(
    client, test_emails, monkeypatch, tmp_path
):
    monkeypatch.setattr(research_ml, "_storage_root", lambda: tmp_path)
    headers = _register_and_login(client, test_emails)

    assert client.get("/api/v1/research/ml/status", headers=headers).json()["available"] is False
    assert client.get("/api/v1/research/ml/history", headers=headers).json() == {"items": [], "total": 0}
    assert client.post(
        "/api/v1/research/ml/predict",
        headers=headers,
        json={"features": {"temperature": 25}},
    ).status_code == 404


def test_training_requires_explicit_rights_confirmation(client, test_emails, monkeypatch, tmp_path):
    monkeypatch.setattr(research_ml, "_storage_root", lambda: tmp_path)
    headers = _register_and_login(client, test_emails)

    response = client.post(
        "/api/v1/research/ml/train",
        headers=headers,
        data={
            "target_column": "yield",
            "feature_columns": "rainfall",
            "split_column": "farm_id",
            "split_strategy": "group",
            "dataset_source": "Owner-provided research CSV",
            "dataset_license": "Owner-supplied terms",
            "research_use_confirmed": "false",
        },
        files={"file": ("observations.csv", b"yield,rainfall,farm_id\n1,20,farm-1\n", "text/csv")},
    )

    assert response.status_code == 403
    assert response.json()["detail"].startswith("Confirm that you have rights")


class PredictionTestDouble:
    def predict(self, frame):
        assert list(frame.columns) == ["rainfall"]
        return np.array([12.5])


def test_prediction_loads_account_model_and_records_history(client, test_emails, monkeypatch, tmp_path):
    monkeypatch.setattr(research_ml, "_storage_root", lambda: tmp_path)
    email = f"ml-predict-{uuid4().hex}@example.com"
    test_emails.append(email)
    account = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "research-test-password"},
    ).json()
    token = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "research-test-password"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    directory = tmp_path / account["id"]
    directory.mkdir()
    joblib.dump(PredictionTestDouble(), directory / "model.joblib")
    (directory / "model.json").write_text(
        json.dumps(
            {
                "model_id": "test-model",
                "feature_columns": ["rainfall"],
                "numeric_feature_columns": ["rainfall"],
                "target_column": "yield",
            }
        ),
        encoding="utf-8",
    )

    response = client.post(
        "/api/v1/research/ml/predict",
        headers=headers,
        json={"features": {"rainfall": 30}},
    )

    assert response.status_code == 200
    assert response.json()["prediction"] == 12.5
    assert client.get("/api/v1/research/ml/history", headers=headers).json()["items"][0]["input_sha256"]
