"""add initiative type

Revision ID: 7b1f0c2e9a55
Revises: 5a7c1e9d3b48
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b1f0c2e9a55"
down_revision: str | Sequence[str] | None = "5a7c1e9d3b48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INITIATIVE_TYPES = (
    "idea",
    "hypothesis",
    "campaign",
    "opportunity",
    "decision",
    "experiment",
    "pricing",
    "market",
    "partnership",
    "internal_improvement",
)
TYPE_CHECK = "initiative_type IN ('" + "', '".join(INITIATIVE_TYPES) + "')"


def upgrade() -> None:
    op.add_column(
        "ideas",
        sa.Column(
            "initiative_type",
            sa.String(length=32),
            server_default=sa.text("'idea'"),
            nullable=False,
        ),
    )
    op.create_check_constraint("ideas_initiative_type_check", "ideas", TYPE_CHECK)


def downgrade() -> None:
    op.drop_constraint("ideas_initiative_type_check", "ideas", type_="check")
    op.drop_column("ideas", "initiative_type")
