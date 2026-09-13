"""add constraint analysis workflows

Revision ID: 7675b6c21b8e
Revises: 04f3435ac590
Create Date: 2026-09-12 22:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "7675b6c21b8e"
down_revision: str | Sequence[str] | None = "04f3435ac590"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_workflows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("source_iteration_id", sa.Uuid(), nullable=True),
        sa.Column("requested_by_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("locale", sa.String(length=2), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("current_step", sa.String(length=64), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("draft_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("review_decision", sa.Boolean(), nullable=True),
        sa.Column("trace_context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("locale IN ('fr', 'en')"),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'awaiting_review', 'review_queued', "
            "'completed', 'rejected', 'failed')"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_iteration_id"], ["iterations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", "idempotency_key"),
    )
    op.create_index(op.f("ix_analysis_workflows_idea_id"), "analysis_workflows", ["idea_id"])
    op.create_table(
        "constraint_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("source_iteration_id", sa.Uuid(), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column("locale", sa.String(length=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_iteration_id"], ["iterations.id"]),
        sa.ForeignKeyConstraint(["workflow_id"], ["analysis_workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_id"),
    )
    op.create_index(op.f("ix_constraint_analyses_idea_id"), "constraint_analyses", ["idea_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_constraint_analyses_idea_id"), table_name="constraint_analyses")
    op.drop_table("constraint_analyses")
    op.drop_index(op.f("ix_analysis_workflows_idea_id"), table_name="analysis_workflows")
    op.drop_table("analysis_workflows")
