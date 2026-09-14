"""split team roles into participation and business function

Revision ID: 9f3c7a2b6e14
Revises: 7b1f0c2e9a55
Create Date: 2026-09-14

"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from src.modules.ideas.domain.team import LEGACY_ROLE_TO_FUNCTION

# revision identifiers, used by Alembic.
revision: str = "9f3c7a2b6e14"
down_revision: str | Sequence[str] | None = "7b1f0c2e9a55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

BUSINESS_FUNCTIONS = (
    "marketing",
    "sales",
    "finance",
    "product",
    "engineering",
    "customer_success",
    "operations",
    "legal",
    "hr",
    "data",
    "direction",
    "other",
)
PARTICIPATIONS = (
    "owner",
    "decision_maker",
    "contributor",
    "observer",
)
FUNCTION_CHECK = (
    "business_function IN (" + ", ".join(f"'{value}'" for value in BUSINESS_FUNCTIONS) + ")"
)
PARTICIPATION_CHECK = (
    "participation IN (" + ", ".join(f"'{value}'" for value in PARTICIPATIONS) + ")"
)
REVERSE_MAP = {function: role for role, function in reversed(list(LEGACY_ROLE_TO_FUNCTION.items()))}


def upgrade() -> None:
    bind = op.get_bind()

    # Memberships: add the two axes, map the legacy craft role once, drop it.
    op.add_column(
        "idea_memberships",
        sa.Column(
            "participation",
            sa.String(length=20),
            server_default=sa.text("'contributor'"),
            nullable=False,
        ),
    )
    op.add_column(
        "idea_memberships", sa.Column("business_function", sa.String(length=32), nullable=True)
    )
    for role, function in LEGACY_ROLE_TO_FUNCTION.items():
        bind.execute(
            sa.text(
                "UPDATE idea_memberships SET business_function = :function, "
                "participation = :participation WHERE role = :role"
            ),
            {
                "function": function,
                "participation": "owner" if function == "direction" else "contributor",
                "role": role,
            },
        )
    bind.execute(
        sa.text(
            "UPDATE idea_memberships SET business_function = 'other' "
            "WHERE business_function IS NULL"
        )
    )
    op.alter_column("idea_memberships", "business_function", nullable=False)
    op.drop_column("idea_memberships", "role")
    op.create_check_constraint(
        "idea_memberships_participation_check", "idea_memberships", PARTICIPATION_CHECK
    )
    op.create_check_constraint(
        "idea_memberships_function_check", "idea_memberships", FUNCTION_CHECK
    )

    # Applications: the requested craft role becomes the requested function.
    op.drop_constraint("idea_join_requests_role_check", "idea_join_requests", type_="check")
    op.alter_column("idea_join_requests", "role", new_column_name="business_function")
    op.alter_column("idea_join_requests", "business_function", type_=sa.String(length=32))
    for role, function in LEGACY_ROLE_TO_FUNCTION.items():
        bind.execute(
            sa.text(
                "UPDATE idea_join_requests SET business_function = :function "
                "WHERE business_function = :role"
            ),
            {"function": function, "role": role},
        )
    known = ", ".join(f"'{value}'" for value in BUSINESS_FUNCTIONS)
    bind.execute(
        sa.text(
            f"UPDATE idea_join_requests SET business_function = 'other' "
            f"WHERE business_function NOT IN ({known})"
        )
    )
    op.create_check_constraint(
        "idea_join_requests_function_check", "idea_join_requests", FUNCTION_CHECK
    )

    # The sought values move to the function axis; the column keeps its name.
    rows = bind.execute(sa.text("SELECT id, sought_roles FROM ideas")).all()
    for idea_id, sought in rows:
        mapped = [LEGACY_ROLE_TO_FUNCTION.get(value, "other") for value in (sought or [])]
        bind.execute(
            sa.text("UPDATE ideas SET sought_roles = CAST(:value AS jsonb) WHERE id = :id"),
            {"value": json.dumps(mapped), "id": idea_id},
        )


def downgrade() -> None:
    bind = op.get_bind()
    for function, role in REVERSE_MAP.items():
        bind.execute(
            sa.text(
                "UPDATE ideas SET sought_roles = "
                "replace(sought_roles::text, :function, :role)::jsonb"
            ),
            {"function": function, "role": role},
        )

    op.drop_constraint("idea_join_requests_function_check", "idea_join_requests", type_="check")
    op.alter_column("idea_join_requests", "business_function", new_column_name="role")
    for function, role in REVERSE_MAP.items():
        bind.execute(
            sa.text("UPDATE idea_join_requests SET role = :role WHERE role = :function"),
            {"role": role, "function": function},
        )
    op.create_check_constraint(
        "idea_join_requests_role_check", "idea_join_requests", "role <> 'owner'"
    )

    op.drop_constraint("idea_memberships_function_check", "idea_memberships", type_="check")
    op.drop_constraint("idea_memberships_participation_check", "idea_memberships", type_="check")
    op.add_column("idea_memberships", sa.Column("role", sa.String(), nullable=True))
    for function, role in REVERSE_MAP.items():
        bind.execute(
            sa.text("UPDATE idea_memberships SET role = :role WHERE business_function = :function"),
            {"role": role, "function": function},
        )
    bind.execute(sa.text("UPDATE idea_memberships SET role = 'product' WHERE role IS NULL"))
    op.alter_column("idea_memberships", "role", nullable=False)
    op.drop_column("idea_memberships", "business_function")
    op.drop_column("idea_memberships", "participation")
