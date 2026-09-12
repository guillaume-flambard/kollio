"""add demo collaboration profiles

Revision ID: 9f71e3c62ad4
Revises: 1ad2b693b036
Create Date: 2026-09-12 16:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9f71e3c62ad4"
down_revision: str | Sequence[str] | None = "1ad2b693b036"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("handle", sa.String(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "roles",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("bio", sa.String(), nullable=True))
    op.add_column("users", sa.Column("avatar_key", sa.String(), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_demo", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_unique_constraint("uq_users_handle", "users", ["handle"])
    op.create_table(
        "idea_memberships",
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("idea_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("idea_memberships")
    op.drop_constraint("uq_users_handle", "users", type_="unique")
    op.drop_column("users", "is_demo")
    op.drop_column("users", "avatar_key")
    op.drop_column("users", "bio")
    op.drop_column("users", "roles")
    op.drop_column("users", "handle")
