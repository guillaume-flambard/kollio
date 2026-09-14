"""add learning embeddings

Revision ID: 3d9a1f4c7b20
Revises: 2c8e5b1f7a93
Create Date: 2026-09-14

"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "3d9a1f4c7b20"
down_revision: str | Sequence[str] | None = "2c8e5b1f7a93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "learnings",
        "outcome_ids",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_type=sa.JSON(),
        postgresql_using="outcome_ids::jsonb",
    )
    op.create_table(
        "learning_embeddings",
        sa.Column("learning_id", sa.Uuid(), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", pgvector.sqlalchemy.Vector(), nullable=False),
        sa.Column("source_language", sa.String(length=2), nullable=False),
        sa.Column("source_identifier", sa.String(length=200), nullable=False),
        sa.Column("provenance", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("source_language IN ('fr', 'en')"),
        sa.CheckConstraint("dimensions = vector_dims(vector)"),
        sa.ForeignKeyConstraint(["learning_id"], ["learnings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("learning_id", "model", "dimensions"),
    )


def downgrade() -> None:
    op.drop_table("learning_embeddings")
    op.alter_column(
        "learnings",
        "outcome_ids",
        type_=sa.JSON(),
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        postgresql_using="outcome_ids::json",
    )
