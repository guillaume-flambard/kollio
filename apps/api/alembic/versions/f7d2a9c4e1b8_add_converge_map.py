"""Add the converge map: relations and clusters.

Revision ID: f7d2a9c4e1b8
Revises: e8b4d6f2a937
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f7d2a9c4e1b8"
down_revision: str | Sequence[str] | None = "e8b4d6f2a937"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TYPE_CHECK = (
    "relation_type IN ('SUPPORTS', 'CONTRADICTS', 'DUPLICATES', 'ALTERNATIVE_TO', "
    "'DERIVED_FROM', 'SUPERSEDES', 'EVIDENCE_FOR', 'EVIDENCE_AGAINST')"
)
NO_SELF_CHECK = "from_contribution_id != to_contribution_id"
TITLE_CHECK = "length(btrim(title)) > 0"


def upgrade() -> None:
    op.create_table(
        "clusters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(TITLE_CHECK, name="clusters_title_not_blank"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clusters_space_id"), "clusters", ["space_id"], unique=False)

    op.create_table(
        "contribution_relations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("space_id", sa.Uuid(), nullable=False),
        sa.Column("from_contribution_id", sa.Uuid(), nullable=False),
        sa.Column("to_contribution_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(TYPE_CHECK, name="contribution_relations_type_check"),
        sa.CheckConstraint(NO_SELF_CHECK, name="contribution_relations_no_self"),
        sa.ForeignKeyConstraint(["space_id"], ["decision_spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_contribution_id"], ["contributions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_contribution_id"], ["contributions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "from_contribution_id",
            "to_contribution_id",
            name="contribution_relations_pair_key",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_contribution_relations_space_id"),
        "contribution_relations",
        ["space_id"],
        unique=False,
    )

    op.add_column("contributions", sa.Column("cluster_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "contributions_cluster_id_fkey",
        "contributions",
        "clusters",
        ["cluster_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("contributions_cluster_id_fkey", "contributions", type_="foreignkey")
    op.drop_column("contributions", "cluster_id")
    op.drop_index(
        op.f("ix_contribution_relations_space_id"),
        table_name="contribution_relations",
    )
    op.drop_table("contribution_relations")
    op.drop_index(op.f("ix_clusters_space_id"), table_name="clusters")
    op.drop_table("clusters")
