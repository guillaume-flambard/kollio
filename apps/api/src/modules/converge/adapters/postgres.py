from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.branches.adapters.postgres import Contribution
from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.platform.db import Base

TYPE_CHECK = (
    "relation_type IN ('SUPPORTS', 'CONTRADICTS', 'DUPLICATES', 'ALTERNATIVE_TO', "
    "'DERIVED_FROM', 'SUPERSEDES', 'EVIDENCE_FOR', 'EVIDENCE_AGAINST')"
)
NO_SELF_CHECK = "from_contribution_id != to_contribution_id"
TITLE_CHECK = "length(btrim(title)) > 0"


class ContributionRelation(Base):
    __tablename__ = "contribution_relations"
    __table_args__ = (
        CheckConstraint(TYPE_CHECK),
        CheckConstraint(NO_SELF_CHECK),
        UniqueConstraint(
            "from_contribution_id",
            "to_contribution_id",
            name="contribution_relations_pair_key",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    from_contribution_id: Mapped[UUID] = mapped_column(
        ForeignKey("contributions.id", ondelete="CASCADE")
    )
    to_contribution_id: Mapped[UUID] = mapped_column(
        ForeignKey("contributions.id", ondelete="CASCADE")
    )
    relation_type: Mapped[str] = mapped_column(String(20))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Cluster(Base):
    __tablename__ = "clusters"
    __table_args__ = (CheckConstraint(TITLE_CHECK),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresConverge:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def memberships(self, subject: str) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(WorkspaceMembership.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(User.auth_subject == subject)
        )
        return frozenset(rows.scalars().all())

    async def user_for_subject(self, subject: str) -> User | None:
        return await self.session.scalar(select(User).where(User.auth_subject == subject))

    async def space(self, space_id: UUID) -> DecisionSpace | None:
        return await self.session.get(DecisionSpace, space_id)

    async def participant_ids(self, space_id: UUID) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(DecisionSpaceParticipant.user_id).where(
                DecisionSpaceParticipant.space_id == space_id
            )
        )
        return frozenset(rows.scalars().all())

    async def contribution(self, space_id: UUID, contribution_id: UUID) -> Contribution | None:
        return await self.session.scalar(
            select(Contribution).where(
                Contribution.id == contribution_id,
                Contribution.space_id == space_id,
            )
        )

    async def confirmed_contributions(self, space_id: UUID) -> list[Contribution]:
        rows = await self.session.execute(
            select(Contribution)
            .where(
                Contribution.space_id == space_id,
                Contribution.status == "confirmed",
            )
            .order_by(Contribution.created_at, Contribution.id)
        )
        return list(rows.scalars().all())

    async def create_relation(
        self,
        *,
        space_id: UUID,
        from_contribution_id: UUID,
        to_contribution_id: UUID,
        relation_type: str,
        created_by: UUID,
    ) -> ContributionRelation:
        relation = ContributionRelation(
            space_id=space_id,
            from_contribution_id=from_contribution_id,
            to_contribution_id=to_contribution_id,
            relation_type=relation_type,
            created_by=created_by,
        )
        self.session.add(relation)
        await self.session.flush()
        return relation

    async def relation_between(
        self, space_id: UUID, from_contribution_id: UUID, to_contribution_id: UUID
    ) -> ContributionRelation | None:
        return await self.session.scalar(
            select(ContributionRelation).where(
                ContributionRelation.space_id == space_id,
                ContributionRelation.from_contribution_id == from_contribution_id,
                ContributionRelation.to_contribution_id == to_contribution_id,
            )
        )

    async def relation(self, space_id: UUID, relation_id: UUID) -> ContributionRelation | None:
        return await self.session.scalar(
            select(ContributionRelation).where(
                ContributionRelation.id == relation_id,
                ContributionRelation.space_id == space_id,
            )
        )

    async def list_relations(self, space_id: UUID) -> list[ContributionRelation]:
        rows = await self.session.execute(
            select(ContributionRelation)
            .where(ContributionRelation.space_id == space_id)
            .order_by(ContributionRelation.created_at, ContributionRelation.id)
        )
        return list(rows.scalars().all())

    async def delete_relation(self, relation: ContributionRelation) -> None:
        await self.session.delete(relation)
        await self.session.flush()

    async def create_cluster(self, *, space_id: UUID, title: str, created_by: UUID) -> Cluster:
        cluster = Cluster(space_id=space_id, title=title, created_by=created_by)
        self.session.add(cluster)
        await self.session.flush()
        return cluster

    async def cluster(self, space_id: UUID, cluster_id: UUID) -> Cluster | None:
        return await self.session.scalar(
            select(Cluster).where(Cluster.id == cluster_id, Cluster.space_id == space_id)
        )

    async def list_clusters(self, space_id: UUID) -> list[Cluster]:
        rows = await self.session.execute(
            select(Cluster)
            .where(Cluster.space_id == space_id)
            .order_by(Cluster.created_at, Cluster.id)
        )
        return list(rows.scalars().all())

    async def delete_cluster(self, cluster: Cluster) -> None:
        await self.session.delete(cluster)
        await self.session.flush()

    async def assign_member(self, contribution: Contribution, cluster_id: UUID) -> Contribution:
        contribution.cluster_id = cluster_id
        await self.session.flush()
        await self.session.refresh(contribution)
        return contribution

    async def unassign_member(self, contribution: Contribution) -> Contribution:
        contribution.cluster_id = None
        await self.session.flush()
        await self.session.refresh(contribution)
        return contribution
