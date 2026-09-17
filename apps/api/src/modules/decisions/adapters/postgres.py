from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
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
from src.modules.options.adapters.postgres import Option
from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
RATIONALE_CHECK = "length(btrim(rationale)) > 0"
VERSION_CHECK = "version >= 1"
SIDE_CHECK = "side IN ('for', 'against')"


class Decision(Base):
    __tablename__ = "decisions"
    __table_args__ = (
        CheckConstraint(LANG_CHECK),
        CheckConstraint(RATIONALE_CHECK),
        CheckConstraint(VERSION_CHECK),
        UniqueConstraint("space_id", "version"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int]
    selected_option_id: Mapped[UUID] = mapped_column(ForeignKey("options.id", ondelete="CASCADE"))
    rationale: Mapped[str] = mapped_column(Text)
    critical_assumptions: Mapped[str | None] = mapped_column(Text)
    uncertainty: Mapped[str | None] = mapped_column(Text)
    success_criteria: Mapped[str | None] = mapped_column(Text)
    revisit_triggers: Mapped[list[dict[str, object]] | None] = mapped_column(JSON)
    reviewer_ids: Mapped[list[str]] = mapped_column(JSON)
    decided_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionRejectedAlternative(Base):
    __tablename__ = "decision_rejected_alternatives"

    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), primary_key=True
    )
    option_id: Mapped[UUID] = mapped_column(
        ForeignKey("options.id", ondelete="CASCADE"), primary_key=True
    )


class DecisionArgument(Base):
    __tablename__ = "decision_arguments"
    __table_args__ = (CheckConstraint(SIDE_CHECK),)

    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"), primary_key=True
    )
    contribution_id: Mapped[UUID] = mapped_column(
        ForeignKey("contributions.id", ondelete="CASCADE"), primary_key=True
    )
    side: Mapped[str] = mapped_column(String(10))


class PostgresDecisions:
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

    async def space(self, workspace_id: UUID, space_id: UUID) -> DecisionSpace | None:
        space = await self.session.get(DecisionSpace, space_id)
        if space is None or space.workspace_id != workspace_id:
            return None
        return space

    async def participant_ids(self, space_id: UUID) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(DecisionSpaceParticipant.user_id).where(
                DecisionSpaceParticipant.space_id == space_id
            )
        )
        return frozenset(rows.scalars().all())

    async def option(self, space_id: UUID, option_id: UUID) -> Option | None:
        return await self.session.scalar(
            select(Option).where(Option.id == option_id, Option.space_id == space_id)
        )

    async def contribution(self, contribution_id: UUID) -> Contribution | None:
        return await self.session.get(Contribution, contribution_id)

    async def latest(self, space_id: UUID) -> Decision | None:
        return await self.session.scalar(
            select(Decision)
            .where(Decision.space_id == space_id)
            .order_by(Decision.version.desc())
            .limit(1)
        )

    async def version(self, space_id: UUID, version: int) -> Decision | None:
        return await self.session.scalar(
            select(Decision).where(Decision.space_id == space_id, Decision.version == version)
        )

    async def all_versions(self, space_id: UUID) -> list[Decision]:
        rows = await self.session.execute(
            select(Decision).where(Decision.space_id == space_id).order_by(Decision.version.desc())
        )
        return list(rows.scalars().all())

    async def next_version(self, space_id: UUID) -> int:
        highest = await self.session.scalar(
            select(func.max(Decision.version)).where(Decision.space_id == space_id)
        )
        return int(highest or 0) + 1

    async def alternatives(self, decision_id: UUID) -> list[UUID]:
        rows = await self.session.execute(
            select(DecisionRejectedAlternative.option_id).where(
                DecisionRejectedAlternative.decision_id == decision_id
            )
        )
        return list(rows.scalars().all())

    async def arguments(self, decision_id: UUID) -> list[DecisionArgument]:
        rows = await self.session.execute(
            select(DecisionArgument)
            .where(DecisionArgument.decision_id == decision_id)
            .order_by(DecisionArgument.side, DecisionArgument.contribution_id)
        )
        return list(rows.scalars().all())

    async def argument_for(
        self, decision_id: UUID, contribution_id: UUID
    ) -> DecisionArgument | None:
        return await self.session.scalar(
            select(DecisionArgument).where(
                DecisionArgument.decision_id == decision_id,
                DecisionArgument.contribution_id == contribution_id,
            )
        )

    async def create(
        self,
        *,
        space_id: UUID,
        version: int,
        selected_option_id: UUID,
        rationale: str,
        critical_assumptions: str | None,
        uncertainty: str | None,
        success_criteria: str | None,
        revisit_triggers: list[dict[str, str | None]] | None,
        reviewer_ids: list[str],
        decided_by: UUID,
        lang: str,
        alternative_ids: list[UUID],
        arguments: list[tuple[UUID, str]],
    ) -> Decision:
        decision = Decision(
            id=uuid4(),
            space_id=space_id,
            version=version,
            selected_option_id=selected_option_id,
            rationale=rationale,
            critical_assumptions=critical_assumptions,
            uncertainty=uncertainty,
            success_criteria=success_criteria,
            revisit_triggers=revisit_triggers,
            reviewer_ids=reviewer_ids,
            decided_by=decided_by,
            lang=lang,
        )
        self.session.add(decision)
        for option_id in alternative_ids:
            self.session.add(
                DecisionRejectedAlternative(decision_id=decision.id, option_id=option_id)
            )
        for contribution_id, side in arguments:
            self.session.add(
                DecisionArgument(
                    decision_id=decision.id,
                    contribution_id=contribution_id,
                    side=side,
                )
            )
        await self.session.flush()
        await self.session.refresh(decision)
        return decision
