from copy import deepcopy
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from scripts.black_pepper_pilot_contract import (
    BlackPepperPilotDataset,
    PilotObservation,
    PilotSourceProvenance,
    require_training_eligible,
)


def test_source_provenance_requires_version_license_and_attribution():
    with pytest.raises(ValidationError):
        PilotSourceProvenance(
            source_id="test-source",
            dataset_name="Test-only source",
            publisher="Test fixture",
            dataset_version="not pinned",
            license_name="",
            attribution="Test-only attribution",
            portfolio_permission="UNVERIFIED",
            commercial_use_status="UNVERIFIED",
            ml_training_permission="NOT_ASSESSED",
            data_quality_status="NOT_ASSESSED",
            training_relevance_status="NOT_ASSESSED",
        )


def test_observation_requires_timestamp_and_timezone_aware_utc():
    record = _base_observation()
    record.pop("observed_at")
    with pytest.raises(ValidationError, match="observed_at"):
        PilotObservation.model_validate(record)

    record = _base_observation()
    record["observed_at"] = datetime(2026, 1, 1)
    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        PilotObservation.model_validate(record)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("crop_ref", "unknown-crop", "Unknown crop reference"),
        ("district_ref", "unknown-district", "Unknown district reference"),
    ],
)
def test_dataset_rejects_invalid_catalog_references(field, value, message):
    record = _base_observation()
    record[field] = value
    with pytest.raises(ValidationError, match=message):
        _dataset([record])


def test_observation_rejects_invalid_units():
    record = _base_observation()
    record["unit"] = "mm"
    with pytest.raises(ValidationError, match="canonical unit"):
        PilotObservation.model_validate(record)


def test_dataset_rejects_duplicate_observation_natural_keys():
    first = _base_observation()
    duplicate = deepcopy(first)
    duplicate["observation_id"] = "test-observation-2"
    with pytest.raises(ValidationError, match="Duplicate observation natural key"):
        _dataset([first, duplicate])


def test_training_rejects_sources_without_explicit_training_permission():
    dataset = _dataset(
        [_base_observation()],
        source_overrides={"ml_training_permission": "NOT_ASSESSED"},
    )
    with pytest.raises(ValueError, match="not approved for research training"):
        require_training_eligible(dataset)


def test_unverified_soil_measurement_is_rejected():
    record = _base_observation()
    record.update(
        {
            "variable": "soil_ph",
            "unit": "1",
            "observation_kind": "MEASURED",
            "use_role": "FEATURE",
            "collection_method": "test-only method",
            "estimator_name": None,
            "estimator_version": None,
            "measurement_depth_top_cm": 0,
            "measurement_depth_bottom_cm": 15,
            "verification_status": "PENDING",
        }
    )
    with pytest.raises(ValidationError, match="Soil measurements require verification"):
        PilotObservation.model_validate(record)


def test_estimated_values_require_model_provenance_and_cannot_be_measured():
    record = _base_observation()
    record["estimator_name"] = None
    with pytest.raises(ValidationError, match="estimator name and version"):
        PilotObservation.model_validate(record)

    record = _base_observation()
    record["collection_method"] = "test-only measurement method"
    with pytest.raises(ValidationError, match="cannot be labeled with a measurement method"):
        PilotObservation.model_validate(record)


def test_soil_target_requires_measured_verified_nonmissing_evidence():
    record = _base_observation()
    record.update(
        {
            "variable": "soil_ph",
            "unit": "1",
            "observation_kind": "ESTIMATED",
            "use_role": "TARGET",
            "estimator_name": "Test-only estimator",
            "estimator_version": "test-1",
            "measurement_depth_top_cm": 0,
            "measurement_depth_bottom_cm": 15,
            "verification_status": "VERIFIED",
            "quality_status": "VERIFIED",
        }
    )
    with pytest.raises(ValidationError, match="Soil targets require non-missing"):
        PilotObservation.model_validate(record)


def _base_observation():
    return {
        "observation_id": "test-observation-1",
        "crop_ref": "black-pepper",
        "district_ref": "idukki",
        "source_id": "test-source",
        "source_version": "test-version",
        "spatial_reference_id": "test-spatial-unit",
        "observed_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "variable": "air_temperature",
        "value": None,
        "unit": "degC",
        "missing_value": True,
        "observation_kind": "ESTIMATED",
        "use_role": "FEATURE",
        "estimator_name": "Test-only estimator",
        "estimator_version": "test-1",
        "quality_status": "UNKNOWN",
        "verification_status": "PENDING",
    }


def _dataset(observations, source_overrides=None):
    source = {
        "source_id": "test-source",
        "dataset_name": "Test-only source",
        "publisher": "Test fixture",
        "dataset_version": "test-version",
        "license_name": "Test-only license",
        "attribution": "Test-only attribution",
        "portfolio_permission": "UNVERIFIED",
        "commercial_use_status": "UNVERIFIED",
        "ml_training_permission": "NOT_ASSESSED",
        "data_quality_status": "NOT_ASSESSED",
        "training_relevance_status": "NOT_ASSESSED",
    }
    source.update(source_overrides or {})
    return BlackPepperPilotDataset(
        pilot_version="contract-test",
        crop_references={"black-pepper": "Piper nigrum"},
        district_references={"idukki"},
        sources=[source],
        observations=observations,
    )
