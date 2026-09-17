from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy import (
    text as sa_text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.decision_spaces.adapters.postgres import DecisionSpace
from src.modules.ideas.adapters.postgres import Idea, User, WorkspaceMembership
from src.modules.options.adapters.postgres import Option
from src.platform.db import Base

STATUS_CHECK = "status IN ('proposed', 'running', 'completed', 'cancelled')"
LEARNING_STATUS_CHECK = "status IN ('draft', 'confirmed')"


class Experiment(Base):
    __tablename__ = "experiments"
    __table_args__ = (CheckConstraint(STATUS_CHECK),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    decision_space_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="SET NULL"), index=True
    )
    option_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("options.id", ondelete="SET NULL"), index=True
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(300))
    hypothesis: Mapped[str] = mapped_column(Text)
    success_metric: Mapped[str] = mapped_column(String(300))
    baseline: Mapped[str | None] = mapped_column(String(200))
    target: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(
        String(16), default="proposed", server_default=sa_text("'proposed'")
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExperimentOutcome(Base):
    __tablename__ = "experiment_outcomes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), index=True
    )
    recorded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    metric: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(50))
    observed_at: Mapped[date | None] = mapped_column(Date)
    comment: Mapped[str | None] = mapped_column(Text)
    qualitative: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Learning(Base):
    __tablename__ = "learnings"
    __table_args__ = (CheckConstraint(LEARNING_STATUS_CHECK), UniqueConstraint("experiment_id"))

    id: Mapped[UUID] = mapped_column(primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"))
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(
        String(16), default="draft", server_default=sa_text("'draft'")
    )
    text: Mapped[str] = mapped_column(Text)
    outcome_ids: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default=sa_text("'[]'::jsonb")
    )
    confirmed_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PostgresExperiments:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def accessible_idea(self, idea_id: UUID, subject: str) -> tuple[Idea, User] | None:
        query = (
            select(Idea, User)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Idea.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(Idea.id == idea_id, User.auth_subject == subject)
        )
        row = (await self.session.execute(query)).one_or_none()
        return (row[0], row[1]) if row is not None else None

    async def experiment_actor(
        self, experiment_id: UUID, subject: str
    ) -> tuple[Experiment, Idea, User] | None:
        query = (
            select(Experiment, Idea, User)
            .join(Idea, Idea.id == Experiment.idea_id)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Idea.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(Experiment.id == experiment_id, User.auth_subject == subject)
        )
        row = (await self.session.execute(query)).one_or_none()
        return (row[0], row[1], row[2]) if row is not None else None

    async def experiments_for_idea(self, idea_id: UUID) -> list[Experiment]:
        query = (
            select(Experiment)
            .where(Experiment.idea_id == idea_id)
            .order_by(Experiment.created_at, Experiment.id)
        )
        return list((await self.session.scalars(query)).all())

    async def space(self, space_id: UUID) -> DecisionSpace | None:
        return await self.session.get(DecisionSpace, space_id)

    async def option_in_space(self, space_id: UUID, option_id: UUID) -> Option | None:
        return await self.session.scalar(
            select(Option).where(Option.id == option_id, Option.space_id == space_id)
        )

    async def is_workspace_member(self, workspace_id: UUID, subject: str) -> bool:
        query = (
            select(WorkspaceMembership)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(
                WorkspaceMembership.workspace_id == workspace_id,
                User.auth_subject == subject,
            )
        )
        return await self.session.scalar(query) is not None

    async def experiments_for_space(self, space_id: UUID) -> list[Experiment]:
        query = (
            select(Experiment)
            .where(Experiment.decision_space_id == space_id)
            .order_by(Experiment.created_at, Experiment.id)
        )
        return list((await self.session.scalars(query)).all())

    async def learnings_for_space(self, space_id: UUID) -> list[Learning]:
        query = (
            select(Learning)
            .join(Experiment, Experiment.id == Learning.experiment_id)
            .where(Experiment.decision_space_id == space_id)
            .order_by(Learning.created_at, Learning.id)
        )
        return list((await self.session.scalars(query)).all())

    async def outcomes(self, experiment_id: UUID) -> list[ExperimentOutcome]:
        query = (
            select(ExperimentOutcome)
            .where(ExperimentOutcome.experiment_id == experiment_id)
            .order_by(ExperimentOutcome.created_at, ExperimentOutcome.id)
        )
        return list((await self.session.scalars(query)).all())

    async def learning(self, experiment_id: UUID) -> Learning | None:
        return await self.session.scalar(
            select(Learning).where(Learning.experiment_id == experiment_id)
        )

    async def learnings_for_idea(self, idea_id: UUID) -> list[Learning]:
        query = select(Learning).where(Learning.idea_id == idea_id).order_by(Learning.created_at)
        return list((await self.session.scalars(query)).all())

    async def create_experiment(self, **values: Any) -> Experiment:
        experiment = Experiment(id=uuid4(), **values)
        self.session.add(experiment)
        await self.session.flush()
        return experiment

    async def record_outcome(self, **values: Any) -> ExperimentOutcome:
        outcome = ExperimentOutcome(id=uuid4(), **values)
        self.session.add(outcome)
        await self.session.flush()
        return outcome

    async def save_learning(
        self, *, experiment: Experiment, text: str, status: str, confirmed_by_id: UUID | None
    ) -> Learning:
        learning = await self.learning(experiment.id)
        outcomes = await self.outcomes(experiment.id)
        outcome_ids = [str(outcome.id) for outcome in outcomes]
        if learning is None:
            learning = Learning(
                id=uuid4(),
                experiment_id=experiment.id,
                idea_id=experiment.idea_id,
                status=status,
                text=text,
                outcome_ids=outcome_ids,
                confirmed_by_id=confirmed_by_id,
            )
            self.session.add(learning)
        else:
            learning.text = text
            learning.status = status
            learning.outcome_ids = outcome_ids
            learning.confirmed_by_id = confirmed_by_id
        await self.session.flush()
        await self.session.refresh(learning)
        return learning

    async def apply_status(self, experiment: Experiment, status: str, now: datetime) -> Experiment:
        experiment.status = status
        if status == "running":
            experiment.started_at = now
        if status in {"completed", "cancelled"}:
            experiment.ended_at = now
        await self.session.flush()
        return experiment

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)
