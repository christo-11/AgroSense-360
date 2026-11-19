"""Add a spatial index for farm boundaries."""

from alembic import op

revision = "0003_add_farm_boundary_index"
down_revision = "0002_add_plots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "idx_farms_boundary",
            "farms",
            ["boundary"],
            postgresql_using="gist",
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "idx_farms_boundary",
            table_name="farms",
            postgresql_concurrently=True,
        )
