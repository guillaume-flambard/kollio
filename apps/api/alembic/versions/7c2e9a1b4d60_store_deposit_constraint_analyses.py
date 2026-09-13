"""store deposit constraint analyses

Revision ID: 7c2e9a1b4d60
Revises: 04f3435ac590
Create Date: 2026-09-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c2e9a1b4d60"
down_revision: str | Sequence[str] | None = "04f3435ac590"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "constraint_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("iteration_id", sa.Uuid(), nullable=False),
        sa.Column("realism_score", sa.Integer(), nullable=True),
        sa.Column("constraints", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("locale", sa.String(length=2), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("locale IN ('fr', 'en')"),
        sa.CheckConstraint("realism_score IS NULL OR (realism_score BETWEEN 0 AND 100)"),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["iteration_id"], ["iterations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("iteration_id"),
    )
    op.create_index(
        op.f("ix_constraint_analyses_idea_id"), "constraint_analyses", ["idea_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_constraint_analyses_idea_id"), table_name="constraint_analyses")
    op.drop_table("constraint_analyses")
