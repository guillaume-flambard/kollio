from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
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

from src.modules.branches.adapters.postgres import Contribution
from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
TITLE_CHECK = "length(btrim(title)) > 0"
PROPOSAL_CHECK = "length(btrim(proposal)) > 0"
SIDE_CHECK = "side IN ('for', 'against')"


class Option(Base):
    __tablename__ = "options"
    __table_args__ = (
        CheckConstraint(TITLE_CHECK),
        CheckConstraint(PROPOSAL_CHECK),
        CheckConstraint(LANG_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str]
    proposal: Mapped[str] = mapped_column(Text)
    mechanism: Mapped[str | None] = mapped_column(Text)
    upside: Mapped[str | None] = mapped_column(Text)
    cost: Mapped[str | None] = mapped_column(Text)
    risks: Mapped[str | None] = mapped_column(Text)
    critical_assumptions: Mapped[str | None] = mapped_column(Text)
    success_metrics: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OptionEvidence(Base):
    __tablename__ = "option_evidence"
    __table_args__ = (CheckConstraint(SIDE_CHECK),)

    option_id: Mapped[UUID] = mapped_column(
        ForeignKey("options.id", ondelete="CASCADE"), primary_key=True
    )
    contribution_id: Mapped[UUID] = mapped_column(
        ForeignKey("contributions.id", ondelete="CASCADE"), primary_key=True
    )
    side: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresOptions:
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

    async def contribution(self, contribution_id: UUID) -> Contribution | None:
        return await self.session.get(Contribution, contribution_id)

    async def create_option(
        self,
        *,
        space_id: UUID,
        title: str,
        proposal: str,
        mechanism: str | None,
        upside: str | None,
        cost: str | None,
        risks: str | None,
        critical_assumptions: str | None,
        success_metrics: str | None,
        created_by: UUID,
        lang: str,
    ) -> Option:
        option = Option(
            space_id=space_id,
            title=title,
            proposal=proposal,
            mechanism=mechanism,
            upside=upside,
            cost=cost,
            risks=risks,
            critical_assumptions=critical_assumptions,
            success_metrics=success_metrics,
            created_by=created_by,
            lang=lang,
        )
        self.session.add(option)
        await self.session.flush()
        return option

    async def option(self, space_id: UUID, option_id: UUID) -> Option | None:
        return await self.session.scalar(
            select(Option).where(Option.id == option_id, Option.space_id == space_id)
        )

    async def list_for_space(self, space_id: UUID) -> list[Option]:
        rows = await self.session.execute(
            select(Option).where(Option.space_id == space_id).order_by(Option.created_at, Option.id)
        )
        return list(rows.scalars().all())

    async def update_option(self, option: Option, values: dict[str, object], lang: str) -> Option:
        for field, value in values.items():
            setattr(option, field, value)
        option.lang = lang
        await self.session.flush()
        await self.session.refresh(option)
        return option

    async def delete_option(self, option: Option) -> None:
        await self.session.delete(option)
        await self.session.flush()

    async def evidence(self, option_id: UUID) -> list[OptionEvidence]:
        rows = await self.session.execute(
            select(OptionEvidence)
            .where(OptionEvidence.option_id == option_id)
            .order_by(OptionEvidence.created_at, OptionEvidence.contribution_id)
        )
        return list(rows.scalars().all())

    async def evidence_for(self, option_id: UUID, contribution_id: UUID) -> OptionEvidence | None:
        return await self.session.get(OptionEvidence, (option_id, contribution_id))

    async def link_evidence(
        self, option_id: UUID, contribution_id: UUID, side: str
    ) -> OptionEvidence:
        link = OptionEvidence(option_id=option_id, contribution_id=contribution_id, side=side)
        self.session.add(link)
        await self.session.flush()
        return link

    async def unlink_evidence(self, link: OptionEvidence) -> None:
        await self.session.delete(link)
        await self.session.flush()
