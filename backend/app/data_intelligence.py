import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Crop,
    CropCategory,
    CropProfile,
    CropVariety,
    District,
    DistrictCropSuitability,
)
from app.schemas import Page

logger = logging.getLogger(__name__)
def _project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "data" / "metadata").is_dir():
            return candidate
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _project_root()
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"

router = APIRouter(prefix="/api/v1/data-intelligence", tags=["data intelligence"])
ModelT = TypeVar("ModelT", bound=BaseModel)
APPROVAL_STATUSES = frozenset({"APPROVED", "CONDITIONAL", "BLOCKED", "REJECTED", "UNVERIFIED"})
PORTFOLIO_STATUSES = frozenset(
    {
        "APPROVED_PORTFOLIO_AND_COMMERCIAL",
        "APPROVED_PORTFOLIO_RESEARCH_ONLY",
        "CONDITIONAL",
        "BLOCKED",
        "UNVERIFIED",
    }
)
DOWNLOAD_STATUSES = frozenset(
    {
        "acquired",
        "blocked_pending_commercial_use_decision",
        "metadata_verified_only",
        "not_downloaded",
    }
)
VERSION_STATUSES = frozenset({"ACQUIRED_VERSION_UNPINNED", "NOT_ACQUIRED"})
ACQUISITION_STATUSES = frozenset(
    {
        "ACQUIRED_UNVERIFIED",
        "ACQUIRED_VERIFIED",
        "MISSING_ARCHIVE",
        "NOT_DOWNLOADED",
        "PROVENANCE_CONFLICT",
    }
)
ARCHIVE_INTEGRITY_STATUSES = frozenset({"FAILED", "NOT_ASSESSED", "UNVERIFIED", "VERIFIED"})
DATA_QUALITY_STATUSES = frozenset({"NOT_ASSESSED", "QUALITY_ACCEPTED", "QUALITY_REJECTED"})


class InventoryDataset(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    id: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=300)
    publisher: str = Field(min_length=1, max_length=200)
    license: str | None = Field(default=None, max_length=500)
    dataset_version: str | None = None
    version_status: str = Field(min_length=1)
    download_status: str = Field(min_length=1)
    last_checked: str | None = None
    download_date: str | None = None
    download_size_bytes: int | None = Field(default=None, ge=0)
    acquisition_status: str | None = None
    archive_integrity_status: str | None = None
    data_quality_status: str | None = None

    @field_validator("download_status")
    @classmethod
    def validate_download_status(cls, value: str) -> str:
        if value not in DOWNLOAD_STATUSES:
            raise ValueError("Unknown inventory acquisition status.")
        return value

    @field_validator("version_status")
    @classmethod
    def validate_version_status(cls, value: str) -> str:
        if value not in VERSION_STATUSES:
            raise ValueError("Unknown dataset version status.")
        return value

    @field_validator("acquisition_status")
    @classmethod
    def validate_acquisition_status(cls, value: str | None) -> str | None:
        if value is not None and value not in ACQUISITION_STATUSES:
            raise ValueError("Unknown reconciled acquisition status.")
        return value

    @field_validator("archive_integrity_status")
    @classmethod
    def validate_archive_integrity_status(cls, value: str | None) -> str | None:
        if value is not None and value not in ARCHIVE_INTEGRITY_STATUSES:
            raise ValueError("Unknown archive integrity status.")
        return value

    @field_validator("data_quality_status")
    @classmethod
    def validate_data_quality_status(cls, value: str | None) -> str | None:
        if value is not None and value not in DATA_QUALITY_STATUSES:
            raise ValueError("Unknown data quality status.")
        return value

    @field_validator("download_date")
    @classmethod
    def validate_download_date(cls, value: str | None) -> str | None:
        if value is not None:
            date.fromisoformat(value)
        return value


class CommercialReview(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    approval_status: str = Field(min_length=1)
    commercial_use_status: str = Field(min_length=1)
    training_data_quality_status: str = Field(min_length=1)
    training_relevance_status: str = Field(min_length=1)

    @field_validator("approval_status")
    @classmethod
    def validate_approval_status(cls, value: str) -> str:
        if value not in APPROVAL_STATUSES:
            raise ValueError("Unknown commercial approval status.")
        return value


class PortfolioReview(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    status: str = Field(min_length=1)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in PORTFOLIO_STATUSES:
            raise ValueError("Unknown portfolio approval status.")
        return value


class InventoryMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    datasets: list[InventoryDataset]
    commercial_reviews: dict[str, CommercialReview]
    portfolio_reviews: dict[str, PortfolioReview]

    @model_validator(mode="after")
    def validate_review_references(self) -> "InventoryMetadata":
        ids = [dataset.id for dataset in self.datasets]
        if len(ids) != len(set(ids)):
            raise ValueError("Dataset identifiers must be unique.")
        expected = set(ids)
        if set(self.commercial_reviews) != expected or set(self.portfolio_reviews) != expected:
            raise ValueError("Every dataset must have one portfolio and commercial review.")
        return self


class ManifestRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    request_number: int = Field(gt=0)
    filename: str = Field(min_length=1, max_length=255)
    request_status: str = Field(min_length=1, max_length=200)
    request_reference: str | None = None
    retrieved_at: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    sha256: str | None = None
    content_length_verified: bool | None = None
    zip_crc_valid: bool | None = None
    zip_format_valid: bool | None = None
    local_path: str | None = None
    user_reported_approx_size: str | None = None

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if "/" in value or "\\" in value or value in {".", ".."}:
            raise ValueError("Artifact filename must not contain a path.")
        return value


class ProvenanceReconciliation(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    reconciled_at: str = Field(min_length=1)
    status: str = Field(min_length=1)
    previous_inventory_last_checked: str = Field(min_length=1)
    previous_download_status: str = Field(min_length=1)
    previous_version_status: str = Field(min_length=1)
    current_download_status: str = Field(min_length=1)
    current_acquisition_status: str = Field(min_length=1)
    current_archive_integrity_status: str = Field(min_length=1)
    current_data_quality_status: str = Field(min_length=1)
    current_version_status: str = Field(min_length=1)
    training_eligible: bool
    evidence: list[str]
    validation_warnings: list[str]

    @field_validator("reconciled_at")
    @classmethod
    def validate_reconciled_at(cls, value: str) -> str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("Reconciliation timestamp must include a timezone.")
        return value

    @field_validator("previous_inventory_last_checked")
    @classmethod
    def validate_previous_inventory_date(cls, value: str) -> str:
        date.fromisoformat(value)
        return value

    @field_validator("status")
    @classmethod
    def validate_reconciliation_status(cls, value: str) -> str:
        if value != "RECONCILED_WITH_LIMITATIONS":
            raise ValueError("Unknown reconciliation status.")
        return value

    @field_validator("previous_download_status", "current_download_status")
    @classmethod
    def validate_inventory_download_status(cls, value: str) -> str:
        if value not in DOWNLOAD_STATUSES:
            raise ValueError("Unknown reconciliation inventory status.")
        return value

    @field_validator("previous_version_status", "current_version_status")
    @classmethod
    def validate_inventory_version_status(cls, value: str) -> str:
        if value not in VERSION_STATUSES:
            raise ValueError("Unknown reconciliation version status.")
        return value

    @field_validator("current_acquisition_status")
    @classmethod
    def validate_reconciliation_acquisition_status(cls, value: str) -> str:
        if value not in ACQUISITION_STATUSES:
            raise ValueError("Unknown reconciliation acquisition status.")
        return value

    @field_validator("current_archive_integrity_status")
    @classmethod
    def validate_reconciliation_integrity_status(cls, value: str) -> str:
        if value not in ARCHIVE_INTEGRITY_STATUSES:
            raise ValueError("Unknown reconciliation archive integrity status.")
        return value

    @field_validator("current_data_quality_status")
    @classmethod
    def validate_reconciliation_quality_status(cls, value: str) -> str:
        if value not in DATA_QUALITY_STATUSES:
            raise ValueError("Unknown reconciliation data quality status.")
        return value


class ManifestMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    dataset_name: str = Field(min_length=1)
    dataset_id: str | None = Field(
        default=None, pattern=r"^[a-z0-9][a-z0-9_-]*$"
    )
    requests: list[ManifestRequest]
    request_metadata_limitations: list[str] = Field(default_factory=list)
    reconciliation: ProvenanceReconciliation | None = None


class QualityArchiveEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    request_number: int | None = None
    format: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    sha256: str | None = None
    sha256_matches_acquisition_manifest: bool | None = None
    zip_crc: str | None = None


class QualityArchiveMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    decision: str = Field(min_length=1)
    training_status: str = Field(min_length=1)
    distinct_dynamic_timestamp_count: int | None = Field(default=None, ge=0)
    distinct_dynamic_timestamps_utc: list[str] | None = None
    dynamic_timestamp_count_per_variable: list[int] | None = None
    dynamic_variable_count: int | None = Field(default=None, ge=0)
    dynamic_data_coverage_utc: dict[str, str] | None = None
    dynamic_coverage_utc: dict[str, str] | None = None
    observed_interval_seconds: list[int] | None = None
    observed_gaps_seconds: list[int] | None = None
    global_grid_missingness: dict[str, Any]

    @model_validator(mode="after")
    def validate_quality_metrics(self) -> "QualityArchiveMetadata":
        if self.distinct_dynamic_timestamp_count is None and not self.distinct_dynamic_timestamps_utc:
            raise ValueError("Dynamic timestamp evidence is required.")
        if self.dynamic_timestamp_count_per_variable is not None and any(
            count < 0 for count in self.dynamic_timestamp_count_per_variable
        ):
            raise ValueError("Timestamp counts must not be negative.")
        if any(value < 0 for value in self.observed_interval_seconds or []):
            raise ValueError("Observed intervals must not be negative.")
        if any(value < 0 for value in self.observed_gaps_seconds or []):
            raise ValueError("Observed gaps must not be negative.")
        fraction = self.global_grid_missingness.get(
            "fraction", self.global_grid_missingness.get("fraction_dynamic")
        )
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not 0 <= fraction <= 1:
            raise ValueError("Global missingness fraction must be between zero and one.")
        return self

    @property
    def timestamp_count(self) -> int:
        if self.distinct_dynamic_timestamp_count is not None:
            return self.distinct_dynamic_timestamp_count
        return len(self.distinct_dynamic_timestamps_utc or [])


class QualityMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    overall_decision: str = Field(min_length=1)
    overall_training_status: str = Field(min_length=1)
    archives: list[QualityArchiveEvidence] = Field(default_factory=list)
    request_1: QualityArchiveMetadata
    request_2: QualityArchiveMetadata


class DataSourceSummary(BaseModel):
    id: str
    name: str
    publisher: str
    license: str | None
    dataset_version: str | None
    version_status: str
    portfolio_status: str
    commercial_approval_status: str
    commercial_use_status: str
    inventory_acquisition_status: str
    acquisition_status: str
    archive_integrity_status: str
    data_quality_status: str
    validation_warnings: list[str]
    last_checked: str | None


class DataSourceApproval(BaseModel):
    id: str
    name: str
    portfolio_status: str
    commercial_approval_status: str
    commercial_use_status: str


class DataSourceArtifact(BaseModel):
    request_number: int
    filename: str
    request_status: str
    retrieved_at: datetime | None
    size_bytes: int | None
    actual_size_bytes: int | None
    sha256: str | None
    checksum_verified: bool
    content_length_verified: bool | None
    zip_crc_valid: bool | None
    zip_format_valid: bool | None
    acquisition_status: str
    archive_integrity_status: str
    data_quality_status: str
    status_explanation: str
    validation_warnings: list[str]


class DataSourceAcquisition(BaseModel):
    id: str
    name: str
    inventory_status: str
    acquisition_status: str
    archive_integrity_status: str
    data_quality_status: str
    status_explanation: str
    validation_warnings: list[str]
    artifacts: list[DataSourceArtifact]


class WeatherArchiveQuality(BaseModel):
    request_number: int
    decision: str
    training_status: str
    dynamic_timestamp_count: int
    coverage_start_utc: str | None
    coverage_end_utc: str | None
    observed_gap_hours: list[float]
    global_grid_missing_fraction: float
    missingness_scope: str
    warning: str


class DataQualityResponse(BaseModel):
    overall_decision: str
    overall_training_status: str
    archives: list[WeatherArchiveQuality]


class WeatherCoverageResponse(BaseModel):
    archives: list[WeatherArchiveQuality]
    note: str


class TrainingEligibilityItem(BaseModel):
    id: str
    name: str
    eligible_for_training: bool
    status: str
    reasons: list[str]


class TrainingEligibilityResponse(BaseModel):
    total_sources: int
    eligible_count: int
    items: Page[TrainingEligibilityItem]
    note: str


class DataProvenanceItem(BaseModel):
    id: str
    name: str
    publisher: str
    license: str | None
    dataset_version: str | None
    version_status: str
    last_checked: str | None
    acquisition_status: str
    archive_integrity_status: str
    data_quality_status: str
    validation_warnings: list[str]
    artifacts: list[DataSourceArtifact]


class CatalogueCompletenessResponse(BaseModel):
    districts_total: int
    crop_categories_total: int
    crops_total: int
    crop_profiles_total: int
    verified_crop_profiles: int
    crop_profile_coverage_percent: float | None
    crop_varieties_total: int
    districts_with_suitability: int
    district_crop_associations_total: int
    district_suitability_coverage_percent: float | None


class DataIntelligenceSummary(BaseModel):
    total_sources: int
    portfolio_status_counts: dict[str, int]
    commercial_approval_counts: dict[str, int]
    inventory_acquisition_counts: dict[str, int]
    acquisition_status_counts: dict[str, int]
    archive_integrity_status_counts: dict[str, int]
    data_quality_status_counts: dict[str, int]
    manifest_request_count: int
    manifest_reported_success_count: int
    training_eligible_count: int
    weather_decision: str
    weather_training_status: str
    metadata_warnings: list[str]
    validation_warnings: list[str]


class DatasetInventoryPage(Page[DataSourceSummary]):
    pass


class DatasetApprovalPage(BaseModel):
    total: int
    counts: dict[str, int]
    items: Page[DataSourceApproval]


class DatasetAcquisitionPage(Page[DataSourceAcquisition]):
    validation_warnings: list[str] = Field(default_factory=list)


class DatasetProvenancePage(Page[DataProvenanceItem]):
    pass


def _metadata_unavailable(filename: str) -> None:
    logger.error("Data intelligence metadata file %s is unavailable or invalid.", filename)
    raise HTTPException(
        status_code=503,
        detail="Dataset intelligence metadata is unavailable or invalid.",
    )


def _read_metadata(filename: str, model: type[ModelT]) -> ModelT:
    try:
        content = (METADATA_DIR / filename).read_text(encoding="utf-8")
        raw_data = json.loads(content)
        return model.model_validate(raw_data)
    except FileNotFoundError:
        _metadata_unavailable(filename)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError):
        _metadata_unavailable(filename)
    raise RuntimeError("Unreachable metadata validation branch.")


def _inventory() -> InventoryMetadata:
    return _read_metadata("source_inventory.json", InventoryMetadata)


def _manifest() -> ManifestMetadata:
    return _read_metadata("era5_land_download_manifest.json", ManifestMetadata)


def _quality() -> QualityMetadata:
    return _read_metadata("era5_land_quality_report.json", QualityMetadata)


@dataclass(frozen=True)
class ProvenanceAssessment:
    acquisition_status: str
    archive_integrity_status: str
    data_quality_status: str
    status_explanation: str
    validation_warnings: list[str]
    artifacts: list[DataSourceArtifact]


def _append_warning(warnings: list[str], warning: str) -> None:
    if warning not in warnings:
        warnings.append(warning)


def _parse_utc_timestamp(value: str | None) -> tuple[datetime | None, str | None]:
    if value is None:
        return None, "Acquisition timestamp is missing."
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None, "Acquisition timestamp is invalid."
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, "Acquisition timestamp has no timezone."
    return parsed, None


def _sha256_is_valid(value: str | None) -> bool:
    return value is not None and re.fullmatch(r"[a-fA-F0-9]{64}", value) is not None


def _resolve_archive(local_path: str | None) -> tuple[Path | None, str | None]:
    if not local_path:
        return None, "Archive location metadata is missing."
    try:
        candidate = Path(local_path)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if candidate.is_symlink():
            return None, "Archive location resolves through a symbolic link."
        resolved = candidate.resolve(strict=False)
        root = PROJECT_ROOT.resolve()
        if resolved != root and root not in resolved.parents:
            return None, "Archive location is outside the project data boundary."
        return resolved, None
    except (OSError, RuntimeError, ValueError):
        return None, "Archive location could not be safely resolved."


def _status_explanation(
    acquisition_status: str,
    integrity_status: str,
    quality_status: str,
) -> str:
    explanations = {
        "ACQUIRED_VERIFIED": (
            "The archive exists and its recorded size, checksum comparison, format, and ZIP "
            "integrity agree with the available acquisition and quality records. This does not "
            "establish training eligibility."
        ),
        "ACQUIRED_UNVERIFIED": (
            "An acquisition is recorded, but one or more archive provenance checks are incomplete."
        ),
        "MISSING_ARCHIVE": (
            "The acquisition record exists, but the archive file is not present at its recorded location."
        ),
        "PROVENANCE_CONFLICT": (
            "The inventory, acquisition manifest, quality report, or archive evidence disagree."
        ),
        "NOT_DOWNLOADED": "No acquired archive is recorded for this source.",
    }
    explanation = explanations.get(
        acquisition_status,
        "Acquisition status could not be determined from the available metadata.",
    )
    if integrity_status == "FAILED":
        explanation += " Archive integrity checks failed."
    elif integrity_status == "UNVERIFIED":
        explanation += " Archive integrity is not fully verified."
    if quality_status == "QUALITY_REJECTED":
        explanation += " Data quality is rejected for model training."
    return explanation


def _quality_by_request(
    quality: QualityMetadata,
) -> tuple[dict[int, QualityArchiveEvidence], set[int], list[str]]:
    records: dict[int, QualityArchiveEvidence] = {}
    duplicates: set[int] = set()
    warnings: list[str] = []
    for archive in quality.archives:
        if archive.request_number is None:
            _append_warning(warnings, "A quality-report archive has no acquisition request identifier.")
            continue
        if archive.request_number in records:
            duplicates.add(archive.request_number)
        else:
            records[archive.request_number] = archive
    if duplicates:
        _append_warning(warnings, "The quality report contains duplicate acquisition request identifiers.")
    return records, duplicates, warnings


def _request_assessment(
    request: ManifestRequest,
    quality_archive: QualityArchiveEvidence | None,
    quality_metadata: QualityArchiveMetadata | None,
    duplicate_request: bool,
    duplicate_reference: bool,
    quality_duplicate: bool,
) -> DataSourceArtifact:
    warnings: list[str] = []
    conflict = duplicate_request or duplicate_reference or quality_duplicate
    if duplicate_request:
        _append_warning(warnings, "Acquisition request identifier is duplicated.")
    if duplicate_reference:
        _append_warning(warnings, "Acquisition reference is duplicated.")
    if quality_duplicate:
        _append_warning(warnings, "Quality report repeats this acquisition request identifier.")

    retrieved_at, timestamp_warning = _parse_utc_timestamp(request.retrieved_at)
    if timestamp_warning:
        _append_warning(warnings, timestamp_warning)
        conflict = conflict or request.retrieved_at is not None

    if not request.request_reference:
        _append_warning(warnings, "Acquisition reference is missing.")
        conflict = True
    if not request.request_status.casefold().startswith("successful"):
        _append_warning(warnings, "Manifest does not report a successful acquisition.")
        conflict = True

    archive_path, path_warning = _resolve_archive(request.local_path)
    actual_size: int | None = None
    missing_archive = False
    if path_warning:
        _append_warning(warnings, path_warning)
        conflict = conflict or path_warning != "Archive location metadata is missing."
        if path_warning != "Archive location metadata is missing.":
            logger.warning(
                "Dataset archive path validation failed for acquisition request %d.",
                request.request_number,
            )
    elif archive_path is not None:
        try:
            if not archive_path.is_file():
                missing_archive = True
                _append_warning(warnings, "Archive file is missing.")
                logger.warning(
                    "Dataset archive is missing for acquisition request %d.",
                    request.request_number,
                )
            else:
                actual_size = archive_path.stat().st_size
        except OSError as error:
            _append_warning(warnings, "Archive file could not be inspected.")
            logger.warning(
                "Dataset archive inspection failed for request %d (%s).",
                request.request_number,
                type(error).__name__,
            )

    if request.size_bytes is None:
        _append_warning(warnings, "Acquisition archive size is missing.")
    elif actual_size is not None and actual_size != request.size_bytes:
        _append_warning(warnings, "Actual archive size does not match the manifest.")
        conflict = True
    if request.content_length_verified is False:
        _append_warning(warnings, "Manifest content-length verification failed.")
        conflict = True
    elif request.content_length_verified is None:
        _append_warning(warnings, "Manifest content-length verification is not recorded.")

    if quality_archive is None:
        _append_warning(warnings, "No archive-level quality evidence matches this request.")
    else:
        if quality_archive.request_number != request.request_number:
            _append_warning(warnings, "Quality-report request identifier does not match the manifest.")
            conflict = True
        if request.size_bytes is None or quality_archive.size_bytes is None:
            _append_warning(warnings, "Quality-report archive size evidence is incomplete.")
        elif request.size_bytes != quality_archive.size_bytes:
            _append_warning(warnings, "Manifest and quality-report archive sizes differ.")
            conflict = True

    checksum_verified = False
    if not _sha256_is_valid(request.sha256):
        _append_warning(warnings, "Manifest checksum is missing or is not a valid SHA-256 digest.")
        conflict = conflict or request.sha256 is not None
    if quality_archive is None or quality_archive.sha256 is None:
        _append_warning(warnings, "Quality-report checksum evidence is missing or invalid.")
    elif not _sha256_is_valid(quality_archive.sha256):
        _append_warning(warnings, "Quality-report checksum evidence is missing or invalid.")
        conflict = True
    elif _sha256_is_valid(request.sha256):
        if (
            quality_archive.sha256.casefold() != request.sha256.casefold()
            or quality_archive.sha256_matches_acquisition_manifest is not True
        ):
            _append_warning(warnings, "Manifest and quality-report checksum evidence disagree.")
            conflict = True
        else:
            checksum_verified = True

    if quality_archive is not None and quality_archive.zip_crc not in (None, "PASS"):
        _append_warning(warnings, "Quality report does not record a passing ZIP CRC check.")
    if request.zip_crc_valid is not True:
        _append_warning(warnings, "Manifest does not record a passing ZIP CRC check.")
    if (
        quality_archive is not None
        and quality_archive.zip_crc is not None
        and (quality_archive.zip_crc == "PASS") != (request.zip_crc_valid is True)
    ):
        _append_warning(warnings, "Manifest and quality-report ZIP CRC evidence disagree.")
        conflict = True
    if request.zip_format_valid is not True:
        _append_warning(warnings, "Manifest does not record a valid ZIP format.")

    quality_status = "NOT_ASSESSED"
    if quality_metadata is not None:
        if (
            quality_metadata.training_status == "REJECT_FOR_TRAINING"
            or quality_metadata.decision == "NEEDS_MORE_DATA"
        ):
            quality_status = "QUALITY_REJECTED"
        elif quality_metadata.training_status != "ELIGIBLE_FOR_TRAINING":
            _append_warning(warnings, "Quality report does not establish training eligibility.")

    integrity_checks_pass = (
        archive_path is not None
        and actual_size is not None
        and request.size_bytes == actual_size
        and checksum_verified
        and request.zip_crc_valid is True
        and request.zip_format_valid is True
        and quality_archive is not None
        and quality_archive.zip_crc == "PASS"
        and bool(quality_archive.format)
    )
    if conflict:
        acquisition_status = "PROVENANCE_CONFLICT"
    elif missing_archive:
        acquisition_status = "MISSING_ARCHIVE"
    elif integrity_checks_pass and retrieved_at is not None:
        acquisition_status = "ACQUIRED_VERIFIED"
    else:
        acquisition_status = "ACQUIRED_UNVERIFIED"
    if acquisition_status == "PROVENANCE_CONFLICT":
        logger.warning(
            "Dataset provenance conflict was found for acquisition request %d.",
            request.request_number,
        )

    if conflict or (quality_archive is not None and quality_archive.zip_crc not in (None, "PASS")):
        integrity_status = "FAILED"
    elif integrity_checks_pass:
        integrity_status = "VERIFIED"
    elif archive_path is not None and actual_size is not None:
        integrity_status = "UNVERIFIED"
    else:
        integrity_status = "NOT_ASSESSED"

    explanation = _status_explanation(
        acquisition_status, integrity_status, quality_status
    )
    return DataSourceArtifact(
        request_number=request.request_number,
        filename=request.filename,
        request_status=request.request_status,
        retrieved_at=retrieved_at,
        size_bytes=request.size_bytes,
        actual_size_bytes=actual_size,
        sha256=request.sha256 if _sha256_is_valid(request.sha256) else None,
        checksum_verified=checksum_verified,
        content_length_verified=request.content_length_verified,
        zip_crc_valid=request.zip_crc_valid,
        zip_format_valid=request.zip_format_valid,
        acquisition_status=acquisition_status,
        archive_integrity_status=integrity_status,
        data_quality_status=quality_status,
        status_explanation=explanation,
        validation_warnings=warnings,
    )


def _reconcile_provenance(
    inventory: InventoryMetadata,
    manifest: ManifestMetadata,
    quality: QualityMetadata,
) -> tuple[dict[str, ProvenanceAssessment], list[str]]:
    warnings: list[str] = []
    assessments: dict[str, ProvenanceAssessment] = {}
    dataset_ids = {dataset.id for dataset in inventory.datasets}
    dataset_id = manifest.dataset_id
    matched_dataset = next(
        (dataset for dataset in inventory.datasets if dataset.id == dataset_id), None
    )

    if not dataset_id:
        _append_warning(warnings, "Acquisition manifest has no source identifier; its records cannot be attributed safely.")
    elif dataset_id not in dataset_ids:
        _append_warning(warnings, "Acquisition manifest refers to an unknown source identifier.")

    if manifest.reconciliation is None:
        _append_warning(warnings, "Provenance reconciliation audit trail is missing.")
    else:
        if manifest.reconciliation.training_eligible and matched_dataset is not None:
            commercial = inventory.commercial_reviews[matched_dataset.id]
            if commercial.approval_status != "APPROVED":
                _append_warning(
                    warnings,
                    "Audit trail claims training eligibility despite a non-approved source permission status.",
                )
            elif quality.overall_training_status == "REJECT_FOR_TRAINING":
                _append_warning(
                    warnings,
                    "Audit trail claims training eligibility despite a rejected data quality status.",
                )

    limitations = " ".join(manifest.request_metadata_limitations).casefold()
    if "mht" in limitations:
        _append_warning(
            warnings,
            "Exact CDS request parameters remain unconfirmed because the supplied request-history MHT was not inspected.",
        )
    if "reversed" in limitations:
        _append_warning(
            warnings,
            "User-reported approximate sizes differ from the observed archive sizes; the original estimates are retained.",
        )

    quality_records, duplicate_quality_ids, quality_warnings = _quality_by_request(quality)
    for warning in quality_warnings:
        _append_warning(warnings, warning)

    request_number_counts = Counter(request.request_number for request in manifest.requests)
    quality_request_mismatch = (
        set(quality_records) != {request.request_number for request in manifest.requests}
    )
    if quality_request_mismatch:
        _append_warning(warnings, "Manifest and quality report do not contain matching request identifiers.")
    quality_archives = (quality.request_1, quality.request_2)
    archive_training_rejections = [
        archive.training_status == "REJECT_FOR_TRAINING"
        for archive in quality_archives
    ]
    archive_quality_rejections = [
        archive.decision == "NEEDS_MORE_DATA"
        for archive in quality_archives
    ]
    quality_decision_mismatch = (
        (
            quality.overall_training_status == "REJECT_FOR_TRAINING"
            and not all(archive_training_rejections)
        )
        or (
            quality.overall_training_status != "REJECT_FOR_TRAINING"
            and any(archive_training_rejections)
        )
        or (
            quality.overall_decision == "NEEDS_MORE_DATA"
            and not all(archive_quality_rejections)
        )
        or (
            quality.overall_decision != "NEEDS_MORE_DATA"
            and any(archive_quality_rejections)
        )
    )
    if quality_decision_mismatch:
        _append_warning(warnings, "Overall and archive-level training quality decisions disagree.")
    reference_counts = Counter(
        request.request_reference
        for request in manifest.requests
        if request.request_reference is not None
    )

    if matched_dataset is not None:
        artifacts: list[DataSourceArtifact] = []
        for request in manifest.requests:
            quality_archive = quality_records.get(request.request_number)
            quality_metadata = (
                getattr(quality, f"request_{request.request_number}", None)
                if request.request_number in (1, 2)
                else None
            )
            artifact = _request_assessment(
                request=request,
                quality_archive=quality_archive,
                quality_metadata=quality_metadata,
                duplicate_request=request_number_counts[request.request_number] > 1,
                duplicate_reference=(
                    request.request_reference is not None
                    and reference_counts[request.request_reference] > 1
                ),
                quality_duplicate=request.request_number in duplicate_quality_ids,
            )
            artifacts.append(artifact)
            for warning in artifact.validation_warnings:
                _append_warning(warnings, warning)

        statuses = [artifact.acquisition_status for artifact in artifacts]
        acquisition_status = "NOT_DOWNLOADED"
        if "PROVENANCE_CONFLICT" in statuses:
            acquisition_status = "PROVENANCE_CONFLICT"
        elif "MISSING_ARCHIVE" in statuses:
            acquisition_status = "MISSING_ARCHIVE"
        elif "ACQUIRED_UNVERIFIED" in statuses:
            acquisition_status = "ACQUIRED_UNVERIFIED"
        elif statuses and all(status == "ACQUIRED_VERIFIED" for status in statuses):
            acquisition_status = "ACQUIRED_VERIFIED"
        if quality_request_mismatch or quality_decision_mismatch:
            acquisition_status = "PROVENANCE_CONFLICT"

        integrity_status = "NOT_ASSESSED"
        integrity_statuses = [artifact.archive_integrity_status for artifact in artifacts]
        if "FAILED" in integrity_statuses:
            integrity_status = "FAILED"
        elif integrity_statuses and all(status == "VERIFIED" for status in integrity_statuses):
            integrity_status = "VERIFIED"
        elif any(status == "UNVERIFIED" for status in integrity_statuses):
            integrity_status = "UNVERIFIED"

        quality_status = (
            "QUALITY_REJECTED"
            if any(artifact.data_quality_status == "QUALITY_REJECTED" for artifact in artifacts)
            else "NOT_ASSESSED"
        )
        actual_total_size = sum(
            artifact.actual_size_bytes or 0 for artifact in artifacts
        )
        if (
            matched_dataset.download_size_bytes is not None
            and all(artifact.actual_size_bytes is not None for artifact in artifacts)
            and matched_dataset.download_size_bytes != actual_total_size
        ):
            acquisition_status = "PROVENANCE_CONFLICT"
            _append_warning(
                warnings,
                "Source inventory aggregate archive size does not match the observed files.",
            )
        inventory_mismatches = (
            matched_dataset.download_status != "acquired"
            or matched_dataset.acquisition_status != acquisition_status
            or matched_dataset.archive_integrity_status != integrity_status
            or matched_dataset.data_quality_status != quality_status
        )
        if inventory_mismatches:
            if acquisition_status not in ("MISSING_ARCHIVE", "PROVENANCE_CONFLICT"):
                acquisition_status = "PROVENANCE_CONFLICT"
            _append_warning(
                warnings,
                "The source inventory's recorded provenance statuses do not match the reconciled evidence.",
            )

        current_inventory_state = manifest.reconciliation
        if current_inventory_state is None or (
            current_inventory_state.current_download_status
            != matched_dataset.download_status
            or current_inventory_state.current_acquisition_status
            != matched_dataset.acquisition_status
            or current_inventory_state.current_archive_integrity_status
            != matched_dataset.archive_integrity_status
            or current_inventory_state.current_data_quality_status
            != matched_dataset.data_quality_status
            or current_inventory_state.current_version_status
            != matched_dataset.version_status
        ):
            acquisition_status = "PROVENANCE_CONFLICT"
            _append_warning(
                warnings,
                "The manifest reconciliation audit trail disagrees with the current source inventory.",
            )

        assessments[matched_dataset.id] = ProvenanceAssessment(
            acquisition_status=acquisition_status,
            archive_integrity_status=integrity_status,
            data_quality_status=quality_status,
            status_explanation=_status_explanation(
                acquisition_status, integrity_status, quality_status
            ),
            validation_warnings=[
                warning
                for warning in warnings
                if warning
                in {
                    "The source inventory's recorded provenance statuses do not match the reconciled evidence.",
                    "The manifest reconciliation audit trail disagrees with the current source inventory.",
                }
            ],
            artifacts=artifacts,
        )

    for dataset in inventory.datasets:
        if dataset.id in assessments:
            continue
        if (
            manifest.requests
            and dataset_id != dataset.id
            and dataset.download_status == "acquired"
        ):
            acquisition_status = "PROVENANCE_CONFLICT"
            source_warnings = [
                "Inventory reports an acquisition but the manifest lacks a matching source identifier."
            ]
        elif dataset.download_status == "acquired":
            acquisition_status = "ACQUIRED_UNVERIFIED"
            source_warnings = ["No matching acquisition manifest is available for this source."]
        elif manifest.requests and dataset.acquisition_status in (
            "ACQUIRED_VERIFIED",
            "ACQUIRED_UNVERIFIED",
        ):
            acquisition_status = "PROVENANCE_CONFLICT"
            source_warnings = ["Inventory reports an acquisition but the manifest lacks a matching source identifier."]
        else:
            acquisition_status = "NOT_DOWNLOADED"
            source_warnings = []
        assessments[dataset.id] = ProvenanceAssessment(
            acquisition_status=acquisition_status,
            archive_integrity_status="NOT_ASSESSED",
            data_quality_status=dataset.data_quality_status or "NOT_ASSESSED",
            status_explanation=_status_explanation(
                acquisition_status,
                "NOT_ASSESSED",
                dataset.data_quality_status or "NOT_ASSESSED",
            ),
            validation_warnings=source_warnings,
            artifacts=[],
        )

    return assessments, warnings


def _source_summary(
    dataset: InventoryDataset,
    inventory: InventoryMetadata,
    assessment: ProvenanceAssessment,
) -> DataSourceSummary:
    commercial = inventory.commercial_reviews[dataset.id]
    portfolio = inventory.portfolio_reviews[dataset.id]
    return DataSourceSummary(
        id=dataset.id,
        name=dataset.name,
        publisher=dataset.publisher,
        license=dataset.license,
        dataset_version=dataset.dataset_version,
        version_status=dataset.version_status,
        portfolio_status=portfolio.status,
        commercial_approval_status=commercial.approval_status,
        commercial_use_status=commercial.commercial_use_status,
        inventory_acquisition_status=dataset.download_status,
        acquisition_status=assessment.acquisition_status,
        archive_integrity_status=assessment.archive_integrity_status,
        data_quality_status=assessment.data_quality_status,
        validation_warnings=assessment.validation_warnings,
        last_checked=dataset.last_checked,
    )


def _eligibility_item(
    dataset: InventoryDataset,
    inventory: InventoryMetadata,
    quality: QualityMetadata,
    assessment: ProvenanceAssessment,
) -> TrainingEligibilityItem:
    commercial = inventory.commercial_reviews[dataset.id]
    reasons: list[str] = []
    if commercial.approval_status != "APPROVED":
        reasons.append(f"Commercial approval is {commercial.approval_status}.")
    if dataset.download_status != "acquired":
        reasons.append("The source inventory does not record an acquired dataset version.")
    if dataset.dataset_version is None:
        reasons.append("The acquired dataset version is not pinned.")
    if assessment.acquisition_status != "ACQUIRED_VERIFIED":
        reasons.append(
            f"Acquisition provenance is {assessment.acquisition_status}, not verified."
        )
    if commercial.training_data_quality_status != "VERIFIED":
        reasons.append("Training data quality is not verified.")
    if commercial.training_relevance_status != "VERIFIED":
        reasons.append("Training geography and crop relevance are not verified.")
    if assessment.data_quality_status == "QUALITY_REJECTED" or (
        dataset.id == "era5_land"
        and quality.overall_training_status == "REJECT_FOR_TRAINING"
    ):
        reasons.append("The inspected data quality report rejects this source for training.")
    has_metadata_blocker = bool(reasons)
    if not has_metadata_blocker:
        reasons.append("Signed approval and provenance must still pass the training governance gate.")
    return TrainingEligibilityItem(
        id=dataset.id,
        name=dataset.name,
        eligible_for_training=False,
        status="INELIGIBLE" if has_metadata_blocker else "GOVERNANCE_CHECK_REQUIRED",
        reasons=reasons,
    )


def _weather_archive(request_number: int, archive: QualityArchiveMetadata) -> WeatherArchiveQuality:
    coverage = archive.dynamic_data_coverage_utc or archive.dynamic_coverage_utc or {}
    missing_fraction = archive.global_grid_missingness.get(
        "fraction", archive.global_grid_missingness.get("fraction_dynamic")
    )
    gap_seconds = archive.observed_gaps_seconds or archive.observed_interval_seconds or []
    return WeatherArchiveQuality(
        request_number=request_number,
        decision=archive.decision,
        training_status=archive.training_status,
        dynamic_timestamp_count=archive.timestamp_count,
        coverage_start_utc=coverage.get("start"),
        coverage_end_utc=coverage.get("end"),
        observed_gap_hours=[round(seconds / 3600, 2) for seconds in gap_seconds],
        global_grid_missing_fraction=float(missing_fraction),
        missingness_scope="Global-grid estimate; not a Kerala-specific missingness rate.",
        warning=(
            "Insufficient temporal coverage; do not use this archive for training."
            if archive.training_status == "REJECT_FOR_TRAINING"
            else "Training eligibility must be verified before model use."
        ),
    )


def _paginate(items: list[Any], limit: int, offset: int) -> tuple[list[Any], int]:
    return items[offset : offset + limit], len(items)


@router.get("/summary", response_model=DataIntelligenceSummary)
def data_intelligence_summary() -> DataIntelligenceSummary:
    inventory = _inventory()
    manifest = _manifest()
    quality = _quality()
    assessments, validation_warnings = _reconcile_provenance(
        inventory, manifest, quality
    )
    eligibility = [
        _eligibility_item(dataset, inventory, quality, assessments[dataset.id])
        for dataset in inventory.datasets
    ]
    metadata_warnings = list(validation_warnings)
    return DataIntelligenceSummary(
        total_sources=len(inventory.datasets),
        portfolio_status_counts=dict(Counter(
            inventory.portfolio_reviews[dataset.id].status for dataset in inventory.datasets
        )),
        commercial_approval_counts=dict(Counter(
            inventory.commercial_reviews[dataset.id].approval_status for dataset in inventory.datasets
        )),
        inventory_acquisition_counts=dict(Counter(
            dataset.download_status for dataset in inventory.datasets
        )),
        acquisition_status_counts=dict(Counter(
            assessments[dataset.id].acquisition_status for dataset in inventory.datasets
        )),
        archive_integrity_status_counts=dict(Counter(
            assessments[dataset.id].archive_integrity_status for dataset in inventory.datasets
        )),
        data_quality_status_counts=dict(Counter(
            assessments[dataset.id].data_quality_status for dataset in inventory.datasets
        )),
        manifest_request_count=len(manifest.requests),
        manifest_reported_success_count=sum(
            request.request_status.casefold().startswith("successful")
            for request in manifest.requests
        ),
        training_eligible_count=sum(item.eligible_for_training for item in eligibility),
        weather_decision=quality.overall_decision,
        weather_training_status=quality.overall_training_status,
        metadata_warnings=metadata_warnings,
        validation_warnings=validation_warnings,
    )


@router.get("/sources", response_model=DatasetInventoryPage)
def list_data_sources(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DatasetInventoryPage:
    inventory = _inventory()
    manifest = _manifest()
    quality = _quality()
    assessments, _ = _reconcile_provenance(inventory, manifest, quality)
    items = [
        _source_summary(dataset, inventory, assessments[dataset.id])
        for dataset in inventory.datasets
    ]
    page_items, total = _paginate(items, limit, offset)
    return DatasetInventoryPage(items=page_items, total=total, limit=limit, offset=offset)


@router.get("/approvals", response_model=DatasetApprovalPage)
def list_data_approvals(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DatasetApprovalPage:
    inventory = _inventory()
    items = [
        DataSourceApproval(
            id=dataset.id,
            name=dataset.name,
            portfolio_status=inventory.portfolio_reviews[dataset.id].status,
            commercial_approval_status=inventory.commercial_reviews[dataset.id].approval_status,
            commercial_use_status=inventory.commercial_reviews[dataset.id].commercial_use_status,
        )
        for dataset in inventory.datasets
    ]
    page_items, total = _paginate(items, limit, offset)
    counts = dict(Counter(item.commercial_approval_status for item in items))
    return DatasetApprovalPage(
        total=total,
        counts=counts,
        items=Page[DataSourceApproval](
            items=page_items,
            total=total,
            limit=limit,
            offset=offset,
        ),
    )


@router.get("/acquisitions", response_model=DatasetAcquisitionPage)
def list_data_acquisitions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DatasetAcquisitionPage:
    inventory = _inventory()
    manifest = _manifest()
    quality = _quality()
    assessments, validation_warnings = _reconcile_provenance(
        inventory, manifest, quality
    )
    items = [
        DataSourceAcquisition(
            id=dataset.id,
            name=dataset.name,
            inventory_status=dataset.download_status,
            acquisition_status=assessments[dataset.id].acquisition_status,
            archive_integrity_status=assessments[dataset.id].archive_integrity_status,
            data_quality_status=assessments[dataset.id].data_quality_status,
            status_explanation=assessments[dataset.id].status_explanation,
            validation_warnings=assessments[dataset.id].validation_warnings,
            artifacts=assessments[dataset.id].artifacts,
        )
        for dataset in inventory.datasets
    ]
    page_items, total = _paginate(items, limit, offset)
    return DatasetAcquisitionPage(
        items=page_items,
        total=total,
        limit=limit,
        offset=offset,
        validation_warnings=validation_warnings,
    )


@router.get("/quality", response_model=DataQualityResponse)
def data_quality() -> DataQualityResponse:
    quality = _quality()
    return DataQualityResponse(
        overall_decision=quality.overall_decision,
        overall_training_status=quality.overall_training_status,
        archives=[
            _weather_archive(1, quality.request_1),
            _weather_archive(2, quality.request_2),
        ],
    )


@router.get("/weather-coverage", response_model=WeatherCoverageResponse)
def weather_coverage() -> WeatherCoverageResponse:
    quality = _quality()
    return WeatherCoverageResponse(
        archives=[
            _weather_archive(1, quality.request_1),
            _weather_archive(2, quality.request_2),
        ],
        note="Timestamp counts describe dynamic weather coverage; ancillary records are not a time series.",
    )


@router.get("/training-eligibility", response_model=TrainingEligibilityResponse)
def training_eligibility(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TrainingEligibilityResponse:
    inventory = _inventory()
    manifest = _manifest()
    quality = _quality()
    assessments, _ = _reconcile_provenance(inventory, manifest, quality)
    items = [
        _eligibility_item(dataset, inventory, quality, assessments[dataset.id])
        for dataset in inventory.datasets
    ]
    page_items, total = _paginate(items, limit, offset)
    eligible_count = sum(item.eligible_for_training for item in items)
    return TrainingEligibilityResponse(
        total_sources=total,
        eligible_count=eligible_count,
        items=Page[TrainingEligibilityItem](
            items=page_items,
            total=total,
            limit=limit,
            offset=offset,
        ),
        note="This read-only assessment never grants training clearance; signed provenance must pass the dataset governance gate.",
    )


@router.get("/provenance", response_model=DatasetProvenancePage)
def list_data_provenance(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DatasetProvenancePage:
    inventory = _inventory()
    manifest = _manifest()
    quality = _quality()
    assessments, _ = _reconcile_provenance(inventory, manifest, quality)
    items = [
        DataProvenanceItem(
            id=dataset.id,
            name=dataset.name,
            publisher=dataset.publisher,
            license=dataset.license,
            dataset_version=dataset.dataset_version,
            version_status=dataset.version_status,
            last_checked=dataset.last_checked,
            acquisition_status=assessments[dataset.id].acquisition_status,
            archive_integrity_status=assessments[dataset.id].archive_integrity_status,
            data_quality_status=assessments[dataset.id].data_quality_status,
            validation_warnings=assessments[dataset.id].validation_warnings,
            artifacts=assessments[dataset.id].artifacts,
        )
        for dataset in inventory.datasets
    ]
    page_items, total = _paginate(items, limit, offset)
    return DatasetProvenancePage(items=page_items, total=total, limit=limit, offset=offset)


@router.get("/catalogue-completeness", response_model=CatalogueCompletenessResponse)
def catalogue_completeness(db: Session = Depends(get_db)) -> CatalogueCompletenessResponse:
    try:
        districts_total = db.scalar(select(func.count(District.id))) or 0
        categories_total = db.scalar(select(func.count(CropCategory.id))) or 0
        crops_total = db.scalar(select(func.count(Crop.id))) or 0
        profiles_total = db.scalar(select(func.count(CropProfile.id))) or 0
        verified_profiles = db.scalar(
            select(func.count(CropProfile.id)).where(CropProfile.verification_status == "verified")
        ) or 0
        varieties_total = db.scalar(select(func.count(CropVariety.id))) or 0
        districts_with_suitability = db.scalar(
            select(func.count(func.distinct(DistrictCropSuitability.district_id)))
        ) or 0
        associations_total = db.scalar(select(func.count(DistrictCropSuitability.id))) or 0
    except SQLAlchemyError as error:
        logger.error("Catalogue completeness query failed (%s).", type(error).__name__)
        raise HTTPException(status_code=503, detail="Catalogue completeness is unavailable.") from None

    return CatalogueCompletenessResponse(
        districts_total=districts_total,
        crop_categories_total=categories_total,
        crops_total=crops_total,
        crop_profiles_total=profiles_total,
        verified_crop_profiles=verified_profiles,
        crop_profile_coverage_percent=(
            round(profiles_total / crops_total * 100, 2) if crops_total else None
        ),
        crop_varieties_total=varieties_total,
        districts_with_suitability=districts_with_suitability,
        district_crop_associations_total=associations_total,
        district_suitability_coverage_percent=(
            round(districts_with_suitability / districts_total * 100, 2)
            if districts_total
            else None
        ),
    )
