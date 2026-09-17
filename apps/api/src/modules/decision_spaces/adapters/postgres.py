from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    String,
    Text,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
STATUS_CHECK = (
    "status IN ('OPEN', 'EXPLORING', 'CONVERGING', 'READY_TO_DECIDE', "
    "'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
TO_STATUS_CHECK = (
    "to_status IN ('OPEN', 'EXPLORING', 'CONVERGING', 'READY_TO_DECIDE', "
    "'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
FROM_STATUS_CHECK = (
    "from_status IS NULL OR from_status IN ('OPEN', 'EXPLORING', 'CONVERGING', "
    "'READY_TO_DECIDE', 'DECIDED', 'TESTING', 'LEARNED', 'REOPENED')"
)
QUESTION_CHECK = "length(btrim(question)) > 0"


class DecisionSpace(Base):
    __tablename__ = "decision_spaces"
    __table_args__ = (
        CheckConstraint(STATUS_CHECK, name="decision_spaces_status_check"),
        CheckConstraint(QUESTION_CHECK, name="decision_spaces_question_not_blank"),
        CheckConstraint(LANG_CHECK, name="decision_spaces_lang_check"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    deadline: Mapped[date | None] = mapped_column(Date)
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DecisionSpaceParticipant(Base):
    __tablename__ = "decision_space_participants"

    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionSpaceStatusEvent(Base):
    __tablename__ = "decision_space_status_events"
    __table_args__ = (
        CheckConstraint(TO_STATUS_CHECK, name="decision_space_status_events_to_status_check"),
        CheckConstraint(FROM_STATUS_CHECK, name="decision_space_status_events_from_status_check"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    seq: Mapped[int] = mapped_column(BigInteger, Identity(always=True))
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresDecisionSpaces:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def memberships(self, subject: str) -> frozenset[UUID]:
        query = (
            select(WorkspaceMembership.workspace_id).join(User).where(User.auth_subject == subject)
        )
        return frozenset((await self.session.scalars(query)).all())

    async def is_workspace_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        query = select(WorkspaceMembership.workspace_id).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        return await self.session.scalar(query) is not None

    async def user_for_subject(self, subject: str) -> User | None:
        return await self.session.scalar(select(User).where(User.auth_subject == subject))

    async def create(
        self,
        *,
        workspace_id: UUID,
        question: str,
        description: str | None,
        deadline: date | None,
        owner_id: UUID,
        lang: str,
    ) -> DecisionSpace:
        space = DecisionSpace(
            id=uuid4(),
            workspace_id=workspace_id,
            question=question,
            description=description,
            owner_id=owner_id,
            status="OPEN",
            deadline=deadline,
            lang=lang,
        )
        self.session.add(space)
        self.session.add(DecisionSpaceParticipant(space_id=space.id, user_id=owner_id))
        self.session.add(
            DecisionSpaceStatusEvent(
                id=uuid4(),
                space_id=space.id,
                from_status=None,
                to_status="OPEN",
                actor_id=owner_id,
                reason=None,
            )
        )
        await self.session.flush()
        return space

    async def space(self, workspace_id: UUID, space_id: UUID) -> DecisionSpace | None:
        return await self.session.scalar(
            select(DecisionSpace).where(
                DecisionSpace.id == space_id,
                DecisionSpace.workspace_id == workspace_id,
            )
        )

    async def list_for_workspace(self, workspace_id: UUID) -> list[DecisionSpace]:
        query = (
            select(DecisionSpace)
            .where(DecisionSpace.workspace_id == workspace_id)
            .order_by(DecisionSpace.created_at, DecisionSpace.id)
        )
        return list((await self.session.scalars(query)).all())

    async def participants(self, space_id: UUID) -> list[DecisionSpaceParticipant]:
        query = (
            select(DecisionSpaceParticipant)
            .where(DecisionSpaceParticipant.space_id == space_id)
            .order_by(DecisionSpaceParticipant.created_at, DecisionSpaceParticipant.user_id)
        )
        return list((await self.session.scalars(query)).all())

    async def participant_ids(self, space_id: UUID) -> frozenset[UUID]:
        query = select(DecisionSpaceParticipant.user_id).where(
            DecisionSpaceParticipant.space_id == space_id
        )
        return frozenset((await self.session.scalars(query)).all())

    async def add_participant(self, space_id: UUID, user_id: UUID) -> DecisionSpaceParticipant:
        existing = await self.session.get(DecisionSpaceParticipant, (space_id, user_id))
        if existing is not None:
            return existing
        participant = DecisionSpaceParticipant(space_id=space_id, user_id=user_id)
        self.session.add(participant)
        await self.session.flush()
        return participant

    async def remove_participant(self, space_id: UUID, user_id: UUID) -> bool:
        participant = await self.session.get(DecisionSpaceParticipant, (space_id, user_id))
        if participant is None:
            return False
        await self.session.delete(participant)
        await self.session.flush()
        return True

    async def history(self, space_id: UUID) -> list[DecisionSpaceStatusEvent]:
        query = (
            select(DecisionSpaceStatusEvent)
            .where(DecisionSpaceStatusEvent.space_id == space_id)
            .order_by(DecisionSpaceStatusEvent.seq)
        )
        return list((await self.session.scalars(query)).all())

    async def append_status_event(
        self,
        space: DecisionSpace,
        *,
        to_status: str,
        actor_id: UUID,
        reason: str | None,
        lang: str,
    ) -> DecisionSpaceStatusEvent:
        event = DecisionSpaceStatusEvent(
            id=uuid4(),
            space_id=space.id,
            from_status=space.status,
            to_status=to_status,
            actor_id=actor_id,
            reason=reason,
        )
        self.session.add(event)
        space.status = to_status
        space.lang = lang
        await self.session.flush()
        await self.session.refresh(space)
        return event
