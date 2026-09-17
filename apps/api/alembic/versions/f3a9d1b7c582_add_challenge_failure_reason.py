"""Record why a challenge run failed.

Revision ID: f3a9d1b7c582
Revises: c8a4f1d29e63
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f3a9d1b7c582"
down_revision: str | Sequence[str] | None = "c8a4f1d29e63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("challenge_runs", sa.Column("failure_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("challenge_runs", "failure_reason")
