from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import Idea, IdeaMembership, User, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration


@dataclass(frozen=True)
class OwnedIdeaRow:
    id: UUID
    slug: str
    title: str
    stage: str
    lang: str
    created_at: datetime


@dataclass(frozen=True)
class MembershipRow:
    idea_id: UUID
    idea_title: str
    role: str


@dataclass(frozen=True)
class ContributionRow:
    idea_id: UUID
    idea_title: str
    message: str
    lang: str
    short_hash: str
    created_at: datetime


@dataclass(frozen=True)
class ProfileRecord:
    user: User
    owned_ideas: list[OwnedIdeaRow]
    memberships: list[MembershipRow]
    contributions: list[ContributionRow]


class PostgresProfiles:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def user(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def workspace_ids(self, user_id: UUID) -> frozenset[UUID]:
        query = select(WorkspaceMembership.workspace_id).where(
            WorkspaceMembership.user_id == user_id
        )
        return frozenset((await self.session.scalars(query)).all())

    async def workspace_ids_for_subject(self, subject: str) -> frozenset[UUID]:
        query = (
            select(WorkspaceMembership.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(User.auth_subject == subject)
        )
        return frozenset((await self.session.scalars(query)).all())

    async def owned_ideas(self, user_id: UUID, workspaces: frozenset[UUID]) -> list[OwnedIdeaRow]:
        if not workspaces:
            return []
        query = (
            select(Idea)
            .where(Idea.owner_id == user_id, Idea.workspace_id.in_(workspaces))
            .order_by(Idea.created_at.desc())
        )
        return [
            OwnedIdeaRow(
                id=idea.id,
                slug=idea.slug,
                title=idea.title,
                stage=idea.stage,
                lang=idea.lang,
                created_at=idea.created_at,
            )
            for idea in (await self.session.scalars(query)).all()
        ]

    async def memberships(self, user_id: UUID, workspaces: frozenset[UUID]) -> list[MembershipRow]:
        if not workspaces:
            return []
        query = (
            select(IdeaMembership.idea_id, Idea.title, IdeaMembership.business_function)
            .join(Idea, Idea.id == IdeaMembership.idea_id)
            .where(
                IdeaMembership.user_id == user_id,
                Idea.workspace_id.in_(workspaces),
            )
            .order_by(IdeaMembership.joined_at)
        )
        return [
            MembershipRow(idea_id=idea_id, idea_title=title, role=role)
            for idea_id, title, role in (await self.session.execute(query)).all()
        ]

    async def contributions(
        self, user_id: UUID, workspaces: frozenset[UUID], limit: int = 50
    ) -> list[ContributionRow]:
        if not workspaces:
            return []
        query = (
            select(
                Idea.id,
                Idea.title,
                Iteration.message,
                Iteration.lang,
                Iteration.short_hash,
                Iteration.created_at,
            )
            .join(Idea, Idea.id == Iteration.idea_id)
            .where(
                Iteration.author_id == user_id,
                Idea.workspace_id.in_(workspaces),
            )
            .order_by(Iteration.created_at.desc())
            .limit(limit)
        )
        return [
            ContributionRow(
                idea_id=idea_id,
                idea_title=idea_title,
                message=message,
                lang=lang,
                short_hash=short_hash,
                created_at=created_at,
            )
            for idea_id, idea_title, message, lang, short_hash, created_at in (
                await self.session.execute(query)
            ).all()
        ]
