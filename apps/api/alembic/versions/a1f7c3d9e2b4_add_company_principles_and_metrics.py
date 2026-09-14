"""add company principles and metrics

Revision ID: a1f7c3d9e2b4
Revises: 3d9a1f4c7b20
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1f7c3d9e2b4"
down_revision: str | Sequence[str] | None = "3d9a1f4c7b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATE_CHECK = "state IN ('active', 'archived')"
LANG_CHECK = "lang IN ('fr', 'en')"


def upgrade() -> None:
    op.create_table(
        "company_principles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("state", sa.String(length=16), nullable=False),
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
        sa.CheckConstraint(STATE_CHECK),
        sa.CheckConstraint(LANG_CHECK),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_company_principles_workspace_id"),
        "company_principles",
        ["workspace_id"],
        unique=False,
    )
    op.create_table(
        "company_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("value", sa.String(length=200), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("observed_at", sa.Date(), nullable=True),
        sa.Column("source", sa.String(length=300), nullable=True),
        sa.Column("state", sa.String(length=16), nullable=False),
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
        sa.CheckConstraint(STATE_CHECK),
        sa.CheckConstraint(LANG_CHECK),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_company_metrics_workspace_id"),
        "company_metrics",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_company_metrics_workspace_id"), table_name="company_metrics")
    op.drop_table("company_metrics")
    op.drop_index(op.f("ix_company_principles_workspace_id"), table_name="company_principles")
    op.drop_table("company_principles")
