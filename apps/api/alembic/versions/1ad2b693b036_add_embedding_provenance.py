"""add embedding provenance

Revision ID: 1ad2b693b036
Revises: 6852a69d3f1d
Create Date: 2026-09-11 21:22:26.987920

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1ad2b693b036"
down_revision: str | Sequence[str] | None = "6852a69d3f1d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("idea_embeddings_model_check", "idea_embeddings", type_="check")
    op.drop_constraint("idea_embeddings_lang_check", "idea_embeddings", type_="check")
    op.drop_constraint("idea_embeddings_pkey", "idea_embeddings", type_="primary")
    op.alter_column("idea_embeddings", "lang", new_column_name="source_language")
    op.add_column(
        "idea_embeddings",
        sa.Column("dimensions", sa.Integer(), server_default="1536", nullable=False),
    )
    op.add_column(
        "idea_embeddings",
        sa.Column("source_identifier", sa.String(), server_default="legacy", nullable=False),
    )
    op.add_column(
        "idea_embeddings",
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.execute("ALTER TABLE idea_embeddings ALTER COLUMN vector TYPE vector USING vector::vector")
    op.create_check_constraint(
        "idea_embeddings_source_language_check",
        "idea_embeddings",
        "source_language IN ('fr', 'en')",
    )
    op.create_check_constraint(
        "idea_embeddings_dimensions_check",
        "idea_embeddings",
        "dimensions = vector_dims(vector)",
    )
    op.create_primary_key(
        "idea_embeddings_pkey",
        "idea_embeddings",
        ["idea_id", "model", "dimensions"],
    )
    op.alter_column("idea_embeddings", "dimensions", server_default=None)
    op.alter_column("idea_embeddings", "source_identifier", server_default=None)
    op.alter_column("idea_embeddings", "provenance", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("idea_embeddings_pkey", "idea_embeddings", type_="primary")
    op.drop_constraint("idea_embeddings_dimensions_check", "idea_embeddings", type_="check")
    op.drop_constraint("idea_embeddings_source_language_check", "idea_embeddings", type_="check")
    op.execute(
        "DELETE FROM idea_embeddings WHERE model <> 'text-embedding-3-large' OR dimensions <> 1536"
    )
    op.execute(
        "ALTER TABLE idea_embeddings ALTER COLUMN vector TYPE vector(1536) "
        "USING vector::vector(1536)"
    )
    op.drop_column("idea_embeddings", "provenance")
    op.drop_column("idea_embeddings", "source_identifier")
    op.drop_column("idea_embeddings", "dimensions")
    op.alter_column("idea_embeddings", "source_language", new_column_name="lang")
    op.create_check_constraint(
        "idea_embeddings_model_check",
        "idea_embeddings",
        "model = 'text-embedding-3-large'",
    )
    op.create_check_constraint(
        "idea_embeddings_lang_check",
        "idea_embeddings",
        "lang IN ('fr', 'en')",
    )
    op.create_primary_key("idea_embeddings_pkey", "idea_embeddings", ["idea_id"])
