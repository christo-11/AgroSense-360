import hashlib
import json
import zipfile
from pathlib import Path


def _write_temporary_provenance(tmp_path, monkeypatch):
    repository_root = Path(__file__).resolve().parents[2]
    original_metadata = repository_root / "data" / "metadata"
    inventory = json.loads(
        (original_metadata / "source_inventory.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (original_metadata / "era5_land_download_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    quality = json.loads(
        (original_metadata / "era5_land_quality_report.json").read_text(
            encoding="utf-8"
        )
    )

    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    sizes = []
    for request, quality_archive in zip(manifest["requests"], quality["archives"]):
        archive_path = raw_dir / request["filename"]
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("test-payload.bin", b"temporary provenance test")
        archive_bytes = archive_path.read_bytes()
        checksum = hashlib.sha256(archive_bytes).hexdigest()
        size = len(archive_bytes)
        sizes.append(size)
        request.update(
            {
                "local_path": str(archive_path),
                "size_bytes": size,
                "sha256": checksum,
                "content_length_verified": True,
                "zip_crc_valid": True,
                "zip_format_valid": True,
            }
        )
        quality_archive.update(
            {
                "size_bytes": size,
                "sha256": checksum,
                "sha256_matches_acquisition_manifest": True,
                "zip_crc": "PASS",
            }
        )

    era5 = next(item for item in inventory["datasets"] if item["id"] == "era5_land")
    era5.update(
        {
            "download_status": "acquired",
            "download_size_bytes": sum(sizes),
            "acquisition_status": "ACQUIRED_VERIFIED",
            "archive_integrity_status": "VERIFIED",
            "data_quality_status": "QUALITY_REJECTED",
        }
    )
    manifest["dataset_id"] = "era5_land"
    manifest["reconciliation"].update(
        {
            "current_download_status": "acquired",
            "current_acquisition_status": "ACQUIRED_VERIFIED",
            "current_archive_integrity_status": "VERIFIED",
            "current_data_quality_status": "QUALITY_REJECTED",
            "training_eligible": False,
        }
    )

    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()
    for filename, value in (
        ("source_inventory.json", inventory),
        ("era5_land_download_manifest.json", manifest),
        ("era5_land_quality_report.json", quality),
    ):
        (metadata_dir / filename).write_text(
            json.dumps(value), encoding="utf-8"
        )
    monkeypatch.setattr("app.data_intelligence.METADATA_DIR", metadata_dir)
    monkeypatch.setattr("app.data_intelligence.PROJECT_ROOT", tmp_path)
    return inventory, manifest, quality, raw_dir


def test_dataset_inventory_uses_paged_whitelisted_metadata(client):
    response = client.get("/api/v1/data-intelligence/sources?limit=2&offset=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 13
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["items"]) == 2
    assert "local_path" not in payload["items"][0]
    assert "official_urls" not in payload["items"][0]


def test_quality_and_training_eligibility_reflect_review_evidence(client):
    quality = client.get("/api/v1/data-intelligence/quality")
    eligibility = client.get("/api/v1/data-intelligence/training-eligibility")

    assert quality.status_code == 200
    quality_payload = quality.json()
    assert quality_payload["overall_decision"] == "NEEDS_MORE_DATA"
    assert quality_payload["overall_training_status"] == "REJECT_FOR_TRAINING"
    assert [archive["dynamic_timestamp_count"] for archive in quality_payload["archives"]] == [2, 12]
    assert all(
        archive["training_status"] == "REJECT_FOR_TRAINING"
        for archive in quality_payload["archives"]
    )
    assert eligibility.status_code == 200
    eligibility_payload = eligibility.json()
    assert eligibility_payload["eligible_count"] == 0
    era5 = next(item for item in eligibility_payload["items"]["items"] if item["id"] == "era5_land")
    assert era5["eligible_for_training"] is False
    assert any("rejects this source for training" in reason for reason in era5["reasons"])


def test_weather_coverage_uses_quality_report_without_claiming_training_eligibility(client):
    response = client.get("/api/v1/data-intelligence/weather-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert [archive["dynamic_timestamp_count"] for archive in payload["archives"]] == [2, 12]
    assert all(archive["training_status"] == "REJECT_FOR_TRAINING" for archive in payload["archives"])
    assert "not a time series" in payload["note"]


def test_summary_keeps_permission_acquisition_integrity_and_quality_separate(client):
    response = client.get("/api/v1/data-intelligence/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_sources"] == 13
    assert payload["commercial_approval_counts"] == {
        "CONDITIONAL": 11,
        "BLOCKED": 2,
    }
    assert payload["portfolio_status_counts"]["APPROVED_PORTFOLIO_RESEARCH_ONLY"] == 3
    assert payload["acquisition_status_counts"]["ACQUIRED_VERIFIED"] == 1
    assert payload["archive_integrity_status_counts"]["VERIFIED"] == 1
    assert payload["data_quality_status_counts"]["QUALITY_REJECTED"] == 1
    assert payload["training_eligible_count"] == 0


def test_acquisition_response_reconciles_inventory_manifest_and_quality(client):
    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    payload = response.json()
    era5 = next(item for item in payload["items"] if item["id"] == "era5_land")
    assert era5["inventory_status"] == "acquired"
    assert era5["acquisition_status"] == "ACQUIRED_VERIFIED"
    assert era5["archive_integrity_status"] == "VERIFIED"
    assert era5["data_quality_status"] == "QUALITY_REJECTED"
    assert len(era5["artifacts"]) == 2
    assert all(item["acquisition_status"] == "ACQUIRED_VERIFIED" for item in era5["artifacts"])
    assert all(item["checksum_verified"] for item in era5["artifacts"])
    assert "reported by user" in era5["artifacts"][0]["request_status"]
    assert "local_path" not in era5["artifacts"][0]
    assert "source_url" not in era5["artifacts"][0]
    assert "local_path" not in response.text
    assert "source_url" not in response.text
    assert any("MHT was not inspected" in warning for warning in payload["validation_warnings"])


def test_missing_archive_is_reported_without_exposing_its_path(
    client, monkeypatch, tmp_path
):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    missing_path = tmp_path / "data" / "raw" / "missing.zip"
    manifest["requests"][0]["local_path"] = str(missing_path)
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    payload = response.json()
    era5 = next(item for item in payload["items"] if item["id"] == "era5_land")
    assert era5["artifacts"][0]["acquisition_status"] == "MISSING_ARCHIVE"
    assert any("Archive file is missing." in warning for warning in era5["artifacts"][0]["validation_warnings"])
    assert str(missing_path) not in response.text


def test_archive_size_mismatch_is_a_provenance_conflict(client, monkeypatch, tmp_path):
    _, manifest, quality, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest["requests"][0]["size_bytes"] += 1
    quality["archives"][0]["size_bytes"] += 1
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (tmp_path / "metadata" / "era5_land_quality_report.json").write_text(
        json.dumps(quality), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert era5["artifacts"][0]["acquisition_status"] == "PROVENANCE_CONFLICT"
    assert any(
        "Actual archive size does not match the manifest." in warning
        for warning in era5["artifacts"][0]["validation_warnings"]
    )


def test_invalid_checksum_and_timestamp_are_reported(client, monkeypatch, tmp_path):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest["requests"][0]["sha256"] = "not-a-sha256"
    manifest["requests"][1]["retrieved_at"] = "not-a-timestamp"
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert era5["artifacts"][0]["acquisition_status"] == "PROVENANCE_CONFLICT"
    assert era5["artifacts"][1]["acquisition_status"] == "PROVENANCE_CONFLICT"
    assert any("SHA-256" in warning for warning in era5["artifacts"][0]["validation_warnings"])
    assert any("timestamp is invalid" in warning for warning in era5["artifacts"][1]["validation_warnings"])


def test_manifest_and_quality_checksum_mismatch_is_a_conflict(client, monkeypatch, tmp_path):
    _, _, quality, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    quality["archives"][0]["sha256"] = "0" * 64
    (tmp_path / "metadata" / "era5_land_quality_report.json").write_text(
        json.dumps(quality), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert era5["artifacts"][0]["acquisition_status"] == "PROVENANCE_CONFLICT"
    assert any(
        "Manifest and quality-report checksum evidence disagree." in warning
        for warning in era5["artifacts"][0]["validation_warnings"]
    )


def test_missing_archive_location_metadata_is_unverified(client, monkeypatch, tmp_path):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest["requests"][0].pop("local_path")
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert era5["artifacts"][0]["acquisition_status"] == "ACQUIRED_UNVERIFIED"
    assert any(
        "Archive location metadata is missing." in warning
        for warning in era5["artifacts"][0]["validation_warnings"]
    )


def test_duplicate_acquisition_reference_is_reported(client, monkeypatch, tmp_path):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest["requests"][1]["request_reference"] = manifest["requests"][0]["request_reference"]
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert all(item["acquisition_status"] == "PROVENANCE_CONFLICT" for item in era5["artifacts"])
    assert any("Acquisition reference is duplicated." in warning for warning in response.json()["validation_warnings"])


def test_missing_source_identifier_is_not_guessed(client, monkeypatch, tmp_path):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest.pop("dataset_id")
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/acquisitions")

    assert response.status_code == 200
    era5 = next(item for item in response.json()["items"] if item["id"] == "era5_land")
    assert era5["acquisition_status"] == "PROVENANCE_CONFLICT"
    assert era5["artifacts"] == []
    assert any("no source identifier" in warning for warning in response.json()["validation_warnings"])


def test_unknown_approval_status_fails_closed(client, monkeypatch, tmp_path):
    inventory, _, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    inventory["commercial_reviews"]["era5_land"]["approval_status"] = "AUTOMATICALLY_APPROVED"
    (tmp_path / "metadata" / "source_inventory.json").write_text(
        json.dumps(inventory), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/summary")

    assert response.status_code == 503
    assert str(tmp_path) not in response.text


def test_training_eligibility_conflict_is_warned_and_never_grants_clearance(
    client, monkeypatch, tmp_path
):
    _, manifest, _, _ = _write_temporary_provenance(tmp_path, monkeypatch)
    manifest["reconciliation"]["training_eligible"] = True
    (tmp_path / "metadata" / "era5_land_download_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    response = client.get("/api/v1/data-intelligence/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["training_eligible_count"] == 0
    assert any("despite a non-approved source permission" in warning for warning in payload["validation_warnings"])


def test_approval_and_provenance_endpoints_keep_portfolio_and_commercial_status_separate(client):
    approvals = client.get("/api/v1/data-intelligence/approvals")
    provenance = client.get("/api/v1/data-intelligence/provenance")

    assert approvals.status_code == 200
    era5_approval = next(
        item for item in approvals.json()["items"]["items"] if item["id"] == "era5_land"
    )
    assert era5_approval["portfolio_status"] == "APPROVED_PORTFOLIO_RESEARCH_ONLY"
    assert era5_approval["commercial_approval_status"] == "CONDITIONAL"
    assert provenance.status_code == 200
    era5_provenance = next(
        item for item in provenance.json()["items"] if item["id"] == "era5_land"
    )
    assert len(era5_provenance["artifacts"]) == 2
    assert "local_path" not in era5_provenance


def test_catalogue_completeness_is_read_only_and_returns_empty_test_catalogue(client):
    response = client.get("/api/v1/data-intelligence/catalogue-completeness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["districts_total"] == 0
    assert payload["crops_total"] == 0
    assert payload["crop_profile_coverage_percent"] is None


def test_invalid_metadata_fails_closed_without_exposing_file_paths(client, monkeypatch, tmp_path):
    (tmp_path / "source_inventory.json").write_text(
        json.dumps({"datasets": "not-an-array"}),
        encoding="utf-8",
    )
    monkeypatch.setattr("app.data_intelligence.METADATA_DIR", tmp_path)

    response = client.get("/api/v1/data-intelligence/sources")

    assert response.status_code == 503
    assert response.json()["detail"] == "Dataset intelligence metadata is unavailable or invalid."
    assert str(tmp_path) not in response.text


def test_missing_metadata_returns_safe_service_error(client, monkeypatch, tmp_path):
    monkeypatch.setattr("app.data_intelligence.METADATA_DIR", tmp_path)

    response = client.get("/api/v1/data-intelligence/sources")

    assert response.status_code == 503
    assert str(tmp_path) not in response.text
