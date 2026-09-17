"""Add scenario variables, runs and values.

Revision ID: e1b7c9d3f425
Revises: d5a8f2b64c19
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e1b7c9d3f425"
down_revision: str | Sequence[str] | None = "d5a8f2b64c19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LANG_CHECK = "lang IN ('fr', 'en')"
NAME_CHECK = "length(btrim(name)) > 0"
RANGE_CHECK = "low <= base AND base <= high"
LEVEL_CHECK = "level IN ('optimistic', 'base', 'pessimistic', 'failure')"
ASSUMPTIONS_CHECK = "length(btrim(assumptions)) > 0"


def upgrade() -> None:
    op.create_table(
        "scenario_variables",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("low", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("base", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("high", sa.Numeric(precision=18, scale=6), nullable=False),
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
        sa.CheckConstraint(NAME_CHECK, name="scenario_variables_name_not_blank"),
        sa.CheckConstraint(RANGE_CHECK, name="scenario_variables_range_ordered"),
        sa.CheckConstraint(LANG_CHECK, name="scenario_variables_lang_check"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("space_id", "name", name="scenario_variables_space_id_name_key"),
    )
    op.create_index(
        op.f("ix_scenario_variables_space_id"),
        "scenario_variables",
        ["space_id"],
        unique=False,
    )

    op.create_table(
        "scenario_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("option_id", sa.Uuid(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("assumptions", sa.Text(), nullable=False),
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
        sa.CheckConstraint(LEVEL_CHECK, name="scenario_runs_level_check"),
        sa.CheckConstraint(ASSUMPTIONS_CHECK, name="scenario_runs_assumptions_not_blank"),
        sa.CheckConstraint(LANG_CHECK, name="scenario_runs_lang_check"),
        sa.ForeignKeyConstraint(["option_id"], ["options.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scenario_runs_option_id"), "scenario_runs", ["option_id"], unique=False
    )
    op.create_index(
        "scenario_runs_one_base_per_option",
        "scenario_runs",
        ["option_id"],
        unique=True,
        postgresql_where=sa.text("level = 'base'"),
    )

    op.create_table(
        "scenario_run_values",
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("variable_id", sa.Uuid(), nullable=False),
        sa.Column("value", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["scenario_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variable_id"], ["scenario_variables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("run_id", "variable_id"),
    )


def downgrade() -> None:
    op.drop_table("scenario_run_values")
    op.drop_index("scenario_runs_one_base_per_option", table_name="scenario_runs")
    op.drop_index(op.f("ix_scenario_runs_option_id"), table_name="scenario_runs")
    op.drop_table("scenario_runs")
    op.drop_index(op.f("ix_scenario_variables_space_id"), table_name="scenario_variables")
    op.drop_table("scenario_variables")
