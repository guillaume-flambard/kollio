"""Add exploration branches and contributions.

Revision ID: e8b4d6f2a937
Revises: c4e9b7a2d815
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e8b4d6f2a937"
down_revision: str | Sequence[str] | None = "c4e9b7a2d815"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

VISIBILITY_CHECK = "visibility IN ('private', 'shared')"
BRANCH_TITLE_CHECK = "length(btrim(title)) > 0"
KIND_CHECK = "kind IN ('idea', 'claim', 'evidence', 'objection', 'constraint')"
CONTRIBUTION_STATUS_CHECK = "status IN ('suggested', 'confirmed')"
CONTRIBUTION_TITLE_CHECK = "length(btrim(title)) > 0"
LANG_CHECK = "lang IN ('fr', 'en')"


def upgrade() -> None:
    op.create_table(
        "branches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_idea_id", sa.Uuid(), nullable=True),
        sa.Column("visibility", sa.String(length=10), nullable=False),
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
        sa.CheckConstraint(VISIBILITY_CHECK, name="branches_visibility_check"),
        sa.CheckConstraint(LANG_CHECK, name="branches_lang_check"),
        sa.CheckConstraint(BRANCH_TITLE_CHECK, name="branches_title_not_blank"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_idea_id"], ["ideas.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("source_idea_id", name="branches_source_idea_id_key"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_branches_space_id"), "branches", ["space_id"], unique=False)

    op.create_table(
        "contributions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("tool_model", sa.String(length=200), nullable=True),
        sa.Column("transformation_history", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=10), nullable=False),
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
        sa.CheckConstraint(KIND_CHECK, name="contributions_kind_check"),
        sa.CheckConstraint(CONTRIBUTION_STATUS_CHECK, name="contributions_status_check"),
        sa.CheckConstraint(LANG_CHECK, name="contributions_lang_check"),
        sa.CheckConstraint(CONTRIBUTION_TITLE_CHECK, name="contributions_title_not_blank"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contributions_space_id"), "contributions", ["space_id"], unique=False)
    op.create_index(
        op.f("ix_contributions_branch_id"), "contributions", ["branch_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_contributions_branch_id"), table_name="contributions")
    op.drop_index(op.f("ix_contributions_space_id"), table_name="contributions")
    op.drop_table("contributions")
    op.drop_index(op.f("ix_branches_space_id"), table_name="branches")
    op.drop_table("branches")
