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
async def idea_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def _seed(session):
    workspace_id, owner_id, colleague_id, outsider_id = (uuid4() for _ in range(4))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Initiative workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=colleague_id, auth_subject=str(colleague_id), display_name="Colleague"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=colleague_id, role="member"),
        ]
    )
    await session.flush()
    return workspace_id, owner_id, colleague_id, outsider_id


def _client(session, url, subject: str):
    app = create_app(Settings(_env_file=None, database_url=url))
    app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def _deposit(client, workspace_id, **overrides):
    body = {"title": "Pricing experiment", "pitch": "Test a usage-based tier", "lang": "en"}
    body.update(overrides)
    return await client.post(f"/workspaces/{workspace_id}/ideas", json=body)


async def test_deposit_defaults_to_the_idea_type(idea_database):
    engine, url = idea_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, _, _ = await _seed(session)
            async with _client(session, url, str(owner_id)) as client:
                created = await _deposit(client, workspace_id)
                assert created.status_code == 201
                assert created.json()["initiative_type"] == "idea"
        await transaction.rollback()


async def test_deposit_stores_the_chosen_type_and_exposes_it(idea_database):
    engine, url = idea_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, _, _ = await _seed(session)
            async with _client(session, url, str(owner_id)) as client:
                created = await _deposit(client, workspace_id, initiative_type="campaign")
                assert created.status_code == 201
                idea_id = created.json()["id"]
                assert created.json()["initiative_type"] == "campaign"

                read = await client.get(f"/ideas/{idea_id}")
                assert read.json()["initiative_type"] == "campaign"

                listed = await client.get(f"/workspaces/{workspace_id}/ideas")
                items = listed.json()["items"]
                assert [item["initiative_type"] for item in items] == ["campaign"]
        await transaction.rollback()


async def test_deposit_refuses_an_unknown_type(idea_database):
    engine, url = idea_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, _, _ = await _seed(session)
            async with _client(session, url, str(owner_id)) as client:
                refused = await _deposit(client, workspace_id, initiative_type="startup")
                assert refused.status_code == 422
        await transaction.rollback()


async def test_owner_changes_the_type(idea_database):
    engine, url = idea_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, _, _ = await _seed(session)
            async with _client(session, url, str(owner_id)) as client:
                idea_id = (await _deposit(client, workspace_id)).json()["id"]
                updated = await client.patch(
                    f"/ideas/{idea_id}", json={"initiative_type": "pricing"}
                )
                assert updated.status_code == 200
                assert updated.json()["initiative_type"] == "pricing"

                unknown = await client.patch(f"/ideas/{idea_id}", json={"initiative_type": "hunch"})
                assert unknown.status_code == 422
        await transaction.rollback()


async def test_only_the_owner_changes_the_type(idea_database):
    engine, url = idea_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, colleague_id, outsider_id = await _seed(session)
            async with _client(session, url, str(owner_id)) as client:
                idea_id = (await _deposit(client, workspace_id)).json()["id"]

            async with _client(session, url, str(colleague_id)) as client:
                forbidden = await client.patch(
                    f"/ideas/{idea_id}", json={"initiative_type": "market"}
                )
                assert forbidden.status_code == 403

            async with _client(session, url, str(outsider_id)) as client:
                hidden = await client.patch(f"/ideas/{idea_id}", json={"initiative_type": "market"})
                assert hidden.status_code == 404
        await transaction.rollback()
