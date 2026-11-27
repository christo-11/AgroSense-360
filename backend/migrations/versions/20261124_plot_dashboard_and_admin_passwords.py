"""Add plot dashboard fields and one-time admin password changes."""

from alembic import op
from geoalchemy2 import Geometry
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "20261124_plot_dashboard"
down_revision = "5d3cbf283629"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("must_change_password", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("plots", sa.Column("crop_id", UUID(as_uuid=True), nullable=True))
    op.add_column("plots", sa.Column("area_value", sa.Numeric(12, 4), nullable=True))
    op.add_column("plots", sa.Column("area_unit", sa.String(length=16), nullable=True))
    op.add_column("plots", sa.Column("latitude", sa.Numeric(9, 6), nullable=True))
    op.add_column("plots", sa.Column("longitude", sa.Numeric(9, 6), nullable=True))
    op.alter_column(
        "plots",
        "boundary",
        existing_type=Geometry(geometry_type="MULTIPOLYGON", srid=4326),
        nullable=True,
    )
    op.create_index("ix_plots_crop_id", "plots", ["crop_id"], unique=False)
    op.create_foreign_key(
        "fk_plots_crop_id_crops",
        "plots",
        "crops",
        ["crop_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint("ck_plot_area_positive", "plots", "area_value IS NULL OR area_value > 0")
    op.create_check_constraint(
        "ck_plot_area_unit", "plots", "area_unit IS NULL OR area_unit IN ('acres', 'hectares')"
    )
    op.create_check_constraint(
        "ck_plot_coordinates_pair",
        "plots",
        "(latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL)",
    )
    op.execute(
        """
        UPDATE plots
        SET crop_id = crops.id
        FROM crops
        WHERE plots.crop IS NOT NULL
          AND lower(trim(plots.crop)) = lower(crops.common_name)
        """
    )


def downgrade() -> None:
    op.drop_constraint("ck_plot_coordinates_pair", "plots", type_="check")
    op.drop_constraint("ck_plot_area_unit", "plots", type_="check")
    op.drop_constraint("ck_plot_area_positive", "plots", type_="check")
    op.drop_constraint("fk_plots_crop_id_crops", "plots", type_="foreignkey")
    op.drop_index("ix_plots_crop_id", table_name="plots")
    op.alter_column(
        "plots",
        "boundary",
        existing_type=Geometry(geometry_type="MULTIPOLYGON", srid=4326),
        nullable=False,
    )
    op.drop_column("plots", "longitude")
    op.drop_column("plots", "latitude")
    op.drop_column("plots", "area_unit")
    op.drop_column("plots", "area_value")
    op.drop_column("plots", "crop_id")
    op.drop_column("users", "must_change_password")
