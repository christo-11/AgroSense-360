import re
import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import (
    AgriculturalSource,
    Crop,
    CropCategory,
    CropProfile,
    CropVariety,
    District,
    DistrictCropSuitability,
    User,
)
from app.schemas import (
    AgriculturalSourceCreate,
    AgriculturalSourceRead,
    CropCategoryRead,
    CropCreate,
    CropProfileRead,
    CropProfileUpdate,
    CropRead,
    CropUpdate,
    CropVarietyCreate,
    CropVarietyRead,
    CropVarietyUpdate,
    DistrictCropCreate,
    DistrictCropRead,
    DistrictCropUpdate,
    DistrictRead,
    Page,
    normalized_key,
)
from app.security import agricultural_admin, current_user

router = APIRouter(prefix="/api/v1", tags=["agricultural catalog"])

PROFILE_VALUE_FIELDS = (
    "temperature_min_celsius",
    "temperature_max_celsius",
    "rainfall_min_mm_year",
    "rainfall_max_mm_year",
    "soil_type",
    "soil_ph_min",
    "soil_ph_max",
    "planting_season",
    "irrigation_requirements",
    "fertilizer_recommendations",
    "cultivation_practices",
    "plant_spacing_min_cm",
    "plant_spacing_max_cm",
    "growth_duration_min_days",
    "growth_duration_max_days",
    "harvesting_information",
    "expected_yield_min",
    "expected_yield_max",
    "expected_yield_unit",
)


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _page(
    db: Session,
    statement,
    count_statement,
    limit: int,
    offset: int,
) -> tuple[Sequence, int]:
    items = db.scalars(statement.limit(limit).offset(offset)).all()
    total = db.scalar(count_statement) or 0
    return items, total


def _source_rows(db: Session, source_ids: list[uuid.UUID]) -> list[AgriculturalSource]:
    unique_ids = list(dict.fromkeys(source_ids))
    if not unique_ids:
        return []
    sources = db.scalars(
        select(AgriculturalSource).where(AgriculturalSource.id.in_(unique_ids))
    ).all()
    if len(sources) != len(unique_ids):
        raise HTTPException(status_code=422, detail="One or more source references do not exist.")
    return list(sources)


def _crop_read(crop: Crop) -> CropRead:
    return CropRead(
        id=crop.id,
        common_name=crop.common_name,
        slug=crop.slug,
        scientific_name=crop.scientific_name,
        category=crop.category,
        verification_status=crop.profile.verification_status if crop.profile else "pending",
        updated_at=crop.updated_at,
    )


def _district_crop_read(item: DistrictCropSuitability) -> DistrictCropRead:
    return DistrictCropRead(
        id=item.id,
        district_id=item.district_id,
        crop_id=item.crop_id,
        crop_name=item.crop.common_name,
        variety_id=item.variety_id,
        variety_name=item.variety.name if item.variety else None,
        suitability_status=item.suitability_status,
        verification_status=item.verification_status,
        notes=item.notes,
        sources=[AgriculturalSourceRead.model_validate(source) for source in item.sources],
        last_updated_at=item.last_updated_at,
    )


def _require_verified_sources(status_value: str, sources: list[AgriculturalSource]) -> None:
    if status_value == "verified" and not sources:
        raise HTTPException(
            status_code=422,
            detail="Verified agricultural information requires at least one source reference.",
        )


def _has_profile_claims(profile: CropProfile) -> bool:
    return any(getattr(profile, field) is not None for field in PROFILE_VALUE_FIELDS) or bool(
        profile.common_pests_diseases
    )


def _validate_profile_ranges(profile: CropProfile) -> None:
    pairs = (
        (profile.temperature_min_celsius, profile.temperature_max_celsius, "temperature"),
        (profile.rainfall_min_mm_year, profile.rainfall_max_mm_year, "rainfall"),
        (profile.soil_ph_min, profile.soil_ph_max, "soil pH"),
        (profile.plant_spacing_min_cm, profile.plant_spacing_max_cm, "plant spacing"),
        (profile.growth_duration_min_days, profile.growth_duration_max_days, "growth duration"),
        (profile.expected_yield_min, profile.expected_yield_max, "expected yield"),
    )
    for minimum, maximum, label in pairs:
        if minimum is not None and maximum is not None and minimum > maximum:
            raise HTTPException(status_code=422, detail=f"{label.capitalize()} minimum cannot exceed its maximum.")
    if (
        profile.expected_yield_min is not None or profile.expected_yield_max is not None
    ) and not profile.expected_yield_unit:
        raise HTTPException(status_code=422, detail="Expected yield values require an explicit unit.")


@router.get("/districts", response_model=Page[DistrictRead])
def list_districts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[DistrictRead]:
    items, total = _page(
        db,
        select(District).order_by(District.name),
        select(func.count()).select_from(District),
        limit,
        offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/crop-categories", response_model=Page[CropCategoryRead])
def list_crop_categories(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[CropCategoryRead]:
    items, total = _page(
        db,
        select(CropCategory).order_by(CropCategory.display_order, CropCategory.name),
        select(func.count()).select_from(CropCategory),
        limit,
        offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/crops", response_model=Page[CropRead])
def list_crops(
    category_id: uuid.UUID | None = None,
    search: str | None = Query(None, max_length=120),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[CropRead]:
    filters = []
    if category_id is not None:
        filters.append(Crop.category_id == category_id)
    if search and search.strip():
        filters.append(Crop.common_name.ilike(f"%{search.strip()}%"))
    statement = (
        select(Crop)
        .options(joinedload(Crop.category), joinedload(Crop.profile))
        .where(*filters)
        .order_by(Crop.common_name)
    )
    count_statement = select(func.count()).select_from(Crop).where(*filters)
    items, total = _page(db, statement, count_statement, limit, offset)
    return Page(items=[_crop_read(crop) for crop in items], total=total, limit=limit, offset=offset)


@router.get("/crops/{crop_id}", response_model=CropRead)
def get_crop(crop_id: uuid.UUID, db: Session = Depends(get_db)) -> CropRead:
    crop = db.scalar(
        select(Crop)
        .options(joinedload(Crop.category), joinedload(Crop.profile))
        .where(Crop.id == crop_id)
    )
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    return _crop_read(crop)


@router.get("/crops/{crop_id}/varieties", response_model=Page[CropVarietyRead])
def list_crop_varieties(
    crop_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[CropVarietyRead]:
    if db.get(Crop, crop_id) is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    statement = (
        select(CropVariety)
        .options(selectinload(CropVariety.sources))
        .where(CropVariety.crop_id == crop_id)
        .order_by(CropVariety.name)
    )
    count_statement = select(func.count()).select_from(CropVariety).where(CropVariety.crop_id == crop_id)
    items, total = _page(db, statement, count_statement, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/crops/{crop_id}/profile", response_model=CropProfileRead)
def get_crop_profile(crop_id: uuid.UUID, db: Session = Depends(get_db)) -> CropProfileRead:
    if db.get(Crop, crop_id) is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    profile = db.scalar(
        select(CropProfile)
        .options(selectinload(CropProfile.sources))
        .where(CropProfile.crop_id == crop_id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Crop profile not found.")
    return CropProfileRead.model_validate(profile)


@router.get("/districts/{district_id}/crops", response_model=Page[DistrictCropRead])
def list_district_crops(
    district_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Page[DistrictCropRead]:
    if db.get(District, district_id) is None:
        raise HTTPException(status_code=404, detail="District not found.")
    statement = (
        select(DistrictCropSuitability)
        .options(
            joinedload(DistrictCropSuitability.crop),
            joinedload(DistrictCropSuitability.variety),
            selectinload(DistrictCropSuitability.sources),
        )
        .where(DistrictCropSuitability.district_id == district_id)
        .order_by(DistrictCropSuitability.crop_id, DistrictCropSuitability.variety_id)
    )
    count_statement = (
        select(func.count())
        .select_from(DistrictCropSuitability)
        .where(DistrictCropSuitability.district_id == district_id)
    )
    items, total = _page(db, statement, count_statement, limit, offset)
    return Page(
        items=[_district_crop_read(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/agricultural-research/idukki-black-pepper")
def idukki_black_pepper_readiness(db: Session = Depends(get_db)) -> dict:
    crop = db.scalar(
        select(Crop)
        .options(joinedload(Crop.profile).selectinload(CropProfile.sources))
        .where(Crop.slug == "black-pepper")
    )
    if crop is None:
        crop = db.scalar(
            select(Crop)
            .options(joinedload(Crop.profile).selectinload(CropProfile.sources))
            .where(Crop.common_name_key == normalized_key("black pepper"))
        )
    district = db.scalar(select(District).where(District.slug == "idukki"))
    if district is None:
        district = db.scalar(select(District).where(District.name_key == normalized_key("Idukki")))

    profile = crop.profile if crop else None
    associations = (
        db.scalars(
            select(DistrictCropSuitability)
            .options(
                joinedload(DistrictCropSuitability.variety),
                selectinload(DistrictCropSuitability.sources),
            )
            .where(
                DistrictCropSuitability.crop_id == crop.id,
                DistrictCropSuitability.district_id == district.id,
            )
            .order_by(DistrictCropSuitability.variety_id)
        ).all()
        if crop and district
        else []
    )
    verified_profile = bool(profile and profile.verification_status == "verified" and profile.sources)
    verified_climate_ranges = bool(
        verified_profile
        and profile.temperature_min_celsius is not None
        and profile.temperature_max_celsius is not None
        and profile.rainfall_min_mm_year is not None
        and profile.rainfall_max_mm_year is not None
    )
    verified_association = any(item.verification_status == "verified" for item in associations)

    blockers = []
    if crop is None:
        blockers.append("No black-pepper crop record is present in the agricultural catalogue.")
    if district is None:
        blockers.append("No Idukki district record is present in the agricultural catalogue.")
    if profile is None or not verified_profile:
        blockers.append("A source-verified black-pepper crop profile is not available.")
    if not verified_climate_ranges:
        blockers.append("Complete, source-verified temperature and annual-rainfall ranges are not available.")
    if not verified_association:
        blockers.append("No source-verified Idukki-black pepper suitability association is available.")
    blockers.extend(
        [
            "The application has no georeferenced Idukki soil-sample records; district soil maps are not plot measurements.",
            "The agricultural catalogue has no plot/season-level pepper yield observations; profile yield ranges are not training labels.",
            "No season-specific pepper climate thresholds and field validation protocol are registered.",
        ]
    )

    return {
        "status": "evidence_incomplete",
        "assessment": "not_computed",
        "crop": (
            {
                "id": str(crop.id),
                "name": crop.common_name,
                "scientific_name": crop.scientific_name,
                "verification_status": profile.verification_status if profile else "pending",
            }
            if crop
            else None
        ),
        "district": {"id": str(district.id), "name": district.name} if district else None,
        "crop_profile": (
            {
                "verification_status": profile.verification_status,
                "temperature_min_celsius": profile.temperature_min_celsius,
                "temperature_max_celsius": profile.temperature_max_celsius,
                "rainfall_min_mm_year": profile.rainfall_min_mm_year,
                "rainfall_max_mm_year": profile.rainfall_max_mm_year,
                "soil_type": profile.soil_type,
                "soil_ph_min": profile.soil_ph_min,
                "soil_ph_max": profile.soil_ph_max,
                "sources": [
                    {
                        "title": source.title,
                        "publisher": source.publisher,
                        "url": source.url,
                        "license": source.license,
                    }
                    for source in profile.sources
                ],
            }
            if profile
            else None
        ),
        "district_associations": [
            {
                "suitability_status": item.suitability_status,
                "verification_status": item.verification_status,
                "variety": item.variety.name if item.variety else None,
                "sources": [
                    {
                        "title": source.title,
                        "publisher": source.publisher,
                        "url": source.url,
                        "license": source.license,
                    }
                    for source in item.sources
                ],
            }
            for item in associations
        ],
        "readiness": {
            "verified_climate_ranges": verified_climate_ranges,
            "verified_district_association": verified_association,
            "georeferenced_soil_samples": False,
            "pepper_yield_observations": False,
            "climate_suitability_result": False,
        },
        "blockers": blockers,
    }


@router.post(
    "/agricultural-sources",
    response_model=AgriculturalSourceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_agricultural_source(
    payload: AgriculturalSourceCreate,
    admin: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> AgriculturalSource:
    source = AgriculturalSource(
        title=payload.title,
        publisher=payload.publisher,
        url=str(payload.url),
        license=payload.license,
        accessed_on=payload.accessed_on,
        notes=payload.notes,
        created_by_id=admin.id,
    )
    db.add(source)
    try:
        db.commit()
        db.refresh(source)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A source reference with this URL already exists.") from None
    return source


@router.post("/crops", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def create_crop(
    payload: CropCreate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> CropRead:
    category = db.get(CropCategory, payload.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Crop category not found.")
    slug = payload.slug or _slugify(payload.common_name)
    if not slug:
        raise HTTPException(status_code=422, detail="A slug is required for this crop name.")
    crop = Crop(
        common_name=payload.common_name,
        common_name_key=normalized_key(payload.common_name),
        slug=slug,
        scientific_name=payload.scientific_name,
        category_id=category.id,
        profile=CropProfile(verification_status="pending", common_pests_diseases=[]),
    )
    db.add(crop)
    try:
        db.commit()
        db.refresh(crop)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A crop with this name or slug already exists.") from None
    return _crop_read(crop)


@router.patch("/crops/{crop_id}", response_model=CropRead)
def update_crop(
    crop_id: uuid.UUID,
    payload: CropUpdate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> CropRead:
    crop = db.scalar(
        select(Crop)
        .options(joinedload(Crop.category), joinedload(Crop.profile))
        .where(Crop.id == crop_id)
    )
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    changes = payload.model_dump(exclude_unset=True)
    if "common_name" in changes and changes["common_name"] is None:
        raise HTTPException(status_code=422, detail="Crop common name cannot be blank.")
    if "common_name" in changes:
        crop.common_name = changes["common_name"]
        crop.common_name_key = normalized_key(changes["common_name"])
    if "scientific_name" in changes:
        crop.scientific_name = changes["scientific_name"]
    if "category_id" in changes:
        category = db.get(CropCategory, changes["category_id"])
        if category is None:
            raise HTTPException(status_code=404, detail="Crop category not found.")
        crop.category = category
    try:
        db.commit()
        db.refresh(crop)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A crop with this name already exists.") from None
    return _crop_read(crop)


@router.patch("/crops/{crop_id}/profile", response_model=CropProfileRead)
def update_crop_profile(
    crop_id: uuid.UUID,
    payload: CropProfileUpdate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> CropProfileRead:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    profile = db.scalar(
        select(CropProfile)
        .options(selectinload(CropProfile.sources))
        .where(CropProfile.crop_id == crop_id)
    )
    if profile is None:
        profile = CropProfile(crop_id=crop_id, common_pests_diseases=[])
        db.add(profile)

    changes = payload.model_dump(exclude_unset=True)
    if "verification_status" in changes and changes["verification_status"] is None:
        raise HTTPException(status_code=422, detail="Verification status cannot be blank.")
    if "common_pests_diseases" in changes and changes["common_pests_diseases"] is None:
        raise HTTPException(status_code=422, detail="Pests and diseases must be a list; use an empty list to clear it.")
    if "source_ids" in changes and changes["source_ids"] is None:
        raise HTTPException(status_code=422, detail="Use an empty source list to clear source references.")
    source_ids = changes.pop("source_ids", None)
    for field, value in changes.items():
        setattr(profile, field, value)
    if source_ids is not None:
        profile.sources = _source_rows(db, source_ids)
    _validate_profile_ranges(profile)
    _require_verified_sources(profile.verification_status, profile.sources)
    if profile.verification_status == "verified" and not _has_profile_claims(profile):
        raise HTTPException(status_code=422, detail="A verified profile must contain sourced profile information.")
    try:
        db.commit()
        db.refresh(profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Crop profile could not be saved.") from None
    return CropProfileRead.model_validate(profile)


@router.post(
    "/crops/{crop_id}/varieties",
    response_model=CropVarietyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_crop_variety(
    crop_id: uuid.UUID,
    payload: CropVarietyCreate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> CropVarietyRead:
    if db.get(Crop, crop_id) is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    sources = _source_rows(db, payload.source_ids)
    variety = CropVariety(
        crop_id=crop_id,
        name=payload.name,
        name_key=normalized_key(payload.name),
        scientific_name=payload.scientific_name,
        description=payload.description,
        verification_status=payload.verification_status,
        sources=sources,
    )
    db.add(variety)
    try:
        db.commit()
        db.refresh(variety)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This variety already exists for the crop.") from None
    return CropVarietyRead.model_validate(variety)


@router.patch(
    "/crops/{crop_id}/varieties/{variety_id}",
    response_model=CropVarietyRead,
)
def update_crop_variety(
    crop_id: uuid.UUID,
    variety_id: uuid.UUID,
    payload: CropVarietyUpdate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> CropVarietyRead:
    variety = db.scalar(
        select(CropVariety)
        .options(selectinload(CropVariety.sources))
        .where(CropVariety.crop_id == crop_id, CropVariety.id == variety_id)
    )
    if variety is None:
        raise HTTPException(status_code=404, detail="Crop variety not found.")
    changes = payload.model_dump(exclude_unset=True)
    if "source_ids" in changes and changes["source_ids"] is None:
        raise HTTPException(status_code=422, detail="Use an empty source list to clear source references.")
    source_ids = changes.pop("source_ids", None)
    if "name" in changes:
        if changes["name"] is None:
            raise HTTPException(status_code=422, detail="Variety name cannot be blank.")
        variety.name = changes["name"]
        variety.name_key = normalized_key(changes["name"])
    for field in ("scientific_name", "description", "verification_status"):
        if field in changes:
            if field == "verification_status" and changes[field] is None:
                raise HTTPException(status_code=422, detail="Verification status cannot be blank.")
            setattr(variety, field, changes[field])
    if source_ids is not None:
        variety.sources = _source_rows(db, source_ids)
    _require_verified_sources(variety.verification_status, variety.sources)
    try:
        db.commit()
        db.refresh(variety)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This variety name already exists for the crop.") from None
    return CropVarietyRead.model_validate(variety)


@router.post(
    "/districts/{district_id}/crops",
    response_model=DistrictCropRead,
    status_code=status.HTTP_201_CREATED,
)
def create_district_crop_suitability(
    district_id: uuid.UUID,
    payload: DistrictCropCreate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> DistrictCropRead:
    district = db.get(District, district_id)
    if district is None:
        raise HTTPException(status_code=404, detail="District not found.")
    if db.get(Crop, payload.crop_id) is None:
        raise HTTPException(status_code=404, detail="Crop not found.")
    if payload.variety_id is not None:
        variety = db.get(CropVariety, payload.variety_id)
        if variety is None or variety.crop_id != payload.crop_id:
            raise HTTPException(status_code=422, detail="The variety must belong to the selected crop.")
    sources = _source_rows(db, payload.source_ids)
    _require_verified_sources(payload.verification_status, sources)
    item = DistrictCropSuitability(
        district_id=district_id,
        crop_id=payload.crop_id,
        variety_id=payload.variety_id,
        suitability_status=payload.suitability_status,
        verification_status=payload.verification_status,
        notes=payload.notes,
        sources=sources,
    )
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A district/crop/variety association already exists.",
        ) from None
    return _district_crop_read(item)


@router.patch(
    "/districts/{district_id}/crops/{association_id}",
    response_model=DistrictCropRead,
)
def update_district_crop_suitability(
    district_id: uuid.UUID,
    association_id: uuid.UUID,
    payload: DistrictCropUpdate,
    _: User = Depends(agricultural_admin),
    db: Session = Depends(get_db),
) -> DistrictCropRead:
    item = db.scalar(
        select(DistrictCropSuitability)
        .options(
            joinedload(DistrictCropSuitability.crop),
            joinedload(DistrictCropSuitability.variety),
            selectinload(DistrictCropSuitability.sources),
        )
        .where(
            DistrictCropSuitability.district_id == district_id,
            DistrictCropSuitability.id == association_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="District-crop association not found.")
    changes = payload.model_dump(exclude_unset=True)
    if "suitability_status" in changes and changes["suitability_status"] is None:
        raise HTTPException(status_code=422, detail="Suitability status cannot be blank.")
    if "verification_status" in changes and changes["verification_status"] is None:
        raise HTTPException(status_code=422, detail="Verification status cannot be blank.")
    if "notes" in changes and changes["notes"] is None:
        changes["notes"] = None
    if "source_ids" in changes and changes["source_ids"] is None:
        raise HTTPException(status_code=422, detail="Use an empty source list to clear source references.")
    source_ids = changes.pop("source_ids", None)
    if "variety_id" in changes and changes["variety_id"] is not None:
        variety = db.get(CropVariety, changes["variety_id"])
        if variety is None or variety.crop_id != item.crop_id:
            raise HTTPException(status_code=422, detail="The variety must belong to the associated crop.")
    for field, value in changes.items():
        setattr(item, field, value)
    if source_ids is not None:
        item.sources = _source_rows(db, source_ids)
    if (
        item.verification_status == "verified"
        and item.suitability_status == "under_review"
    ):
        raise HTTPException(status_code=422, detail="A verified association cannot remain under review.")
    _require_verified_sources(item.verification_status, item.sources)
    try:
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A district/crop/variety association already exists.",
        ) from None
    return _district_crop_read(item)
