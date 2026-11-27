"""Local validation contract for a future, evidence-backed pilot dataset.

This module performs no file, network, database, or model operations.
"""

from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


VARIABLE_UNITS = {
    "air_temperature": "degC",
    "precipitation": "mm",
    "relative_humidity": "%",
    "soil_ph": "1",
    "soil_nitrogen": "mg/kg",
    "soil_phosphorus": "mg/kg",
    "soil_potassium": "mg/kg",
    "soil_organic_carbon": "g/kg",
}
SOIL_VARIABLES = frozenset(
    {
        "soil_ph",
        "soil_nitrogen",
        "soil_phosphorus",
        "soil_potassium",
        "soil_organic_carbon",
    }
)


class PilotSourceProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    license_name: str = Field(min_length=1)
    attribution: str = Field(min_length=1)
    portfolio_permission: Literal[
        "APPROVED_PORTFOLIO_RESEARCH_ONLY", "CONDITIONAL", "BLOCKED", "UNVERIFIED"
    ]
    commercial_use_status: Literal["APPROVED", "CONDITIONAL", "BLOCKED", "UNVERIFIED"]
    ml_training_permission: Literal[
        "APPROVED_RESEARCH_ONLY", "APPROVED_COMMERCIAL", "NOT_ASSESSED", "BLOCKED"
    ]
    data_quality_status: Literal["VERIFIED", "NOT_ASSESSED", "REJECTED"]
    training_relevance_status: Literal["VERIFIED", "NOT_ASSESSED", "REJECTED"]

    @field_validator(
        "source_id",
        "dataset_name",
        "publisher",
        "dataset_version",
        "license_name",
        "attribution",
    )
    @classmethod
    def require_concrete_provenance(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or normalized.casefold() in {
            "unknown",
            "not pinned",
            "not verified",
            "not available",
        }:
            raise ValueError("A concrete provenance value is required.")
        return normalized


class PilotObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str = Field(min_length=1)
    crop_ref: str = Field(min_length=1)
    district_ref: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    spatial_reference_id: str = Field(min_length=1)
    season: str | None = None
    observed_at: datetime
    interval_end: datetime | None = None
    variable: Literal[
        "air_temperature",
        "precipitation",
        "relative_humidity",
        "soil_ph",
        "soil_nitrogen",
        "soil_phosphorus",
        "soil_potassium",
        "soil_organic_carbon",
    ]
    value: float | None = Field(default=None, allow_inf_nan=False)
    unit: str = Field(min_length=1)
    missing_value: bool = False
    observation_kind: Literal["MEASURED", "ESTIMATED", "DERIVED", "UNVERIFIED"]
    use_role: Literal["FEATURE", "TARGET", "CONTEXT"]
    collection_method: str | None = None
    estimator_name: str | None = None
    estimator_version: str | None = None
    derivation_method: str | None = None
    measurement_depth_top_cm: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    measurement_depth_bottom_cm: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    quality_status: Literal["VERIFIED", "FLAGGED", "REJECTED", "UNKNOWN"]
    verification_status: Literal["VERIFIED", "PENDING", "REJECTED"]

    @field_validator("observed_at", "interval_end")
    @classmethod
    def require_utc_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is not None and (
            value.tzinfo is None or value.utcoffset() != timedelta(0)
        ):
            raise ValueError("Observation timestamps must be timezone-aware UTC.")
        return value

    @field_validator("collection_method", "estimator_name", "estimator_version", "derivation_method")
    @classmethod
    def normalize_method_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def validate_measurement_contract(self) -> "PilotObservation":
        expected_unit = VARIABLE_UNITS[self.variable]
        if self.unit != expected_unit:
            raise ValueError(
                f"{self.variable} must use canonical unit {expected_unit!r}."
            )
        if self.interval_end is not None and self.interval_end <= self.observed_at:
            raise ValueError("Observation interval end must follow its start.")
        if self.value is None and not self.missing_value:
            raise ValueError("A missing value must be explicitly flagged.")
        if self.value is not None and self.missing_value:
            raise ValueError("A flagged missing value cannot contain a numeric value.")
        if self.variable == "precipitation" and self.value is not None and self.value < 0:
            raise ValueError("Precipitation cannot be negative.")
        if self.variable == "relative_humidity" and self.value is not None and not 0 <= self.value <= 100:
            raise ValueError("Relative humidity must be between 0 and 100 percent.")
        if self.variable == "soil_ph" and self.value is not None and not 0 <= self.value <= 14:
            raise ValueError("Soil pH must be between 0 and 14.")

        if self.variable in SOIL_VARIABLES:
            if (
                self.measurement_depth_top_cm is None
                or self.measurement_depth_bottom_cm is None
                or self.measurement_depth_bottom_cm <= self.measurement_depth_top_cm
            ):
                raise ValueError("Soil observations require a valid depth interval.")
        elif (
            self.measurement_depth_top_cm is not None
            or self.measurement_depth_bottom_cm is not None
        ):
            raise ValueError("Soil depth must not be assigned to a weather variable.")

        if self.observation_kind == "MEASURED":
            if not self.collection_method:
                raise ValueError("Measured observations require a collection method.")
            if self.estimator_name or self.estimator_version or self.derivation_method:
                raise ValueError("Measured observations cannot be labeled as estimated or derived.")
            if self.variable in SOIL_VARIABLES and self.verification_status != "VERIFIED":
                raise ValueError("Soil measurements require verification before acceptance.")
        elif self.observation_kind == "ESTIMATED":
            if not self.estimator_name or not self.estimator_version:
                raise ValueError("Estimated values require an estimator name and version.")
            if self.collection_method:
                raise ValueError("Estimated values cannot be labeled with a measurement method.")
        elif self.observation_kind == "DERIVED" and not self.derivation_method:
            raise ValueError("Derived values require a documented derivation method.")
        elif (
            self.observation_kind == "UNVERIFIED"
            and self.verification_status == "VERIFIED"
        ):
            raise ValueError("Unverified values cannot have verified status.")

        if self.quality_status == "REJECTED" and self.verification_status == "VERIFIED":
            raise ValueError("Rejected observations cannot be verified.")
        if self.use_role == "TARGET" and self.variable in SOIL_VARIABLES:
            if (
                self.observation_kind != "MEASURED"
                or self.verification_status != "VERIFIED"
                or self.quality_status != "VERIFIED"
                or self.missing_value
            ):
                raise ValueError(
                    "Soil targets require non-missing, quality-verified measurements."
                )
        return self


class BlackPepperPilotDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pilot_version: str = Field(min_length=1)
    crop_references: dict[str, str | None]
    district_references: set[str]
    sources: list[PilotSourceProvenance]
    observations: list[PilotObservation]

    @model_validator(mode="after")
    def validate_references_and_uniqueness(self) -> "BlackPepperPilotDataset":
        sources = {source.source_id: source for source in self.sources}
        if len(sources) != len(self.sources):
            raise ValueError("Source identifiers must be unique.")

        seen_observations: set[tuple[object, ...]] = set()
        for observation in self.observations:
            if observation.crop_ref not in self.crop_references:
                raise ValueError(f"Unknown crop reference: {observation.crop_ref}.")
            if observation.district_ref not in self.district_references:
                raise ValueError(f"Unknown district reference: {observation.district_ref}.")
            source = sources.get(observation.source_id)
            if source is None:
                raise ValueError(f"Unknown source reference: {observation.source_id}.")
            if observation.source_version != source.dataset_version:
                raise ValueError("Observation source version does not match its provenance.")

            key = (
                observation.crop_ref,
                observation.district_ref,
                observation.source_id,
                observation.source_version,
                observation.spatial_reference_id,
                observation.variable,
                observation.observed_at,
                observation.interval_end,
                observation.measurement_depth_top_cm,
                observation.measurement_depth_bottom_cm,
            )
            if key in seen_observations:
                raise ValueError("Duplicate observation natural key.")
            seen_observations.add(key)
        return self


def require_training_eligible(
    dataset: BlackPepperPilotDataset, purpose: Literal["research", "commercial"] = "research"
) -> None:
    sources = {source.source_id: source for source in dataset.sources}
    used_source_ids = {observation.source_id for observation in dataset.observations}
    for source_id in used_source_ids:
        source = sources[source_id]
        permitted = (
            {"APPROVED_RESEARCH_ONLY", "APPROVED_COMMERCIAL"}
            if purpose == "research"
            else {"APPROVED_COMMERCIAL"}
        )
        if source.ml_training_permission not in permitted:
            raise ValueError(f"Source {source_id} is not approved for {purpose} training.")
        if source.data_quality_status != "VERIFIED":
            raise ValueError(f"Source {source_id} data quality is not verified.")
        if source.training_relevance_status != "VERIFIED":
            raise ValueError(f"Source {source_id} training relevance is not verified.")

    for observation in dataset.observations:
        if (
            observation.value is None
            or observation.missing_value
            or observation.quality_status != "VERIFIED"
            or observation.verification_status != "VERIFIED"
            or observation.observation_kind == "UNVERIFIED"
        ):
            raise ValueError(
                f"Observation {observation.observation_id} is not eligible for training."
            )
