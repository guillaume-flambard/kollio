from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ideas.adapters.postgres import Idea, User, WorkspaceMembership
from src.platform.db import Base


class Iteration(Base):
    __tablename__ = "iterations"
    __table_args__ = (
        CheckConstraint("lang IN ('fr', 'en')"),
        CheckConstraint(
            "proposal_status IS NULL OR proposal_status IN ('pending', 'accepted', 'rejected')"
        ),
        CheckConstraint(
            "(branch = 'main' AND proposal_status IS NULL) OR "
            "(branch <> 'main' AND proposal_status IS NOT NULL)"
        ),
        CheckConstraint("revision > 0"),
        UniqueConstraint("idea_id", "short_hash"),
        UniqueConstraint("idea_id", "revision"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("iterations.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str]
    lang: Mapped[str] = mapped_column(String(2))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    branch: Mapped[str] = mapped_column(String(64), default="main")
    proposal_status: Mapped[str | None] = mapped_column(String(16))
    short_hash: Mapped[str] = mapped_column(String(12))
    revision: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IdeaAnalysis(Base):
    __tablename__ = "constraint_analyses"
    __table_args__ = (
        CheckConstraint("locale IN ('fr', 'en')"),
        CheckConstraint("realism_score IS NULL OR (realism_score BETWEEN 0 AND 100)"),
        UniqueConstraint("iteration_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    iteration_id: Mapped[UUID] = mapped_column(ForeignKey("iterations.id", ondelete="CASCADE"))
    realism_score: Mapped[int | None] = mapped_column(Integer)
    constraints: Mapped[dict[str, Any]] = mapped_column(JSONB)
    locale: Mapped[str] = mapped_column(String(2))
    model: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresIterations:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def accessible_idea(
        self, idea_id: UUID, subject: str, *, lock: bool = False
    ) -> tuple[Idea, User] | None:
        query = (
            select(Idea, User)
            .join(
                WorkspaceMembership,
                WorkspaceMembership.workspace_id == Idea.workspace_id,
            )
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(Idea.id == idea_id, User.auth_subject == subject)
        )
        if lock:
            query = query.with_for_update(of=Idea)
        return (await self.session.execute(query)).one_or_none()

    async def history(self, idea_id: UUID) -> list[Iteration]:
        query = (
            select(Iteration)
            .where(Iteration.idea_id == idea_id)
            .order_by(Iteration.revision.desc())
        )
        return list((await self.session.scalars(query)).all())

    async def get(self, idea_id: UUID, iteration_id: UUID) -> Iteration | None:
        return await self.session.scalar(
            select(Iteration).where(
                Iteration.id == iteration_id,
                Iteration.idea_id == idea_id,
            )
        )

    async def head(self, idea_id: UUID, branch: str) -> Iteration | None:
        return await self.session.scalar(
            select(Iteration)
            .where(Iteration.idea_id == idea_id, Iteration.branch == branch)
            .order_by(Iteration.revision.desc())
            .limit(1)
        )

    async def next_revision(self, idea_id: UUID) -> int:
        current = await self.session.scalar(
            select(func.max(Iteration.revision)).where(Iteration.idea_id == idea_id)
        )
        return int(current or 0) + 1

    async def analysis_for_iteration(self, iteration_id: UUID) -> IdeaAnalysis | None:
        return await self.session.scalar(
            select(IdeaAnalysis).where(IdeaAnalysis.iteration_id == iteration_id)
        )

    async def append(self, iteration: Iteration, idea: Idea, *, project: bool) -> Iteration:
        self.session.add(iteration)
        if project:
            idea.title = str(iteration.payload["title"])
            idea.pitch = str(iteration.payload["pitch"])
            idea.stage = str(iteration.payload["stage"])
        await self.session.flush()
        return iteration

    async def resolve_branch(self, idea_id: UUID, branch: str, status: str) -> None:
        await self.session.execute(
            update(Iteration)
            .where(
                Iteration.idea_id == idea_id,
                Iteration.branch == branch,
                Iteration.proposal_status == "pending",
            )
            .values(proposal_status=status)
        )
        await self.session.flush()
