from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership


@dataclass(frozen=True)
class WorkspaceRecord:
    id: UUID
    name: str
    role: str


@dataclass(frozen=True)
class WorkspaceMemberRecord:
    id: UUID
    display_name: str
    role: str


class PostgresWorkspaces:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def for_subject(self, subject: str) -> list[WorkspaceRecord]:
        query = (
            select(Workspace.id, Workspace.name, WorkspaceMembership.role)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(User.auth_subject == subject)
            .order_by(Workspace.name, Workspace.id)
        )
        rows = (await self.session.execute(query)).all()
        return [WorkspaceRecord(id=row.id, name=row.name, role=row.role) for row in rows]

    async def members(self, workspace_id: UUID, subject: str) -> list[WorkspaceMemberRecord] | None:
        """The workspace's members, or None when the viewer is not one of them."""
        viewer = await self.session.scalar(
            select(WorkspaceMembership.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(
                WorkspaceMembership.workspace_id == workspace_id,
                User.auth_subject == subject,
            )
        )
        if viewer is None:
            return None
        query = (
            select(User.id, User.display_name, WorkspaceMembership.role)
            .join(WorkspaceMembership, WorkspaceMembership.user_id == User.id)
            .where(WorkspaceMembership.workspace_id == workspace_id)
            .order_by(User.display_name, User.id)
        )
        rows = (await self.session.execute(query)).all()
        return [
            WorkspaceMemberRecord(id=row.id, display_name=row.display_name, role=row.role)
            for row in rows
        ]
