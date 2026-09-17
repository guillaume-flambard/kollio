"""Add options and their evidence links.

Revision ID: a2c7e5b81f46
Revises: f7d2a9c4e1b8
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a2c7e5b81f46"
down_revision: str | Sequence[str] | None = "f7d2a9c4e1b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TITLE_CHECK = "length(btrim(title)) > 0"
PROPOSAL_CHECK = "length(btrim(proposal)) > 0"
LANG_CHECK = "lang IN ('fr', 'en')"
SIDE_CHECK = "side IN ('for', 'against')"


def upgrade() -> None:
    op.create_table(
        "options",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("proposal", sa.Text(), nullable=False),
        sa.Column("mechanism", sa.Text(), nullable=True),
        sa.Column("upside", sa.Text(), nullable=True),
        sa.Column("cost", sa.Text(), nullable=True),
        sa.Column("risks", sa.Text(), nullable=True),
        sa.Column("critical_assumptions", sa.Text(), nullable=True),
        sa.Column("success_metrics", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
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
        sa.CheckConstraint(TITLE_CHECK, name="options_title_not_blank"),
        sa.CheckConstraint(PROPOSAL_CHECK, name="options_proposal_not_blank"),
        sa.CheckConstraint(LANG_CHECK, name="options_lang_check"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_options_space_id"), "options", ["space_id"], unique=False)

    op.create_table(
        "option_evidence",
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.Column("contribution_id", sa.Uuid(), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(SIDE_CHECK, name="option_evidence_side_check"),
        sa.ForeignKeyConstraint(["option_id"], ["options.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contribution_id"], ["contributions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("option_id", "contribution_id"),
    )


def downgrade() -> None:
    op.drop_table("option_evidence")
    op.drop_index(op.f("ix_options_space_id"), table_name="options")
    op.drop_table("options")
