"""reconcile: proposal rationale, sought roles, join requests and departures

Revision ID: 4d2e8f1a9b37
Revises: 7675b6c21b8e
Create Date: 2026-09-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4d2e8f1a9b37"
down_revision: str | Sequence[str] | None = "7675b6c21b8e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("iterations", sa.Column("rationale", sa.String(length=500), nullable=True))
    op.add_column(
        "ideas",
        sa.Column(
            "sought_roles",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.create_table(
        "idea_join_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("requester_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("rationale", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'accepted', 'rejected')"),
        sa.CheckConstraint("role <> 'owner'"),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", "requester_id", "status"),
    )
    op.create_index(
        op.f("ix_idea_join_requests_idea_id"), "idea_join_requests", ["idea_id"], unique=False
    )
    op.create_table(
        "idea_departures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("direction IN ('left', 'removed')"),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_idea_departures_idea_id"), "idea_departures", ["idea_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_idea_departures_idea_id"), table_name="idea_departures")
    op.drop_table("idea_departures")
    op.drop_index(op.f("ix_idea_join_requests_idea_id"), table_name="idea_join_requests")
    op.drop_table("idea_join_requests")
    op.drop_column("ideas", "sought_roles")
    op.drop_column("iterations", "rationale")
