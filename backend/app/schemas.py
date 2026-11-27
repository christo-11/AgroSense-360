import uuid
from datetime import date, datetime
import math
import re
from typing import Generic, Literal, TypeVar
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def validate_boundary(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Boundary must be a GeoJSON Polygon or MultiPolygon.")
    coordinates = value.get("coordinates")
    polygons = [coordinates] if value["type"] == "Polygon" else coordinates
    if not isinstance(polygons, list) or not polygons:
        raise ValueError("Boundary coordinates must contain at least one polygon.")
    for polygon in polygons:
        if not isinstance(polygon, list) or not polygon:
            raise ValueError("Each polygon must contain at least one linear ring.")
        for ring in polygon:
            if not isinstance(ring, list) or len(ring) < 4:
                raise ValueError("Each boundary ring must contain at least four positions.")
            positions: list[list[float]] = []
            for position in ring:
                if (
                    not isinstance(position, list)
                    or len(position) != 2
                    or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in position)
                ):
                    raise ValueError("Boundary positions must be [longitude, latitude] numeric pairs.")
                longitude, latitude = position
                if (
                    not math.isfinite(longitude)
                    or not math.isfinite(latitude)
                    or not -180 <= longitude <= 180
                    or not -90 <= latitude <= 90
                ):
                    raise ValueError("Boundary coordinates must be finite WGS84 longitude/latitude values.")
                positions.append([longitude, latitude])
            if positions[0] != positions[-1]:
                raise ValueError("Boundary rings must be closed.")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    model_config = ConfigDict(extra="forbid")


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    boundary: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @field_validator("location", mode="before")
    @classmethod
    def strip_location(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("boundary")
    @classmethod
    def check_boundary(cls, value: Any) -> dict[str, Any] | None:
        return validate_boundary(value)


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    boundary: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "location", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("boundary")
    @classmethod
    def check_boundary(cls, value: Any) -> dict[str, Any] | None:
        return validate_boundary(value)


class FarmRead(BaseModel):
    id: uuid.UUID
    name: str
    location: str | None
    boundary: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlotCreate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    crop: str | None = Field(default=None, max_length=120)
    crop_id: uuid.UUID | None = None
    area_value: float | None = Field(default=None, gt=0, le=1_000_000, allow_inf_nan=False)
    area_unit: Literal["acres", "hectares"] | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    longitude: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)
    boundary: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "crop", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_plot_location_and_area(self) -> "PlotCreate":
        if (self.area_value is None) != (self.area_unit is None):
            raise ValueError("Plot area and its unit must be provided together.")
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Plot latitude and longitude must be provided together.")
        return self

    @field_validator("boundary")
    @classmethod
    def check_boundary(cls, value: Any) -> dict[str, Any] | None:
        return validate_boundary(value)


class PlotUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    crop: str | None = Field(default=None, max_length=120)
    crop_id: uuid.UUID | None = None
    area_value: float | None = Field(default=None, gt=0, le=1_000_000, allow_inf_nan=False)
    area_unit: Literal["acres", "hectares"] | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    longitude: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)
    boundary: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "crop", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("boundary")
    @classmethod
    def check_boundary(cls, value: Any) -> dict[str, Any] | None:
        return validate_boundary(value)


class PlotRead(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    crop: str | None
    crop_id: uuid.UUID | None
    area_value: float | None
    area_unit: str | None
    latitude: float | None
    longitude: float | None
    boundary: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class PasswordChange(BaseModel):
    new_password: str = Field(min_length=10, max_length=128)

    model_config = ConfigDict(extra="forbid")


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


def normalized_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


class DistrictRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    state_name: str

    model_config = ConfigDict(from_attributes=True)


class CropCategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class AgriculturalSourceRead(BaseModel):
    id: uuid.UUID
    title: str
    publisher: str
    url: str
    license: str | None
    accessed_on: date | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class AgriculturalSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    publisher: str = Field(min_length=1, max_length=200)
    url: AnyHttpUrl
    license: str | None = Field(default=None, max_length=200)
    accessed_on: date | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "publisher", "license", "notes", mode="before")
    @classmethod
    def strip_source_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("title", "publisher")
    @classmethod
    def require_source_text(cls, value: str) -> str:
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class CropRead(BaseModel):
    id: uuid.UUID
    common_name: str
    slug: str
    scientific_name: str | None
    category: CropCategoryRead
    verification_status: str
    updated_at: datetime


class CropCreate(BaseModel):
    common_name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=160)
    scientific_name: str | None = Field(default=None, max_length=200)
    category_id: uuid.UUID

    model_config = ConfigDict(extra="forbid")

    @field_validator("common_name", "slug", "scientific_name", mode="before")
    @classmethod
    def strip_crop_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ValueError("Slug must use lowercase letters, numbers, and hyphens.")
        return value


class CropUpdate(BaseModel):
    common_name: str | None = Field(default=None, min_length=1, max_length=120)
    scientific_name: str | None = Field(default=None, max_length=200)
    category_id: uuid.UUID | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("common_name", "scientific_name", mode="before")
    @classmethod
    def strip_crop_update_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value


class CropProfileRead(BaseModel):
    crop_id: uuid.UUID
    temperature_min_celsius: float | None
    temperature_max_celsius: float | None
    rainfall_min_mm_year: float | None
    rainfall_max_mm_year: float | None
    soil_type: str | None
    soil_ph_min: float | None
    soil_ph_max: float | None
    planting_season: str | None
    irrigation_requirements: str | None
    fertilizer_recommendations: str | None
    cultivation_practices: str | None
    plant_spacing_min_cm: float | None
    plant_spacing_max_cm: float | None
    growth_duration_min_days: int | None
    growth_duration_max_days: int | None
    harvesting_information: str | None
    common_pests_diseases: list[str]
    expected_yield_min: float | None
    expected_yield_max: float | None
    expected_yield_unit: str | None
    sources: list[AgriculturalSourceRead]
    verification_status: str
    last_updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropProfileUpdate(BaseModel):
    temperature_min_celsius: float | None = Field(default=None, ge=-80, le=80, allow_inf_nan=False)
    temperature_max_celsius: float | None = Field(default=None, ge=-80, le=80, allow_inf_nan=False)
    rainfall_min_mm_year: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    rainfall_max_mm_year: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    soil_type: str | None = None
    soil_ph_min: float | None = Field(default=None, ge=0, le=14, allow_inf_nan=False)
    soil_ph_max: float | None = Field(default=None, ge=0, le=14, allow_inf_nan=False)
    planting_season: str | None = None
    irrigation_requirements: str | None = None
    fertilizer_recommendations: str | None = None
    cultivation_practices: str | None = None
    plant_spacing_min_cm: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    plant_spacing_max_cm: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    growth_duration_min_days: int | None = Field(default=None, ge=0, le=100_000)
    growth_duration_max_days: int | None = Field(default=None, ge=0, le=100_000)
    harvesting_information: str | None = None
    common_pests_diseases: list[str] | None = None
    expected_yield_min: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    expected_yield_max: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    expected_yield_unit: str | None = Field(default=None, max_length=80)
    source_ids: list[uuid.UUID] | None = None
    verification_status: Literal["pending", "verified", "rejected"] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "soil_type",
        "planting_season",
        "irrigation_requirements",
        "fertilizer_recommendations",
        "cultivation_practices",
        "harvesting_information",
        "expected_yield_unit",
        mode="before",
    )
    @classmethod
    def strip_profile_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("common_pests_diseases")
    @classmethod
    def normalize_pests_diseases(cls, value: list[str] | None) -> list[str] | None:
        return [item.strip() for item in value if item.strip()] if value is not None else None

    @model_validator(mode="after")
    def check_ranges(self) -> "CropProfileUpdate":
        pairs = (
            (self.temperature_min_celsius, self.temperature_max_celsius, "temperature"),
            (self.rainfall_min_mm_year, self.rainfall_max_mm_year, "rainfall"),
            (self.soil_ph_min, self.soil_ph_max, "soil pH"),
            (self.plant_spacing_min_cm, self.plant_spacing_max_cm, "plant spacing"),
            (self.growth_duration_min_days, self.growth_duration_max_days, "growth duration"),
            (self.expected_yield_min, self.expected_yield_max, "expected yield"),
        )
        for minimum, maximum, label in pairs:
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(f"{label} minimum cannot exceed its maximum.")
        return self


class CropVarietyRead(BaseModel):
    id: uuid.UUID
    crop_id: uuid.UUID
    name: str
    scientific_name: str | None
    description: str | None
    sources: list[AgriculturalSourceRead]
    verification_status: str
    last_updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropVarietyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    scientific_name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    source_ids: list[uuid.UUID] = Field(default_factory=list)
    verification_status: Literal["pending", "verified", "rejected"] = "pending"

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "scientific_name", "description", mode="before")
    @classmethod
    def strip_variety_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_source_for_verified(self) -> "CropVarietyCreate":
        if self.verification_status == "verified" and not self.source_ids:
            raise ValueError("Verified varieties require at least one source reference.")
        return self


class CropVarietyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    scientific_name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    source_ids: list[uuid.UUID] | None = None
    verification_status: Literal["pending", "verified", "rejected"] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "scientific_name", "description", mode="before")
    @classmethod
    def strip_variety_update_text(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value


class DistrictCropRead(BaseModel):
    id: uuid.UUID
    district_id: uuid.UUID
    crop_id: uuid.UUID
    crop_name: str
    variety_id: uuid.UUID | None
    variety_name: str | None
    suitability_status: str
    verification_status: str
    notes: str | None
    sources: list[AgriculturalSourceRead]
    last_updated_at: datetime


class DistrictCropCreate(BaseModel):
    crop_id: uuid.UUID
    variety_id: uuid.UUID | None = None
    suitability_status: Literal["suitable", "not_suitable", "under_review"] = "under_review"
    verification_status: Literal["pending", "verified", "rejected"] = "pending"
    notes: str | None = None
    source_ids: list[uuid.UUID] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @field_validator("notes", mode="before")
    @classmethod
    def strip_association_notes(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_source_for_verified(self) -> "DistrictCropCreate":
        if self.verification_status == "verified":
            if self.suitability_status == "under_review":
                raise ValueError("A verified association cannot remain under review.")
            if not self.source_ids:
                raise ValueError("Verified district-crop associations require at least one source.")
        return self


class DistrictCropUpdate(BaseModel):
    variety_id: uuid.UUID | None = None
    suitability_status: Literal["suitable", "not_suitable", "under_review"] | None = None
    verification_status: Literal["pending", "verified", "rejected"] | None = None
    notes: str | None = None
    source_ids: list[uuid.UUID] | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("notes", mode="before")
    @classmethod
    def strip_association_update_notes(cls, value: Any) -> Any:
        return value.strip() or None if isinstance(value, str) else value
