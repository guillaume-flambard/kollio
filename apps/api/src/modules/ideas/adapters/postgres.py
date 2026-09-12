from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    false,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.platform.db import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    auth_subject: Mapped[str | None] = mapped_column(unique=True)
    display_name: Mapped[str]
    handle: Mapped[str | None] = mapped_column(unique=True)
    roles: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    bio: Mapped[str | None]
    avatar_key: Mapped[str | None]
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())


class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"
    __table_args__ = (CheckConstraint("role IN ('admin', 'member')"),)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(default="member")


class Idea(Base):
    __tablename__ = "ideas"
    __table_args__ = (
        CheckConstraint("lang IN ('fr', 'en')"),
        CheckConstraint("stage IN ('seed', 'iterating', 'team_formed')"),
        CheckConstraint(
            "(visibility = 'workspace' AND workspace_id IS NOT NULL) OR "
            "(visibility = 'public' AND workspace_id IS NULL)"
        ),
        UniqueConstraint("source", "source_id"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True)
    title: Mapped[str]
    pitch: Mapped[str]
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    workspace_id: Mapped[UUID | None] = mapped_column(ForeignKey("workspaces.id"), index=True)
    stage: Mapped[str] = mapped_column(default="seed")
    lang: Mapped[str]
    visibility: Mapped[str] = mapped_column(default="workspace")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str | None]
    source_id: Mapped[str | None]
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class IdeaMembership(Base):
    __tablename__ = "idea_memberships"
    idea_id: Mapped[UUID] = mapped_column(
        ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str]
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresIdeas:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, idea_id: UUID) -> Idea | None:
        return await self.session.get(Idea, idea_id)

    async def memberships(self, subject: str) -> frozenset[UUID]:
        query = (
            select(WorkspaceMembership.workspace_id).join(User).where(User.auth_subject == subject)
        )
        return frozenset((await self.session.scalars(query)).all())

    async def collaborators(self, idea_id: UUID) -> list[tuple[User, str]]:
        query = (
            select(User, IdeaMembership.role)
            .join(IdeaMembership, IdeaMembership.user_id == User.id)
            .where(IdeaMembership.idea_id == idea_id)
            .order_by(IdeaMembership.joined_at, User.display_name)
        )
        return [(user, role) for user, role in (await self.session.execute(query)).all()]

    async def list_for_workspace(
        self,
        workspace_id: UUID,
        limit: int,
        offset: int,
        query_text: str | None = None,
        stage: str | None = None,
        domain: str | None = None,
    ) -> tuple[list[Idea], int]:
        filters: list[Any] = [
            Idea.workspace_id == workspace_id,
            Idea.visibility == "workspace",
        ]
        if query_text:
            pattern = f"%{query_text.strip()}%"
            filters.append(
                or_(
                    Idea.title.ilike(pattern),
                    Idea.pitch.ilike(pattern),
                    Idea.provenance["domaine"].astext.ilike(pattern),
                )
            )
        if stage:
            filters.append(Idea.stage == stage)
        if domain:
            filters.append(Idea.provenance["domaine"].astext == domain)
        query = (
            select(Idea)
            .where(*filters)
            .order_by(Idea.created_at.desc(), Idea.id.desc())
            .limit(limit)
            .offset(offset)
        )
        count_query = select(func.count()).select_from(Idea).where(*filters)
        ideas = list((await self.session.scalars(query)).all())
        total = int((await self.session.scalar(count_query)) or 0)
        return ideas, total
