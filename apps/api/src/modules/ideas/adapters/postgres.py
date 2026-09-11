from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func, select
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
