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
