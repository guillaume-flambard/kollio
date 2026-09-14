"""persist adversarial reasoning steps per run

Revision ID: b6d24e8f1a07
Revises: a1f7c3d9e2b4
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b6d24e8f1a07"
down_revision: str | Sequence[str] | None = "a1f7c3d9e2b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "constraint_analyses",
        sa.Column(
            "steps",
            JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "analysis_workflows",
        sa.Column("draft_steps", JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analysis_workflows", "draft_steps")
    op.drop_column("constraint_analyses", "steps")
