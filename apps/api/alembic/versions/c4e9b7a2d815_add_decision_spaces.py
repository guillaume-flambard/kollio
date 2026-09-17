"""Add decision spaces, participation and status history.

Revision ID: c4e9b7a2d815
Revises: b6d24e8f1a07
Create Date: 2026-09-16
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c4e9b7a2d815"
down_revision: str | Sequence[str] | None = "b6d24e8f1a07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATUS_CHECK = (
    "status IN ('OPEN', 'EXPLORING', 'CONVERGING', 'READY_TO_DECIDE', "
    "'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
TO_STATUS_CHECK = (
    "to_status IN ('OPEN', 'EXPLORING', 'CONVERGING', 'READY_TO_DECIDE', "
    "'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
FROM_STATUS_CHECK = (
    "from_status IS NULL OR from_status IN ('OPEN', 'EXPLORING', 'CONVERGING', "
    "'READY_TO_DECIDE', 'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
QUESTION_CHECK = "length(btrim(question)) > 0"
LANG_CHECK = "lang IN ('fr', 'en')"


def upgrade() -> None:
    op.create_table(
        "decision_spaces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("lang", sa.String(length=2), nullable=False),
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
        sa.CheckConstraint(STATUS_CHECK, name="decision_spaces_status_check"),
        sa.CheckConstraint(QUESTION_CHECK, name="decision_spaces_question_not_blank"),
        sa.CheckConstraint(LANG_CHECK, name="decision_spaces_lang_check"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_decision_spaces_workspace_id"), "decision_spaces", ["workspace_id"], unique=False
    )

    op.create_table(
        "decision_space_participants",
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("space_id", "user_id"),
    )

    op.create_table(
        "decision_space_status_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("seq", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=True),
        sa.Column("to_status", sa.String(length=20), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(TO_STATUS_CHECK, name="decision_space_status_events_to_status_check"),
        sa.CheckConstraint(
            FROM_STATUS_CHECK, name="decision_space_status_events_from_status_check"
        ),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_decision_space_status_events_space_id"),
        "decision_space_status_events",
        ["space_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_decision_space_status_events_space_id"),
        table_name="decision_space_status_events",
    )
    op.drop_table("decision_space_status_events")
    op.drop_table("decision_space_participants")
    op.drop_index(op.f("ix_decision_spaces_workspace_id"), table_name="decision_spaces")
    op.drop_table("decision_spaces")
