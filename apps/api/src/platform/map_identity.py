"""Map one Logto subject to the imported private workspace."""

import argparse
import asyncio
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.platform.config import get_settings
from src.platform.import_legacy import WORKSPACE_ID


async def map_identity_in_session(
    session: AsyncSession,
    subject: str,
    display_name: str,
    workspace_id: UUID = WORKSPACE_ID,
) -> UUID:
    if not subject.strip():
        raise ValueError("Logto subject must not be empty")

    if await session.get(Workspace, workspace_id) is None:
        raise ValueError("Target workspace does not exist")
    user_id = await session.scalar(select(User.id).where(User.auth_subject == subject))
    if user_id is None:
        user_id = uuid4()
        session.add(User(id=user_id, auth_subject=subject, display_name=display_name))
        await session.flush()
    await session.execute(
        insert(WorkspaceMembership)
        .values(workspace_id=workspace_id, user_id=user_id, role="admin")
        .on_conflict_do_update(
            index_elements=[
                WorkspaceMembership.workspace_id,
                WorkspaceMembership.user_id,
            ],
            set_={"role": "admin"},
        )
    )
    return user_id


async def map_identity(subject: str, display_name: str, workspace_id: UUID = WORKSPACE_ID) -> UUID:
    if not subject.strip():
        raise ValueError("Logto subject must not be empty")

    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as session:
            return await map_identity_in_session(session, subject, display_name, workspace_id)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("subject")
    parser.add_argument("--display-name", default="Kollio owner")
    arguments = parser.parse_args()
    mapped_user_id = asyncio.run(map_identity(arguments.subject, arguments.display_name))
    print(f"Mapped identity to user {mapped_user_id}")
