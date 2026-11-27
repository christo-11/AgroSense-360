import uuid
from datetime import date, datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    JSON,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    pass


crop_profile_sources = Table(
    "crop_profile_sources",
    Base.metadata,
    Column("crop_profile_id", Uuid, ForeignKey("crop_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Uuid, ForeignKey("agricultural_sources.id", ondelete="CASCADE"), primary_key=True),
)

crop_variety_sources = Table(
    "crop_variety_sources",
    Base.metadata,
    Column("crop_variety_id", Uuid, ForeignKey("crop_varieties.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Uuid, ForeignKey("agricultural_sources.id", ondelete="CASCADE"), primary_key=True),
)

district_crop_sources = Table(
    "district_crop_sources",
    Base.metadata,
    Column(
        "district_crop_suitability_id",
        Uuid,
        ForeignKey("district_crop_suitability.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("source_id", Uuid, ForeignKey("agricultural_sources.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="users_email_key"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    farms: Mapped[list["Farm"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class District(Base):
    __tablename__ = "districts"
    __table_args__ = (
        UniqueConstraint("name_key", name="uq_districts_name_key"),
        UniqueConstraint("slug", name="uq_districts_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_key: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False)
    state_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Kerala")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )
    crop_suitabilities: Mapped[list["DistrictCropSuitability"]] = relationship(
        back_populates="district", cascade="all, delete-orphan"
    )


class CropCategory(Base):
    __tablename__ = "crop_categories"
    __table_args__ = (
        UniqueConstraint("name_key", name="uq_crop_categories_name_key"),
        UniqueConstraint("slug", name="uq_crop_categories_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_key: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )
    crops: Mapped[list["Crop"]] = relationship(back_populates="category")


class Crop(Base):
    __tablename__ = "crops"
    __table_args__ = (
        UniqueConstraint("common_name_key", name="uq_crops_common_name_key"),
        UniqueConstraint("slug", name="uq_crops_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    common_name: Mapped[str] = mapped_column(String(120), nullable=False)
    common_name_key: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(200))
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_categories.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    category: Mapped[CropCategory] = relationship(back_populates="crops")
    profile: Mapped["CropProfile | None"] = relationship(
        back_populates="crop", cascade="all, delete-orphan", uselist=False
    )
    varieties: Mapped[list["CropVariety"]] = relationship(
        back_populates="crop", cascade="all, delete-orphan"
    )
    district_suitabilities: Mapped[list["DistrictCropSuitability"]] = relationship(
        back_populates="crop",
        foreign_keys=lambda: [DistrictCropSuitability.crop_id],
    )


class CropProfile(Base):
    __tablename__ = "crop_profiles"
    __table_args__ = (
        UniqueConstraint("crop_id", name="uq_crop_profiles_crop_id"),
        CheckConstraint(
            "verification_status IN ('pending', 'verified', 'rejected')",
            name="ck_crop_profiles_verification_status",
        ),
        CheckConstraint(
            "temperature_min_celsius IS NULL OR temperature_max_celsius IS NULL "
            "OR temperature_min_celsius <= temperature_max_celsius",
            name="ck_crop_profiles_temperature_range",
        ),
        CheckConstraint(
            "rainfall_min_mm_year IS NULL OR rainfall_max_mm_year IS NULL "
            "OR rainfall_min_mm_year <= rainfall_max_mm_year",
            name="ck_crop_profiles_rainfall_range",
        ),
        CheckConstraint(
            "soil_ph_min IS NULL OR soil_ph_max IS NULL OR soil_ph_min <= soil_ph_max",
            name="ck_crop_profiles_ph_range",
        ),
        CheckConstraint(
            "plant_spacing_min_cm IS NULL OR plant_spacing_max_cm IS NULL "
            "OR plant_spacing_min_cm <= plant_spacing_max_cm",
            name="ck_crop_profiles_spacing_range",
        ),
        CheckConstraint(
            "growth_duration_min_days IS NULL OR growth_duration_max_days IS NULL "
            "OR growth_duration_min_days <= growth_duration_max_days",
            name="ck_crop_profiles_duration_range",
        ),
        CheckConstraint(
            "expected_yield_min IS NULL OR expected_yield_max IS NULL "
            "OR expected_yield_min <= expected_yield_max",
            name="ck_crop_profiles_yield_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    crop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), nullable=False
    )
    temperature_min_celsius: Mapped[float | None] = mapped_column(Numeric(7, 2))
    temperature_max_celsius: Mapped[float | None] = mapped_column(Numeric(7, 2))
    rainfall_min_mm_year: Mapped[float | None] = mapped_column(Numeric(9, 2))
    rainfall_max_mm_year: Mapped[float | None] = mapped_column(Numeric(9, 2))
    soil_type: Mapped[str | None] = mapped_column(Text)
    soil_ph_min: Mapped[float | None] = mapped_column(Numeric(4, 2))
    soil_ph_max: Mapped[float | None] = mapped_column(Numeric(4, 2))
    planting_season: Mapped[str | None] = mapped_column(Text)
    irrigation_requirements: Mapped[str | None] = mapped_column(Text)
    fertilizer_recommendations: Mapped[str | None] = mapped_column(Text)
    cultivation_practices: Mapped[str | None] = mapped_column(Text)
    plant_spacing_min_cm: Mapped[float | None] = mapped_column(Numeric(8, 2))
    plant_spacing_max_cm: Mapped[float | None] = mapped_column(Numeric(8, 2))
    growth_duration_min_days: Mapped[int | None]
    growth_duration_max_days: Mapped[int | None]
    harvesting_information: Mapped[str | None] = mapped_column(Text)
    common_pests_diseases: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        server_default=text("'[]'"),
        nullable=False,
    )
    expected_yield_min: Mapped[float | None] = mapped_column(Numeric(12, 3))
    expected_yield_max: Mapped[float | None] = mapped_column(Numeric(12, 3))
    expected_yield_unit: Mapped[str | None] = mapped_column(String(80))
    verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    crop: Mapped[Crop] = relationship(back_populates="profile")
    sources: Mapped[list["AgriculturalSource"]] = relationship(
        secondary=crop_profile_sources, order_by="AgriculturalSource.title"
    )


class CropVariety(Base):
    __tablename__ = "crop_varieties"
    __table_args__ = (
        UniqueConstraint("crop_id", "name_key", name="uq_crop_varieties_crop_name_key"),
        UniqueConstraint("id", "crop_id", name="uq_crop_varieties_id_crop"),
        CheckConstraint(
            "verification_status IN ('pending', 'verified', 'rejected')",
            name="ck_crop_varieties_verification_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    crop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    name_key: Mapped[str] = mapped_column(String(160), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    crop: Mapped[Crop] = relationship(back_populates="varieties")
    sources: Mapped[list["AgriculturalSource"]] = relationship(
        secondary=crop_variety_sources, order_by="AgriculturalSource.title"
    )


class AgriculturalSource(Base):
    __tablename__ = "agricultural_sources"
    __table_args__ = (UniqueConstraint("url", name="uq_agricultural_sources_url"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    license: Mapped[str | None] = mapped_column(String(200))
    accessed_on: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )


class DistrictCropSuitability(Base):
    __tablename__ = "district_crop_suitability"
    __table_args__ = (
        ForeignKeyConstraint(
            ["variety_id", "crop_id"],
            ["crop_varieties.id", "crop_varieties.crop_id"],
            name="fk_district_crop_variety_crop",
        ),
        CheckConstraint(
            "suitability_status IN ('suitable', 'not_suitable', 'under_review')",
            name="ck_district_crop_suitability_status",
        ),
        CheckConstraint(
            "verification_status IN ('pending', 'verified', 'rejected')",
            name="ck_district_crop_verification_status",
        ),
        CheckConstraint(
            "verification_status != 'verified' OR suitability_status != 'under_review'",
            name="ck_district_crop_verified_not_under_review",
        ),
        Index(
            "uq_district_crop_general",
            "district_id",
            "crop_id",
            unique=True,
            postgresql_where=text("variety_id IS NULL"),
            sqlite_where=text("variety_id IS NULL"),
        ),
        Index(
            "uq_district_crop_variety",
            "district_id",
            "crop_id",
            "variety_id",
            unique=True,
            postgresql_where=text("variety_id IS NOT NULL"),
            sqlite_where=text("variety_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    district_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("districts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    crop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False
    )
    variety_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    suitability_status: Mapped[str] = mapped_column(String(24), default="under_review", nullable=False)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    district: Mapped[District] = relationship(back_populates="crop_suitabilities")
    crop: Mapped[Crop] = relationship(
        back_populates="district_suitabilities",
        foreign_keys=[crop_id],
    )
    variety: Mapped[CropVariety | None] = relationship(
        foreign_keys=[variety_id],
        overlaps="crop,district_suitabilities",
    )
    sources: Mapped[list[AgriculturalSource]] = relationship(
        secondary=district_crop_sources, order_by="AgriculturalSource.title"
    )


class Farm(Base):
    __tablename__ = "farms"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_farm_owner_name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    boundary = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    owner: Mapped[User] = relationship(back_populates="farms")
    plots: Mapped[list["Plot"]] = relationship(back_populates="farm", cascade="all, delete-orphan")


class Plot(Base):
    __tablename__ = "plots"
    __table_args__ = (
        UniqueConstraint("farm_id", "name", name="uq_plot_farm_name"),
        CheckConstraint("area_value IS NULL OR area_value > 0", name="ck_plot_area_positive"),
        CheckConstraint("area_unit IS NULL OR area_unit IN ('acres', 'hectares')", name="ck_plot_area_unit"),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_plot_coordinates_pair",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    crop: Mapped[str | None] = mapped_column(String(120))
    crop_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("crops.id", ondelete="SET NULL"), index=True)
    area_value: Mapped[float | None] = mapped_column(Numeric(12, 4))
    area_unit: Mapped[str | None] = mapped_column(String(16))
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    boundary = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    farm: Mapped[Farm] = relationship(back_populates="plots")
