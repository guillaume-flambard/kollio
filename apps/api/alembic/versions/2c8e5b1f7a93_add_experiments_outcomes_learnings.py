"""add experiments, outcomes and learnings

Revision ID: 2c8e5b1f7a93
Revises: 9f3c7a2b6e14
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "2c8e5b1f7a93"
down_revision: str | Sequence[str] | None = "9f3c7a2b6e14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EXPERIMENT_STATUS_CHECK = "status IN ('proposed', 'running', 'completed', 'cancelled')"
LEARNING_STATUS_CHECK = "status IN ('draft', 'confirmed')"


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("success_metric", sa.String(length=300), nullable=False),
        sa.Column("baseline", sa.String(length=200), nullable=True),
        sa.Column("target", sa.String(length=200), nullable=True),
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'proposed'"), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(EXPERIMENT_STATUS_CHECK),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_experiments_idea_id"), "experiments", ["idea_id"], unique=False)
    op.create_table(
        "experiment_outcomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("recorded_by_id", sa.Uuid(), nullable=False),
        sa.Column("metric", sa.String(length=200), nullable=False),
        sa.Column("value", sa.String(length=200), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("observed_at", sa.Date(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("qualitative", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_experiment_outcomes_experiment_id"),
        "experiment_outcomes",
        ["experiment_id"],
        unique=False,
    )
    op.create_table(
        "learnings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'draft'"), nullable=False
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("outcome_ids", sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False),
        sa.Column("confirmed_by_id", sa.Uuid(), nullable=True),
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
        sa.CheckConstraint(LEARNING_STATUS_CHECK),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["confirmed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("experiment_id"),
    )
    op.create_index(op.f("ix_learnings_idea_id"), "learnings", ["idea_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_learnings_idea_id"), table_name="learnings")
    op.drop_table("learnings")
    op.drop_index(op.f("ix_experiment_outcomes_experiment_id"), table_name="experiment_outcomes")
    op.drop_table("experiment_outcomes")
    op.drop_index(op.f("ix_experiments_idea_id"), table_name="experiments")
    op.drop_table("experiments")
