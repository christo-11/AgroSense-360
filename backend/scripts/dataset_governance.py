"""Fail-closed commercial licensing and provenance checks for ML inputs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

APPROVAL_STATUSES = {"APPROVED", "CONDITIONAL", "BLOCKED", "UNVERIFIED"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_APPROVAL_FIELDS = (
    "resource_url",
    "download_api_url",
    "license_name",
    "license_url",
    "commercial_use_status",
    "attribution_obligations",
    "share_alike_obligations",
    "redistribution_restrictions",
    "third_party_rights",
    "kerala_coverage",
    "district_level_availability",
    "authentication_requirements",
    "access_status",
    "verification_date",
)


class DatasetEligibilityError(ValueError):
    """Raised when source approval or input provenance is incomplete."""


def _is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def load_inventory(path: Path) -> dict:
    try:
        inventory = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetEligibilityError("Dataset source inventory could not be read.") from error
    if not isinstance(inventory, dict):
        raise DatasetEligibilityError("Dataset source inventory must be a JSON object.")
    datasets = inventory.get("datasets")
    if not isinstance(datasets, list):
        raise DatasetEligibilityError("Dataset inventory must contain a datasets list.")
    seen: set[str] = set()
    for record in datasets:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise DatasetEligibilityError("Every dataset record must have a string resource id.")
        if record["id"] in seen:
            raise DatasetEligibilityError(f"Duplicate dataset resource id: {record['id']}.")
        seen.add(record["id"])
    return inventory


def reviewer_allowlist(project_root: Path) -> frozenset[str]:
    configured = os.environ.get("DATASET_REVIEWER_EMAILS")
    if configured is None:
        env_file = project_root / ".env"
        if env_file.is_file():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                key, separator, value = line.partition("=")
                if separator and key.strip() == "DATASET_REVIEWER_EMAILS":
                    configured = value.strip().strip("\"'")
                    break
    return frozenset(
        email.strip().casefold()
        for email in (configured or "").split(",")
        if email.strip()
    )


def approval_key(project_root: Path) -> str:
    configured = os.environ.get("DATASET_APPROVAL_HMAC_KEY")
    if configured is None:
        env_file = project_root / ".env"
        if env_file.is_file():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                key, separator, value = line.partition("=")
                if separator and key.strip() == "DATASET_APPROVAL_HMAC_KEY":
                    configured = value.strip().strip("\"'")
                    break
    return configured or ""


def _find_source(inventory: dict, dataset_id: str) -> dict:
    for record in inventory["datasets"]:
        if record["id"] == dataset_id:
            return record
    raise DatasetEligibilityError(f"Unknown dataset resource id: {dataset_id}.")


def _validate_approved_review(
    source: dict,
    review: dict,
    allowed_reviewers: frozenset[str],
) -> None:
    missing = [
        field for field in _APPROVAL_FIELDS
        if not isinstance(review.get(field), str) or not review[field].strip()
    ]
    if missing:
        raise DatasetEligibilityError(
            "Approved dataset review is missing required fields: " + ", ".join(missing) + "."
        )
    if review["commercial_use_status"] != "PERMITTED":
        raise DatasetEligibilityError("Commercial use is not verified as permitted.")
    if review["third_party_rights"] != "CLEARED":
        raise DatasetEligibilityError("Third-party rights are not marked as cleared.")
    if not _is_http_url(review["resource_url"]) or not _is_http_url(review["download_api_url"]):
        raise DatasetEligibilityError("Resource and download/API URLs must be valid HTTP(S) URLs.")
    if not _is_http_url(review["license_url"]):
        raise DatasetEligibilityError("License URL must be a valid HTTP(S) URL.")
    evidence_urls = review.get("evidence_urls")
    if not isinstance(evidence_urls, list) or not evidence_urls:
        raise DatasetEligibilityError("An approved dataset requires official evidence URLs.")
    if not all(_is_http_url(url) for url in evidence_urls):
        raise DatasetEligibilityError("Evidence URLs must be valid HTTP(S) URLs.")
    if not all(
        isinstance(review[field], str) and review[field].strip()
        for field in (
            "attribution_obligations",
            "share_alike_obligations",
            "redistribution_restrictions",
            "kerala_coverage",
            "district_level_availability",
            "authentication_requirements",
            "access_status",
        )
    ):
        raise DatasetEligibilityError("License obligations, coverage, and access facts must be recorded.")
    concerns = review.get("remaining_concerns")
    if not isinstance(concerns, list) or concerns:
        raise DatasetEligibilityError("An approved dataset cannot have unresolved review concerns.")
    official_urls = source.get("official_urls") or []
    if not isinstance(official_urls, list):
        raise DatasetEligibilityError("Inventoried official_urls must be a list.")
    source_urls = [source.get("official_url"), *official_urls]
    source_urls = [url for url in source_urls if isinstance(url, str)]
    if review["resource_url"] not in source_urls:
        raise DatasetEligibilityError("Reviewed resource URL does not match the inventoried source.")
    reviewer = review.get("reviewed_by")
    if not isinstance(reviewer, str) or reviewer.casefold() not in allowed_reviewers:
        raise DatasetEligibilityError("Dataset approval is missing an allowlisted reviewer.")
    reviewed_at = review.get("reviewed_at")
    try:
        if not isinstance(reviewed_at, str) or not datetime.fromisoformat(
            reviewed_at.replace("Z", "+00:00")
        ).tzinfo:
            raise ValueError
    except ValueError:
        raise DatasetEligibilityError("Dataset approval requires a timezone-aware review timestamp.") from None


def _approval_signature(source: dict, review: dict, key: str) -> str:
    signed_review = {field: value for field, value in review.items() if field != "review_signature"}
    payload = {
        "source": {
            "id": source.get("id"),
            "publisher": source.get("publisher"),
            "official_url": source.get("official_url"),
            "official_urls": source.get("official_urls"),
        },
        "review": signed_review,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def _hash_path(path: Path) -> str:
    if not path.exists() or path.is_symlink():
        raise DatasetEligibilityError("Training input does not exist or is a symbolic link.")
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    if not path.is_dir():
        raise DatasetEligibilityError("Training input must be a regular file or directory.")
    file_count = 0
    for root, directories, filenames in os.walk(path, followlinks=False):
        root_path = Path(root)
        directories.sort()
        filenames.sort()
        if any((root_path / directory).is_symlink() for directory in directories):
            raise DatasetEligibilityError("Training input cannot contain symbolic links.")
        for filename in filenames:
            item = root_path / filename
            if item.is_symlink():
                raise DatasetEligibilityError("Training input cannot contain symbolic links.")
            relative = item.relative_to(path).as_posix().encode("utf-8")
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            file_count += 1
    if not file_count:
        raise DatasetEligibilityError("Training input directory is empty.")
    return digest.hexdigest()


def require_training_dataset(
    dataset_id: str,
    data_path: Path,
    provenance_path: Path,
    inventory_path: Path,
    allowed_reviewers: frozenset[str],
    signing_key: str = "",
) -> dict:
    inventory = load_inventory(inventory_path)
    source = _find_source(inventory, dataset_id)
    reviews = inventory.get("commercial_reviews")
    review = reviews.get(dataset_id) if isinstance(reviews, dict) else None
    if not isinstance(review, dict):
        raise DatasetEligibilityError(f"Dataset {dataset_id} has no commercial review.")
    status = review.get("approval_status")
    if status not in APPROVAL_STATUSES:
        raise DatasetEligibilityError(f"Dataset {dataset_id} has an invalid approval status.")
    if status != "APPROVED":
        raise DatasetEligibilityError(
            f"Dataset {dataset_id} is {status}; only APPROVED datasets may enter training."
        )
    _validate_approved_review(source, review, allowed_reviewers)
    if len(signing_key.encode("utf-8")) < 32:
        raise DatasetEligibilityError("Dataset approval signing key is not configured securely.")
    signature = review.get("review_signature")
    expected_signature = _approval_signature(source, review, signing_key)
    if not isinstance(signature, str) or not hmac.compare_digest(signature, expected_signature):
        raise DatasetEligibilityError("Dataset approval signature is missing or invalid.")
    if source.get("download_status") != "acquired":
        raise DatasetEligibilityError(f"Dataset {dataset_id} has not been recorded as acquired.")
    if review.get("training_data_quality_status") != "VERIFIED":
        raise DatasetEligibilityError("Training data quality has not been verified.")
    if review.get("training_relevance_status") != "VERIFIED":
        raise DatasetEligibilityError("Training geography and crop relevance have not been verified.")

    try:
        manifest = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetEligibilityError("Training provenance manifest could not be read.") from error
    if not isinstance(manifest, dict):
        raise DatasetEligibilityError("Training provenance manifest must be a JSON object.")
    if manifest.get("dataset_id") != dataset_id:
        raise DatasetEligibilityError("Provenance manifest dataset id does not match the requested dataset.")
    if data_path.is_symlink():
        raise DatasetEligibilityError("Training input cannot be a symbolic link.")
    requested_path = data_path.resolve()
    manifest_path = Path(manifest.get("data_path", ""))
    if not manifest_path.is_absolute():
        manifest_path = provenance_path.parent / manifest_path
    if manifest_path.resolve() != requested_path:
        raise DatasetEligibilityError("Provenance manifest does not identify the training input path.")
    source_url = manifest.get("source_url")
    if not isinstance(source_url, str) or source_url not in {
        review["resource_url"],
        review["download_api_url"],
    }:
        raise DatasetEligibilityError("Provenance source URL does not match the reviewed resource.")
    if not isinstance(manifest.get("source_version"), str) or not manifest["source_version"].strip():
        raise DatasetEligibilityError("Provenance manifest must identify the source version.")
    if manifest.get("license_name") != review["license_name"]:
        raise DatasetEligibilityError("Provenance license does not match the approved license.")
    retrieved_at = manifest.get("retrieved_at")
    try:
        if not isinstance(retrieved_at, str) or not datetime.fromisoformat(
            retrieved_at.replace("Z", "+00:00")
        ).tzinfo:
            raise ValueError
    except ValueError:
        raise DatasetEligibilityError("Provenance manifest requires a timezone-aware retrieval timestamp.") from None
    recorded_hash = manifest.get("sha256")
    if not isinstance(recorded_hash, str) or not _SHA256_RE.fullmatch(recorded_hash.lower()):
        raise DatasetEligibilityError("Provenance manifest requires a valid SHA-256 digest.")
    if _hash_path(requested_path) != recorded_hash.lower():
        raise DatasetEligibilityError("Training input checksum does not match its provenance manifest.")
    return source


def record_admin_review(
    inventory_path: Path,
    dataset_id: str,
    status: str,
    reviewer: str,
    allowed_reviewers: frozenset[str],
    reason: str,
    signing_key: str,
) -> None:
    if status not in APPROVAL_STATUSES:
        raise DatasetEligibilityError("Review status is not recognized.")
    if not reviewer or reviewer.casefold() not in allowed_reviewers:
        raise DatasetEligibilityError("Reviewer is not in DATASET_REVIEWER_EMAILS.")
    if not reason.strip():
        raise DatasetEligibilityError("A review reason is required.")
    inventory = load_inventory(inventory_path)
    source = _find_source(inventory, dataset_id)
    reviews = inventory.get("commercial_reviews")
    review = reviews.get(dataset_id) if isinstance(reviews, dict) else None
    if not isinstance(review, dict):
        raise DatasetEligibilityError(f"Dataset {dataset_id} has no commercial review.")
    review["approval_status"] = status
    review["reviewed_by"] = reviewer
    review["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    review["review_reason"] = reason.strip()
    if status == "APPROVED":
        if len(signing_key.encode("utf-8")) < 32:
            raise DatasetEligibilityError("Dataset approval signing key is not configured securely.")
        review.pop("review_signature", None)
        _validate_approved_review(source, review, allowed_reviewers)
        review["review_signature"] = _approval_signature(source, review, signing_key)
    else:
        review.pop("review_signature", None)
    serialized = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=inventory_path.parent,
            prefix=f".{inventory_path.name}.{uuid4().hex}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_path = Path(temporary.name)
        temporary_path.replace(inventory_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
