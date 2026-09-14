from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    false,
    func,
    or_,
    select,
    text,
)
from sqlalchemy import (
    true as sa_true,
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
    sought_roles: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )


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


class JoinRequest(Base):
    __tablename__ = "idea_join_requests"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'accepted', 'rejected')"),
        CheckConstraint("role <> 'owner'"),
        UniqueConstraint("idea_id", "requester_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    requester_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    rationale: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Departure(Base):
    __tablename__ = "idea_departures"
    __table_args__ = (CheckConstraint("direction IN ('left', 'removed')"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    direction: Mapped[str] = mapped_column(String(10))
    reason: Mapped[str | None] = mapped_column(String(500))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


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

    async def user_by_subject(self, subject: str) -> User | None:
        return await self.session.scalar(select(User).where(User.auth_subject == subject))

    async def pending_join_request(self, idea_id: UUID, requester_id: UUID) -> JoinRequest | None:
        return await self.session.scalar(
            select(JoinRequest).where(
                JoinRequest.idea_id == idea_id,
                JoinRequest.requester_id == requester_id,
                JoinRequest.status == "pending",
            )
        )

    async def join_requests_for_idea(self, idea_id: UUID) -> list[JoinRequest]:
        query = (
            select(JoinRequest)
            .where(JoinRequest.idea_id == idea_id)
            .order_by(JoinRequest.created_at)
        )
        return list((await self.session.scalars(query)).all())

    async def join_request(self, idea_id: UUID, request_id: UUID) -> JoinRequest | None:
        return await self.session.scalar(
            select(JoinRequest).where(JoinRequest.id == request_id, JoinRequest.idea_id == idea_id)
        )

    async def membership(self, idea_id: UUID, user_id: UUID) -> IdeaMembership | None:
        return await self.session.get(IdeaMembership, (idea_id, user_id))

    def commit_team_state(self, join_request: JoinRequest) -> None:
        self.session.add(join_request)

    async def record_departure(
        self, idea_id: UUID, user_id: UUID, direction: str, reason: str | None
    ) -> Departure:
        departure = Departure(
            id=uuid4(), idea_id=idea_id, user_id=user_id, direction=direction, reason=reason
        )
        self.session.add(departure)
        await self.session.flush()
        return departure

    async def add_idea_membership(self, idea_id: UUID, user_id: UUID, role: str) -> IdeaMembership:
        membership = IdeaMembership(idea_id=idea_id, user_id=user_id, role=role)
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def remove_membership(self, idea_id: UUID, user_id: UUID) -> None:
        membership = await self.membership(idea_id, user_id)
        if membership is not None:
            await self.session.delete(membership)
            await self.session.flush()

    def add_idea(self, idea: Idea) -> None:
        self.session.add(idea)

    async def collaborators(self, idea_id: UUID) -> list[tuple[User, str]]:
        query = (
            select(User, IdeaMembership.role)
            .join(IdeaMembership, IdeaMembership.user_id == User.id)
            .where(IdeaMembership.idea_id == idea_id)
            .order_by(IdeaMembership.joined_at, User.display_name)
        )
        return [(user, role) for user, role in (await self.session.execute(query)).all()]

    async def collaborators_for_ideas(
        self, idea_ids: list[UUID]
    ) -> dict[UUID, list[tuple[User, str]]]:
        if not idea_ids:
            return {}
        query = (
            select(IdeaMembership.idea_id, User, IdeaMembership.role)
            .join(User, User.id == IdeaMembership.user_id)
            .where(IdeaMembership.idea_id.in_(idea_ids))
            .order_by(IdeaMembership.idea_id, IdeaMembership.joined_at, User.display_name)
        )
        collaborators: dict[UUID, list[tuple[User, str]]] = {}
        for idea_id, user, role in (await self.session.execute(query)).all():
            collaborators.setdefault(idea_id, []).append((user, role))
        return collaborators

    async def list_for_workspace(
        self,
        workspace_id: UUID,
        limit: int,
        offset: int,
        query_text: str | None = None,
        stage: str | None = None,
        sought_role: str | None = None,
        realism_min: int | None = None,
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
        if sought_role:
            filters.append(Idea.sought_roles.contains([sought_role]))
        activity, _analysis, head = self._activity_binding()
        if realism_min is not None:
            filters.append(_analysis >= realism_min)
        query = (
            select(
                Idea,
                _analysis.label("realism_score"),
                activity.label("last_activity_at"),
            )
            .outerjoin(head, sa_true())
            .where(*filters)
            .order_by(activity.desc().nulls_last(), Idea.created_at.desc(), Idea.id.desc())
            .limit(limit)
            .offset(offset)
        )
        count_query = select(func.count()).select_from(Idea).where(*filters)
        total = int((await self.session.scalar(count_query)) or 0)
        ideas: list[Idea] = []
        realism_scores: dict[UUID, int | None] = {}
        last_activity: dict[UUID, datetime | None] = {}
        for row in (await self.session.execute(query)).all():
            idea = row[0]
            realism_scores[idea.id] = row[1]
            last_activity[idea.id] = row[2]
            ideas.append(idea)
        return ideas, total, realism_scores, last_activity

    def _activity_binding(self) -> tuple[Any, Any, Any]:
        from src.modules.constraint_analysis.adapters.postgres import (
            ConstraintAnalysis as StoredAnalysis,
        )
        from src.modules.iterations.adapters.postgres import Iteration

        head = (
            select(Iteration)
            .where(Iteration.idea_id == Idea.id, Iteration.branch == "main")
            .order_by(Iteration.revision.desc())
            .limit(1)
            .subquery()
            .lateral()
        )
        analysis = (
            select(StoredAnalysis.result["overall_score"].astext.cast(Integer))
            .where(StoredAnalysis.idea_id == Idea.id)
            .order_by(StoredAnalysis.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        return head.c.created_at, analysis, head
