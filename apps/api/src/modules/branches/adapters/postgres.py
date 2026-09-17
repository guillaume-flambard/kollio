from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.ideas.adapters.postgres import Idea, User, WorkspaceMembership
from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
VISIBILITY_CHECK = "visibility IN ('private', 'shared')"
BRANCH_TITLE_CHECK = "length(btrim(title)) > 0"
KIND_CHECK = "kind IN ('idea', 'claim', 'evidence', 'objection', 'constraint')"
CONTRIBUTION_STATUS_CHECK = "status IN ('suggested', 'confirmed')"
CONTRIBUTION_TITLE_CHECK = "length(btrim(title)) > 0"


class Branch(Base):
    __tablename__ = "branches"
    __table_args__ = (
        CheckConstraint(VISIBILITY_CHECK),
        CheckConstraint(LANG_CHECK),
        CheckConstraint(BRANCH_TITLE_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str]
    summary: Mapped[str | None] = mapped_column(Text)
    source_idea_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ideas.id", ondelete="SET NULL"), unique=True
    )
    visibility: Mapped[str] = mapped_column(String(10))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Contribution(Base):
    __tablename__ = "contributions"
    __table_args__ = (
        CheckConstraint(KIND_CHECK),
        CheckConstraint(CONTRIBUTION_STATUS_CHECK),
        CheckConstraint(LANG_CHECK),
        CheckConstraint(CONTRIBUTION_TITLE_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    branch_id: Mapped[UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), index=True
    )
    cluster_id: Mapped[UUID | None] = mapped_column(ForeignKey("clusters.id", ondelete="SET NULL"))
    kind: Mapped[str] = mapped_column(String(20))
    title: Mapped[str]
    body: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    source: Mapped[str | None] = mapped_column(Text)
    tool_model: Mapped[str | None] = mapped_column(String(200))
    transformation_history: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(10))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PostgresBranches:
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

    async def is_workspace_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        row = await self.session.scalar(
            select(WorkspaceMembership).where(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
        )
        return row is not None

    async def space(self, space_id: UUID) -> DecisionSpace | None:
        return await self.session.get(DecisionSpace, space_id)

    async def idea(self, idea_id: UUID) -> Idea | None:
        return await self.session.get(Idea, idea_id)

    async def participant_ids(self, space_id: UUID) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(DecisionSpaceParticipant.user_id).where(
                DecisionSpaceParticipant.space_id == space_id
            )
        )
        return frozenset(rows.scalars().all())

    async def branch_for_idea(self, idea_id: UUID) -> Branch | None:
        return await self.session.scalar(select(Branch).where(Branch.source_idea_id == idea_id))

    async def create_branch(
        self,
        *,
        space_id: UUID,
        title: str,
        summary: str | None,
        visibility: str,
        created_by: UUID,
        source_idea_id: UUID | None,
        lang: str,
    ) -> Branch:
        branch = Branch(
            space_id=space_id,
            title=title,
            summary=summary,
            visibility=visibility,
            created_by=created_by,
            source_idea_id=source_idea_id,
            lang=lang,
        )
        self.session.add(branch)
        await self.session.flush()
        return branch

    async def branch(self, space_id: UUID, branch_id: UUID) -> Branch | None:
        return await self.session.scalar(
            select(Branch).where(Branch.id == branch_id, Branch.space_id == space_id)
        )

    async def list_for_space(self, space_id: UUID) -> list[Branch]:
        rows = await self.session.execute(
            select(Branch).where(Branch.space_id == space_id).order_by(Branch.created_at, Branch.id)
        )
        return list(rows.scalars().all())

    async def create_contribution(
        self,
        *,
        space_id: UUID,
        branch_id: UUID,
        kind: str,
        title: str,
        body: str | None,
        author_id: UUID,
        source: str | None,
        tool_model: str | None,
        transformation_history: dict | None,
        status: str,
        lang: str,
    ) -> Contribution:
        contribution = Contribution(
            space_id=space_id,
            branch_id=branch_id,
            kind=kind,
            title=title,
            body=body,
            author_id=author_id,
            source=source,
            tool_model=tool_model,
            transformation_history=transformation_history,
            status=status,
            lang=lang,
        )
        self.session.add(contribution)
        await self.session.flush()
        return contribution

    async def contribution(self, space_id: UUID, contribution_id: UUID) -> Contribution | None:
        return await self.session.scalar(
            select(Contribution).where(
                Contribution.id == contribution_id,
                Contribution.space_id == space_id,
            )
        )

    async def list_contributions_for_space(self, space_id: UUID) -> list[Contribution]:
        rows = await self.session.execute(
            select(Contribution)
            .where(Contribution.space_id == space_id)
            .order_by(Contribution.created_at, Contribution.id)
        )
        return list(rows.scalars().all())

    async def confirm_contribution(
        self, contribution: Contribution, confirmer_id: UUID
    ) -> Contribution:
        contribution.status = "confirmed"
        contribution.author_id = confirmer_id
        await self.session.flush()
        await self.session.refresh(contribution)
        return contribution
