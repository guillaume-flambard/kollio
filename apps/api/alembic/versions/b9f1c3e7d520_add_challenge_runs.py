"""Add challenge runs and findings.

Revision ID: b9f1c3e7d520
Revises: a2c7e5b81f46
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b9f1c3e7d520"
down_revision: str | Sequence[str] | None = "a2c7e5b81f46"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RUN_STATUS_CHECK = "status IN ('OPEN', 'RUNNING', 'COMPLETED', 'FAILED')"
KIND_CHECK = (
    "kind IN ('unsupported_assumption', 'contradictory_evidence', 'hidden_dependency', "
    "'failure_mode', 'causal_claim', 'missing_success_criteria')"
)
SEVERITY_CHECK = "severity IN ('low', 'medium', 'high')"
ORIGIN_CHECK = "origin IN ('human', 'critic')"
FINDING_STATUS_CHECK = "status IN ('proposed', 'confirmed', 'dismissed')"
DETAIL_CHECK = "length(btrim(detail)) > 0"
LANG_CHECK = "lang IN ('fr', 'en')"


def upgrade() -> None:
    op.create_table(
        "challenge_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("opened_by", sa.Uuid(), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=True),
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
        sa.CheckConstraint(RUN_STATUS_CHECK, name="challenge_runs_status_check"),
        sa.CheckConstraint(LANG_CHECK, name="challenge_runs_lang_check"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["option_id"], ["options.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opened_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_challenge_runs_space_id"), "challenge_runs", ["space_id"], unique=False
    )
    op.create_index(
        op.f("ix_challenge_runs_option_id"), "challenge_runs", ["option_id"], unique=False
    )

    op.create_table(
        "challenge_findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=10), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("origin", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("contribution_id", sa.Uuid(), nullable=True),
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
        sa.CheckConstraint(KIND_CHECK, name="challenge_findings_kind_check"),
        sa.CheckConstraint(SEVERITY_CHECK, name="challenge_findings_severity_check"),
        sa.CheckConstraint(ORIGIN_CHECK, name="challenge_findings_origin_check"),
        sa.CheckConstraint(FINDING_STATUS_CHECK, name="challenge_findings_status_check"),
        sa.CheckConstraint(DETAIL_CHECK, name="challenge_findings_detail_not_blank"),
        sa.CheckConstraint(LANG_CHECK, name="challenge_findings_lang_check"),
        sa.ForeignKeyConstraint(["run_id"], ["challenge_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contribution_id"], ["contributions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_challenge_findings_run_id"),
        "challenge_findings",
        ["run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_challenge_findings_run_id"), table_name="challenge_findings")
    op.drop_table("challenge_findings")
    op.drop_index(op.f("ix_challenge_runs_option_id"), table_name="challenge_runs")
    op.drop_index(op.f("ix_challenge_runs_space_id"), table_name="challenge_runs")
    op.drop_table("challenge_runs")
