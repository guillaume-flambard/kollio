import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def members_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def test_a_member_lists_the_workspace_members_and_an_outsider_does_not(members_database):
    engine, url = members_database
    workspace_id, owner_id, colleague_id, outsider_id = (uuid4() for _ in range(4))
    subject = {"value": str(owner_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Faktus"),
                    User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
                    User(id=colleague_id, auth_subject=str(colleague_id), display_name="Colleague"),
                    User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
                    WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
                    WorkspaceMembership(
                        workspace_id=workspace_id, user_id=colleague_id, role="member"
                    ),
                ]
            )
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                listed = await client.get(f"/workspaces/{workspace_id}/members")
                assert listed.status_code == 200
                assert [row["display_name"] for row in listed.json()] == ["Colleague", "Owner"]
                assert {row["role"] for row in listed.json()} == {"admin", "member"}

                subject["value"] = str(outsider_id)
                denied = await client.get(f"/workspaces/{workspace_id}/members")
                assert denied.status_code == 404
                assert denied.json()["detail"]["code"] == "workspace_not_found"

        await transaction.rollback()
