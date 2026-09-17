"""Add decision records, rejected alternatives and arguments.

Revision ID: d5a8f2b64c19
Revises: b9f1c3e7d520
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5a8f2b64c19"
down_revision: str | Sequence[str] | None = "b9f1c3e7d520"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LANG_CHECK = "lang IN ('fr', 'en')"
RATIONALE_CHECK = "length(btrim(rationale)) > 0"
VERSION_CHECK = "version >= 1"
SIDE_CHECK = "side IN ('for', 'against')"


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("selected_option_id", sa.Uuid(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("critical_assumptions", sa.Text(), nullable=True),
        sa.Column("uncertainty", sa.Text(), nullable=True),
        sa.Column("success_criteria", sa.Text(), nullable=True),
        sa.Column("revisit_triggers", sa.JSON(), nullable=True),
        sa.Column("reviewer_ids", sa.JSON(), nullable=False),
        sa.Column("decided_by", sa.Uuid(), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(LANG_CHECK, name="decisions_lang_check"),
        sa.CheckConstraint(RATIONALE_CHECK, name="decisions_rationale_not_blank"),
        sa.CheckConstraint(VERSION_CHECK, name="decisions_version_positive"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selected_option_id"], ["options.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("space_id", "version", name="decisions_space_version_key"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decisions_space_id"), "decisions", ["space_id"], unique=False)

    op.create_table(
        "decision_rejected_alternatives",
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["option_id"], ["options.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("decision_id", "option_id"),
    )

    op.create_table(
        "decision_arguments",
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("contribution_id", sa.Uuid(), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.CheckConstraint(SIDE_CHECK, name="decision_arguments_side_check"),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contribution_id"], ["contributions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("decision_id", "contribution_id"),
    )


def downgrade() -> None:
    op.drop_table("decision_arguments")
    op.drop_table("decision_rejected_alternatives")
    op.drop_index(op.f("ix_decisions_space_id"), table_name="decisions")
    op.drop_table("decisions")
