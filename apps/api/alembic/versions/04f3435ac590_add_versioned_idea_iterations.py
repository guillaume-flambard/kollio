"""add versioned idea iterations

Revision ID: 04f3435ac590
Revises: 9f71e3c62ad4
Create Date: 2026-09-12 18:16:40.327689

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "04f3435ac590"
down_revision: str | Sequence[str] | None = "9f71e3c62ad4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "iterations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("branch", sa.String(length=64), nullable=False),
        sa.Column("proposal_status", sa.String(length=16), nullable=True),
        sa.Column("short_hash", sa.String(length=12), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "proposal_status IS NULL OR proposal_status IN ('pending', 'accepted', 'rejected')"
        ),
        sa.CheckConstraint("lang IN ('fr', 'en')"),
        sa.CheckConstraint(
            "(branch = 'main' AND proposal_status IS NULL) OR "
            "(branch <> 'main' AND proposal_status IS NOT NULL)"
        ),
        sa.CheckConstraint("revision > 0"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["iterations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", "short_hash"),
        sa.UniqueConstraint("idea_id", "revision"),
    )
    op.create_index(op.f("ix_iterations_idea_id"), "iterations", ["idea_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_iterations_idea_id"), table_name="iterations")
    op.drop_table("iterations")
