from contextlib import asynccontextmanager
import json
from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agriculture import router as agriculture_router
from app.config import get_settings
from app.database import database_ready, get_db
from app.data_intelligence import router as data_intelligence_router
from app.integrations import integration_status, model_status
from app.markets import router as markets_router
from app.research import router as research_router
from app.research_ml import router as research_ml_router
from app.weather import router as weather_router
from app.models import (
    AgriculturalSource,
    Crop,
    CropProfile,
    District,
    DistrictCropSuitability,
    Farm,
    Plot,
    User,
)
from app.schemas import (
    FarmCreate,
    FarmRead,
    FarmUpdate,
    PlotCreate,
    PlotRead,
    PlotUpdate,
    PasswordChange,
    TokenRead,
    UserCreate,
    UserRead,
)
from app.security import (
    agricultural_admin,
    create_access_token,
    current_user,
    hash_password,
    password_change_user,
    verify_password,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="AgroSense-360 API",
    description="Farm records and transparent readiness status for agricultural data services.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(agriculture_router)
app.include_router(data_intelligence_router)
app.include_router(research_ml_router)
app.include_router(weather_router)
app.include_router(markets_router)
app.include_router(research_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/database")
def database_health() -> dict[str, str]:
    if not database_ready():
        raise HTTPException(status_code=503, detail="Database is unavailable.")
    return {"status": "ok", "database": "connected"}


@app.get("/api/v1/status")
def status_read() -> dict[str, object]:
    return {
        "api": "online",
        "database": "connected" if database_ready() else "unavailable",
        "public_demo_mode": get_settings().public_demo_mode,
        "integrations": integration_status(),
        "models": model_status(),
    }


def set_boundary(db: Session, item: Farm | Plot, boundary: dict[str, object] | None) -> None:
    model = type(item)
    if boundary is None:
        item.boundary = None
        return
    item.boundary = func.ST_Multi(
        func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(boundary, separators=(",", ":"))), 4326)
    )
    db.flush()
    if not db.scalar(select(func.ST_IsValid(model.boundary)).where(model.id == item.id)):
        db.rollback()
        raise HTTPException(status_code=422, detail="Boundary must be a valid, non-self-intersecting polygon.")


def read_boundary(db: Session, item: Farm | Plot) -> dict[str, object] | None:
    model = type(item)
    geometry = db.scalar(
        select(func.ST_AsGeoJSON(model.boundary)).where(model.id == item.id)
    )
    return json.loads(geometry) if geometry else None


def farm_response(db: Session, farm: Farm) -> FarmRead:
    return FarmRead(
        id=farm.id,
        name=farm.name,
        location=farm.location,
        boundary=read_boundary(db, farm),
        created_at=farm.created_at,
    )


def plot_response(db: Session, plot: Plot) -> PlotRead:
    boundary = read_boundary(db, plot)
    return PlotRead(
        id=plot.id,
        farm_id=plot.farm_id,
        name=plot.name,
        crop=plot.crop,
        crop_id=plot.crop_id,
        area_value=float(plot.area_value) if plot.area_value is not None else None,
        area_unit=plot.area_unit,
        latitude=float(plot.latitude) if plot.latitude is not None else None,
        longitude=float(plot.longitude) if plot.longitude is not None else None,
        boundary=boundary,
        created_at=plot.created_at,
    )


def owned_farm(db: Session, user: User, farm_id: UUID) -> Farm:
    farm = db.scalar(select(Farm).where(Farm.id == farm_id, Farm.owner_id == user.id))
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found.")
    return farm


def owned_plot(db: Session, user: User, farm_id: UUID, plot_id: UUID) -> Plot:
    plot = db.scalar(
        select(Plot)
        .join(Farm, Plot.farm_id == Farm.id)
        .where(Plot.id == plot_id, Plot.farm_id == farm_id, Farm.owner_id == user.id)
    )
    if plot is None:
        raise HTTPException(status_code=404, detail="Plot not found.")
    return plot


def _next_plot_name(db: Session, farm_id: UUID) -> str:
    existing = set(db.scalars(select(Plot.name).where(Plot.farm_id == farm_id)))
    index = 1
    while f"Plot {index}" in existing:
        index += 1
    return f"Plot {index}"


def _crop_values(db: Session, crop_id: UUID | None, crop_name: str | None) -> tuple[UUID | None, str | None]:
    if crop_id is None:
        return None, crop_name
    from app.models import Crop

    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=422, detail="Choose a crop from the agricultural catalogue.")
    return crop.id, crop.common_name


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, int]:
    farm_count = db.scalar(select(func.count(Farm.id)).where(Farm.owner_id == user.id)) or 0
    plot_count = (
        db.scalar(select(func.count(Plot.id)).join(Farm).where(Farm.owner_id == user.id)) or 0
    )
    return {"farm_count": farm_count, "plot_count": plot_count}


@app.get("/api/v1/admin/summary")
def admin_summary(
    _: User = Depends(agricultural_admin), db: Session = Depends(get_db)
) -> dict[str, object]:
    return {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "farms": db.scalar(select(func.count(Farm.id))) or 0,
        "plots": db.scalar(select(func.count(Plot.id))) or 0,
        "districts": db.scalar(select(func.count(District.id))) or 0,
        "crops": db.scalar(select(func.count(Crop.id))) or 0,
        "verified_crop_profiles": db.scalar(
            select(func.count(CropProfile.id)).where(CropProfile.verification_status == "verified")
        ) or 0,
        "verified_district_associations": db.scalar(
            select(func.count(DistrictCropSuitability.id)).where(
                DistrictCropSuitability.verification_status == "verified"
            )
        ) or 0,
        "source_references": db.scalar(select(func.count(AgriculturalSource.id))) or 0,
        "integrations": integration_status(),
        "models": model_status(),
    }


@app.post("/api/v1/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if get_settings().public_demo_mode:
        raise HTTPException(status_code=503, detail="Account registration is disabled in public demo mode.")
    if not get_settings().auth_configured:
        raise HTTPException(status_code=503, detail="Authentication is not configured with a secure JWT secret.")
    if payload.email.casefold() in get_settings().agricultural_admin_email_set:
        raise HTTPException(
            status_code=403,
            detail="Administrative accounts must be created or reset with the secure bootstrap command.",
        )
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from None
    return user


@app.post("/api/v1/auth/token", response_model=TokenRead)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenRead:
    if get_settings().public_demo_mode:
        raise HTTPException(status_code=503, detail="Authentication is disabled in public demo mode.")
    if not get_settings().auth_configured:
        raise HTTPException(status_code=503, detail="Authentication is not configured with a secure JWT secret.")
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRead(
        access_token=create_access_token(user.id),
        must_change_password=user.must_change_password,
    )


@app.post("/api/v1/auth/change-password")
def change_password(
    payload: PasswordChange,
    user: User = Depends(password_change_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    user.password_hash = hash_password(payload.new_password)
    user.must_change_password = False
    db.commit()
    return {"status": "password_changed"}


@app.get("/api/v1/farms", response_model=list[FarmRead])
def list_farms(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[FarmRead]:
    farms = db.scalars(select(Farm).where(Farm.owner_id == user.id).order_by(Farm.created_at.desc()))
    return [farm_response(db, farm) for farm in farms]


@app.post("/api/v1/farms", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> FarmRead:
    farm = Farm(owner_id=user.id, name=payload.name, location=payload.location)
    db.add(farm)
    try:
        db.flush()
        set_boundary(db, farm, payload.boundary)
        db.commit()
        db.refresh(farm)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A farm with this name already exists in your account.") from None
    return farm_response(db, farm)


@app.get("/api/v1/farms/{farm_id}", response_model=FarmRead)
def get_farm(
    farm_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> FarmRead:
    return farm_response(db, owned_farm(db, user, farm_id))


@app.patch("/api/v1/farms/{farm_id}", response_model=FarmRead)
def update_farm(
    farm_id: UUID,
    payload: FarmUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> FarmRead:
    farm = owned_farm(db, user, farm_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        if changes["name"] is None:
            raise HTTPException(status_code=422, detail="Farm name cannot be blank.")
        farm.name = changes["name"]
    if "location" in changes:
        farm.location = changes["location"]
    try:
        if "boundary" in changes:
            set_boundary(db, farm, changes["boundary"])
        db.commit()
        db.refresh(farm)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A farm with this name already exists in your account.") from None
    return farm_response(db, farm)


@app.delete("/api/v1/farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> None:
    farm = owned_farm(db, user, farm_id)
    db.delete(farm)
    db.commit()


@app.get("/api/v1/farms/{farm_id}/plots", response_model=list[PlotRead])
def list_plots(
    farm_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[PlotRead]:
    owned_farm(db, user, farm_id)
    plots = db.scalars(select(Plot).where(Plot.farm_id == farm_id).order_by(Plot.created_at.desc()))
    return [plot_response(db, plot) for plot in plots]


@app.post(
    "/api/v1/farms/{farm_id}/plots",
    response_model=PlotRead,
    status_code=status.HTTP_201_CREATED,
)
def create_plot(
    farm_id: UUID,
    payload: PlotCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PlotRead:
    owned_farm(db, user, farm_id)
    crop_id, crop_name = _crop_values(db, payload.crop_id, payload.crop)
    plot = Plot(
        farm_id=farm_id,
        name=payload.name or _next_plot_name(db, farm_id),
        crop=crop_name,
        crop_id=crop_id,
        area_value=payload.area_value,
        area_unit=payload.area_unit,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(plot)
    try:
        if payload.boundary is not None:
            set_boundary(db, plot, payload.boundary)
        db.commit()
        db.refresh(plot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A plot with this name already exists in this farm.") from None
    return plot_response(db, plot)


@app.get("/api/v1/farms/{farm_id}/plots/{plot_id}", response_model=PlotRead)
def get_plot(
    farm_id: UUID,
    plot_id: UUID,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PlotRead:
    return plot_response(db, owned_plot(db, user, farm_id, plot_id))


@app.patch("/api/v1/farms/{farm_id}/plots/{plot_id}", response_model=PlotRead)
def update_plot(
    farm_id: UUID,
    plot_id: UUID,
    payload: PlotUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PlotRead:
    plot = owned_plot(db, user, farm_id, plot_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        if changes["name"] is None:
            raise HTTPException(status_code=422, detail="Plot name cannot be blank.")
        plot.name = changes["name"]
    if "crop" in changes:
        plot.crop = changes["crop"]
        if "crop_id" not in changes:
            plot.crop_id = None
    if "crop_id" in changes:
        plot.crop_id, plot.crop = _crop_values(db, changes["crop_id"], None)
    for field in ("area_value", "area_unit", "latitude", "longitude"):
        if field in changes:
            setattr(plot, field, changes[field])
    if (plot.area_value is None) != (plot.area_unit is None):
        raise HTTPException(status_code=422, detail="Plot area and its unit must be provided together.")
    if (plot.latitude is None) != (plot.longitude is None):
        raise HTTPException(status_code=422, detail="Plot latitude and longitude must be provided together.")
    try:
        if "boundary" in changes:
            if changes["boundary"] is None:
                raise HTTPException(status_code=422, detail="Plot boundary cannot be cleared.")
            set_boundary(db, plot, changes["boundary"])
        db.commit()
        db.refresh(plot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A plot with this name already exists in this farm.") from None
    return plot_response(db, plot)


@app.delete("/api/v1/farms/{farm_id}/plots/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plot(
    farm_id: UUID,
    plot_id: UUID,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    plot = owned_plot(db, user, farm_id, plot_id)
    db.delete(plot)
    db.commit()


@app.get("/api/v1/insights/{insight_type}")
def unavailable_insight(insight_type: str) -> None:
    supported = {"soil", "weather", "yield", "disease", "markets"}
    if insight_type not in supported:
        raise HTTPException(status_code=404, detail="Unknown insight type.")
    raise HTTPException(
        status_code=503,
        detail=f"{insight_type.capitalize()} insights are unavailable until their verified data and model services are deployed.",
    )


@app.post("/api/v1/copilot/query")
def copilot_query() -> None:
    raise HTTPException(status_code=503, detail="The grounded agricultural copilot is not configured.")


@app.post("/api/v1/crop-health/analyze")
async def analyze_crop_image(image: UploadFile = File(...)) -> None:
    if image.content_type is None or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload a valid image file.")
    raise HTTPException(status_code=503, detail="Crop image analysis is unavailable until a validated model is deployed.")
