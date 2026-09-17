"""Link experiments to decision spaces and their options.

Revision ID: c8a4f1d29e63
Revises: e1b7c9d3f425
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c8a4f1d29e63"
down_revision: str | Sequence[str] | None = "e1b7c9d3f425"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("experiments", sa.Column("decision_space_id", sa.Uuid(), nullable=True))
    op.add_column("experiments", sa.Column("option_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "experiments_decision_space_id_fkey",
        "experiments",
        "decision_spaces",
        ["decision_space_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "experiments_option_id_fkey",
        "experiments",
        "options",
        ["option_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_experiments_decision_space_id"),
        "experiments",
        ["decision_space_id"],
        unique=False,
    )
    op.create_index(op.f("ix_experiments_option_id"), "experiments", ["option_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_experiments_option_id"), table_name="experiments")
    op.drop_index(op.f("ix_experiments_decision_space_id"), table_name="experiments")
    op.drop_constraint("experiments_option_id_fkey", "experiments", type_="foreignkey")
    op.drop_constraint("experiments_decision_space_id_fkey", "experiments", type_="foreignkey")
    op.drop_column("experiments", "option_id")
    op.drop_column("experiments", "decision_space_id")
