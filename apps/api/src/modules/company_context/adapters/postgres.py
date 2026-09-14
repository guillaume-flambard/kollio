from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    false,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.platform.db import Base

STATE_CHECK = "state IN ('active', 'archived')"
LANG_CHECK = "lang IN ('fr', 'en')"


class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    __table_args__ = (CheckConstraint(LANG_CHECK),)

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    business_model: Mapped[str | None] = mapped_column(Text)
    products_services: Mapped[str | None] = mapped_column(Text)
    customer_segments: Mapped[str | None] = mapped_column(Text)
    markets: Mapped[str | None] = mapped_column(Text)
    structure: Mapped[str | None] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CompanyObjective(Base):
    __tablename__ = "company_objectives"
    __table_args__ = (CheckConstraint(STATE_CHECK), CheckConstraint(LANG_CHECK))

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    state: Mapped[str] = mapped_column(String(16), default="active")
    priority: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CompanyConstraint(Base):
    __tablename__ = "company_constraints"
    __table_args__ = (CheckConstraint(STATE_CHECK), CheckConstraint(LANG_CHECK))

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    detail: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(16), default="active")
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PostgresCompanyContext:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def memberships(self, subject: str) -> frozenset[UUID]:
        query = (
            select(WorkspaceMembership.workspace_id).join(User).where(User.auth_subject == subject)
        )
        return frozenset((await self.session.scalars(query)).all())

    async def profile(self, workspace_id: UUID) -> CompanyProfile | None:
        return await self.session.get(CompanyProfile, workspace_id)

    async def objectives(self, workspace_id: UUID) -> list[CompanyObjective]:
        query = (
            select(CompanyObjective)
            .where(CompanyObjective.workspace_id == workspace_id)
            .order_by(CompanyObjective.created_at, CompanyObjective.id)
        )
        return list((await self.session.scalars(query)).all())

    async def constraints(self, workspace_id: UUID) -> list[CompanyConstraint]:
        query = (
            select(CompanyConstraint)
            .where(CompanyConstraint.workspace_id == workspace_id)
            .order_by(CompanyConstraint.created_at, CompanyConstraint.id)
        )
        return list((await self.session.scalars(query)).all())

    async def upsert_profile(
        self, workspace_id: UUID, values: dict[str, Any], lang: str
    ) -> CompanyProfile:
        profile = await self.profile(workspace_id)
        if profile is None:
            profile = CompanyProfile(workspace_id=workspace_id, lang=lang, **values)
            self.session.add(profile)
        else:
            for key, value in values.items():
                setattr(profile, key, value)
            profile.lang = lang
        await self.session.flush()
        return profile

    async def create_objective(self, workspace_id: UUID, title: str, lang: str) -> CompanyObjective:
        objective = CompanyObjective(
            id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            state="active",
            priority=False,
            lang=lang,
        )
        self.session.add(objective)
        await self.session.flush()
        return objective

    async def objective(self, workspace_id: UUID, objective_id: UUID) -> CompanyObjective | None:
        return await self.session.scalar(
            select(CompanyObjective).where(
                CompanyObjective.id == objective_id,
                CompanyObjective.workspace_id == workspace_id,
            )
        )

    async def create_constraint(
        self, workspace_id: UUID, title: str, detail: str | None, lang: str
    ) -> CompanyConstraint:
        constraint = CompanyConstraint(
            id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            detail=detail,
            state="active",
            lang=lang,
        )
        self.session.add(constraint)
        await self.session.flush()
        return constraint

    async def update_objective(
        self, workspace_id: UUID, objective_id: UUID, changes: dict[str, Any], lang: str
    ) -> CompanyObjective | None:
        objective = await self.objective(workspace_id, objective_id)
        if objective is None:
            return None
        for key, value in changes.items():
            setattr(objective, key, value)
        objective.lang = lang
        await self.session.flush()
        return objective

    async def constraint(self, workspace_id: UUID, constraint_id: UUID) -> CompanyConstraint | None:
        return await self.session.scalar(
            select(CompanyConstraint).where(
                CompanyConstraint.id == constraint_id,
                CompanyConstraint.workspace_id == workspace_id,
            )
        )

    async def update_constraint(
        self, workspace_id: UUID, constraint_id: UUID, changes: dict[str, Any], lang: str
    ) -> CompanyConstraint | None:
        constraint = await self.constraint(workspace_id, constraint_id)
        if constraint is None:
            return None
        for key, value in changes.items():
            setattr(constraint, key, value)
        constraint.lang = lang
        await self.session.flush()
        return constraint
