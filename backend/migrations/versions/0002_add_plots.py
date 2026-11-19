"""Add farm plots with PostGIS boundaries."""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID

revision = "0002_add_plots"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("farm_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("crop", sa.String(length=120), nullable=True),
        sa.Column(
            "boundary",
            Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farm_id", "name", name="uq_plot_farm_name"),
    )
    op.create_index("ix_plots_farm_id", "plots", ["farm_id"], unique=False)
    op.create_index("idx_plots_boundary", "plots", ["boundary"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("idx_plots_boundary", table_name="plots")
    op.drop_index("ix_plots_farm_id", table_name="plots")
    op.drop_table("plots")
