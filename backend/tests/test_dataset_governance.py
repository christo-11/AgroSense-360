import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.dataset_governance import (
    DatasetEligibilityError,
    load_inventory,
    record_admin_review,
    require_training_dataset,
)


ADMIN_EMAIL = "dataset-admin@example.com"
ALLOWED_REVIEWERS = frozenset({ADMIN_EMAIL})
SIGNING_KEY = "test-dataset-approval-signing-key-32-bytes"


def _approved_inventory_record(status: str = "APPROVED") -> tuple[dict, dict]:
    source = {
        "id": "licensed-test-resource",
        "name": "Licensed test resource",
        "publisher": "Example Publisher",
        "official_url": "https://example.org/dataset",
        "download_status": "acquired",
        "local_path": "data/raw/example.csv",
    }
    review = {
        "resource_url": "https://example.org/dataset",
        "download_api_url": "https://example.org/download.csv",
        "approval_status": status,
        "commercial_use_status": "PERMITTED",
        "license_name": "Example Commercial License",
        "license_url": "https://example.org/license",
        "attribution_obligations": "Credit Example Publisher",
        "share_alike_obligations": "None",
        "redistribution_restrictions": "None",
        "third_party_rights": "CLEARED",
        "kerala_coverage": "Kerala records verified",
        "district_level_availability": "District field verified",
        "authentication_requirements": "None",
        "access_status": "Resource response verified",
        "verification_date": "2026-11-19",
        "evidence_urls": ["https://example.org/terms"],
        "remaining_concerns": [],
        "reviewed_by": ADMIN_EMAIL,
        "reviewed_at": "2026-11-19T10:00:00+00:00",
        "training_data_quality_status": "VERIFIED",
        "training_relevance_status": "VERIFIED",
    }
    return source, review


def _write_inventory(path: Path, source: dict, review: dict) -> None:
    path.write_text(
        json.dumps({"datasets": [source], "commercial_reviews": {source["id"]: review}}),
        encoding="utf-8",
    )


def _approve_inventory(path: Path, source: dict, review: dict) -> None:
    _write_inventory(path, source, review)
    record_admin_review(
        path,
        source["id"],
        "APPROVED",
        ADMIN_EMAIL,
        ALLOWED_REVIEWERS,
        "Terms and dataset evidence reviewed",
        SIGNING_KEY,
    )


def _write_provenance(data_path: Path, provenance_path: Path, dataset_id: str) -> None:
    provenance = {
        "dataset_id": dataset_id,
        "source_url": "https://example.org/download.csv",
        "source_version": "v1",
        "retrieved_at": "2026-11-19T10:00:00+00:00",
        "license_name": "Example Commercial License",
        "data_path": str(data_path.resolve()),
        "sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
    }
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")


def test_approved_dataset_requires_matching_provenance(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("measured,value\nsample,1\n", encoding="utf-8")
    _approve_inventory(inventory_path, source, review)
    _write_provenance(data_path, provenance_path, source["id"])

    eligible = require_training_dataset(
        source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
    )

    assert eligible["id"] == source["id"]


@pytest.mark.parametrize("status", ["BLOCKED", "CONDITIONAL", "UNVERIFIED"])
def test_non_approved_statuses_are_rejected(status: str, tmp_path: Path) -> None:
    source, review = _approved_inventory_record(status)
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("data", encoding="utf-8")
    _write_inventory(inventory_path, source, review)
    _write_provenance(data_path, provenance_path, source["id"])

    with pytest.raises(DatasetEligibilityError, match=f"is {status}"):
        require_training_dataset(
            source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS
        )


def test_approved_dataset_with_missing_license_is_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    review["license_name"] = ""
    inventory_path = tmp_path / "source_inventory.json"
    _write_inventory(inventory_path, source, review)

    with pytest.raises(DatasetEligibilityError, match="license_name"):
        require_training_dataset(
            source["id"], tmp_path / "missing.csv", tmp_path / "missing.json",
            inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_approved_dataset_with_invalid_source_url_is_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    review["download_api_url"] = "ftp://example.org/data.csv"
    inventory_path = tmp_path / "source_inventory.json"
    _write_inventory(inventory_path, source, review)

    with pytest.raises(DatasetEligibilityError, match="valid HTTP"):
        require_training_dataset(
            source["id"], tmp_path / "missing.csv", tmp_path / "missing.json",
            inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_duplicate_resource_ids_are_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    inventory = {
        "datasets": [source, dict(source)],
        "commercial_reviews": {source["id"]: review},
    }
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(DatasetEligibilityError, match="Duplicate dataset resource id"):
        load_inventory(inventory_path)


def test_provenance_checksum_mismatch_is_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("real data", encoding="utf-8")
    _approve_inventory(inventory_path, source, review)
    _write_provenance(data_path, provenance_path, source["id"])
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["sha256"] = "0" * 64
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")

    with pytest.raises(DatasetEligibilityError, match="checksum"):
        require_training_dataset(
            source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_non_object_provenance_manifest_is_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("data", encoding="utf-8")
    _approve_inventory(inventory_path, source, review)
    provenance_path.write_text("[]", encoding="utf-8")

    with pytest.raises(DatasetEligibilityError, match="must be a JSON object"):
        require_training_dataset(
            source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_tampered_approval_signature_is_rejected(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("data", encoding="utf-8")
    _approve_inventory(inventory_path, source, review)
    _write_provenance(data_path, provenance_path, source["id"])
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["commercial_reviews"][source["id"]]["license_name"] = "Changed license"
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(DatasetEligibilityError, match="signature is missing or invalid"):
        require_training_dataset(
            source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_provenance_must_match_source_url_and_dataset(tmp_path: Path) -> None:
    source, review = _approved_inventory_record()
    inventory_path = tmp_path / "source_inventory.json"
    data_path = tmp_path / "training.csv"
    provenance_path = tmp_path / "provenance.json"
    data_path.write_text("data", encoding="utf-8")
    _approve_inventory(inventory_path, source, review)
    _write_provenance(data_path, provenance_path, source["id"])
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["source_url"] = "https://other.example/download.csv"
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")

    with pytest.raises(DatasetEligibilityError, match="source URL"):
        require_training_dataset(
            source["id"], data_path, provenance_path, inventory_path, ALLOWED_REVIEWERS, SIGNING_KEY
        )


def test_only_allowlisted_reviewer_can_approve(tmp_path: Path) -> None:
    source, review = _approved_inventory_record("UNVERIFIED")
    inventory_path = tmp_path / "source_inventory.json"
    _write_inventory(inventory_path, source, review)

    with pytest.raises(DatasetEligibilityError, match="not in DATASET_REVIEWER_EMAILS"):
        record_admin_review(
            inventory_path,
            source["id"],
            "APPROVED",
            "ordinary-user@example.com",
            ALLOWED_REVIEWERS,
            "Review complete",
            SIGNING_KEY,
        )


def test_blocked_terms_cannot_be_overridden_by_review_status(tmp_path: Path) -> None:
    source, review = _approved_inventory_record("BLOCKED")
    review["commercial_use_status"] = "PROHIBITED"
    inventory_path = tmp_path / "source_inventory.json"
    _write_inventory(inventory_path, source, review)

    with pytest.raises(DatasetEligibilityError, match="not verified as permitted"):
        record_admin_review(
            inventory_path,
            source["id"],
            "APPROVED",
            ADMIN_EMAIL,
            ALLOWED_REVIEWERS,
            "Terms changed",
            SIGNING_KEY,
        )


def test_project_sources_cannot_enter_training_until_approved(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    inventory_path = project_root / "data" / "metadata" / "source_inventory.json"
    source_id = "plantdoc"
    dummy_data = tmp_path / "not-used"
    dummy_manifest = tmp_path / "not-used.json"

    with pytest.raises(DatasetEligibilityError, match="is UNVERIFIED"):
        require_training_dataset(
            source_id, dummy_data, dummy_manifest, inventory_path, ALLOWED_REVIEWERS
        )


def test_project_inventory_keeps_portfolio_rights_separate_from_training_gate() -> None:
    project_root = Path(__file__).resolve().parents[2]
    inventory = load_inventory(project_root / "data" / "metadata" / "source_inventory.json")
    dataset_ids = {dataset["id"] for dataset in inventory["datasets"]}
    portfolio_reviews = inventory["portfolio_reviews"]
    commercial_reviews = inventory["commercial_reviews"]
    allowed_portfolio_statuses = {
        "APPROVED_PORTFOLIO_AND_COMMERCIAL",
        "APPROVED_PORTFOLIO_RESEARCH_ONLY",
        "CONDITIONAL",
        "BLOCKED",
        "UNVERIFIED",
    }

    assert set(portfolio_reviews) == dataset_ids
    assert set(commercial_reviews) == dataset_ids
    assert all(review["status"] in allowed_portfolio_statuses for review in portfolio_reviews.values())
    assert not any(
        review["status"] == "APPROVED_PORTFOLIO_AND_COMMERCIAL"
        for review in portfolio_reviews.values()
    )
    assert portfolio_reviews["open_meteo_historical"]["status"] == "APPROVED_PORTFOLIO_RESEARCH_ONLY"
    assert commercial_reviews["open_meteo_historical"]["approval_status"] == "BLOCKED"
    assert all(
        dataset["dataset_version"] is None and dataset["version_status"] == "NOT_ACQUIRED"
        for dataset in inventory["datasets"]
    )
    assert inventory["stage_status"]["stage_7"].startswith("not_started")
    assert inventory["stage_status"]["stage_8"].startswith("not_started")
    assert inventory["stage_status"]["stage_9"].startswith("not_started")


@pytest.mark.parametrize(
    ("source_id", "expected_status"),
    [
        ("faostat_qcl", "BLOCKED"),
        ("open_meteo_historical", "BLOCKED"),
        ("soilgrids_v2", "CONDITIONAL"),
        ("plantvillage", "UNVERIFIED"),
        ("plantdoc", "UNVERIFIED"),
    ],
)
def test_unapproved_project_sources_fail_before_input_access(
    source_id: str, expected_status: str, tmp_path: Path
) -> None:
    project_root = Path(__file__).resolve().parents[2]
    inventory_path = project_root / "data" / "metadata" / "source_inventory.json"

    with pytest.raises(DatasetEligibilityError, match=f"is {expected_status}"):
        require_training_dataset(
            source_id,
            tmp_path / "input-does-not-exist",
            tmp_path / "provenance-does-not-exist.json",
            inventory_path,
            ALLOWED_REVIEWERS,
        )


@pytest.mark.parametrize("script_name", ["train_soil_model.py", "train_disease_model.py"])
def test_training_entrypoints_reject_blocked_source_before_loading_ml_stack(
    script_name: str, tmp_path: Path
) -> None:
    project_root = Path(__file__).resolve().parents[2]
    script_path = project_root / "backend" / "scripts" / script_name
    output_path = tmp_path / "model-output-must-not-be-created"
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--data",
            str(tmp_path / "input-does-not-exist"),
            "--dataset-id",
            "faostat_qcl",
            "--provenance",
            str(tmp_path / "provenance-does-not-exist.json"),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        check=False,
        cwd=project_root,
        text=True,
    )

    assert result.returncode != 0
    assert "Dataset rejected by commercial eligibility gate" in result.stderr
    assert "is BLOCKED" in result.stderr
    assert not output_path.exists()
