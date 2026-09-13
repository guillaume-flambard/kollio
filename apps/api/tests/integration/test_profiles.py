import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def profile_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def _seed(session):
    workspace_id, other_workspace_id, person_id, viewer_id, outsider_id, idea_id = (
        uuid4() for _ in range(6)
    )
    other_idea_id, iteration_id = uuid4(), uuid4()
    session.add_all(
        [
            Workspace(id=workspace_id, name="Profile workspace"),
            Workspace(id=other_workspace_id, name="Elsewhere"),
            User(
                id=person_id,
                auth_subject=str(person_id),
                display_name="Ada",
                handle="ada",
                roles=["dev", "data"],
                bio="Ships things.",
            ),
            User(id=viewer_id, auth_subject=str(viewer_id), display_name="Viewer"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=person_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=viewer_id, role="member"),
            WorkspaceMembership(workspace_id=other_workspace_id, user_id=outsider_id, role="admin"),
        ]
    )
    await session.flush()
    session.add_all(
        [
            Idea(
                id=idea_id,
                slug=f"owned-{idea_id.hex[:8]}",
                title="Cargo bikes coop",
                pitch="A shared fleet",
                owner_id=person_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
            Idea(
                id=other_idea_id,
                slug=f"secret-{other_idea_id.hex[:8]}",
                title="Hidden elsewhere",
                pitch="Another workspace",
                owner_id=person_id,
                workspace_id=other_workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
            Iteration(
                id=iteration_id,
                idea_id=idea_id,
                parent_id=None,
                author_id=person_id,
                message="Initial deposit",
                lang="en",
                payload={"title": "Cargo bikes coop", "pitch": "A shared fleet", "stage": "seed"},
                branch="main",
                proposal_status=None,
                short_hash=iteration_id.hex[:12],
                revision=1,
            ),
        ]
    )
    await session.flush()
    from src.modules.ideas.adapters.postgres import IdeaMembership

    session.add(
        IdeaMembership(
            idea_id=other_idea_id, user_id=person_id, role="growth"
        )  # membership on the other workspace
    )
    await session.flush()
    return {
        "workspace_id": workspace_id,
        "other_workspace_id": other_workspace_id,
        "person_id": person_id,
        "viewer_id": viewer_id,
        "outsider_id": outsider_id,
        "idea_id": idea_id,
        "other_idea_id": other_idea_id,
    }


def _client(session, app, subject):
    app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_member_sees_scoped_profile(profile_database):
    engine, url = profile_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            ids = await _seed(session)
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, str(ids["viewer_id"])) as client:
                read = await client.get(f"/users/{ids['person_id']}")
                assert read.status_code == 200
                body = read.json()
                assert body["display_name"] == "Ada"
                assert body["handle"] == "ada"
                assert sorted(body["roles"]) == ["data", "dev"]
                assert body["bio"] == "Ships things."
                assert [item["id"] for item in body["owned_ideas"]] == [str(ids["idea_id"])]
                assert body["memberships"] == []
                assert [item["message"] for item in body["contributions"]] == ["Initial deposit"]
                assert body["contributions"][0]["idea_id"] == str(ids["idea_id"])
        await transaction.rollback()


async def test_own_profile_uses_the_same_rule(profile_database):
    engine, url = profile_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            ids = await _seed(session)
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, str(ids["person_id"])) as client:
                read = await client.get(f"/users/{ids['person_id']}")
                assert read.status_code == 200
                assert [item["id"] for item in read.json()["owned_ideas"]] == [str(ids["idea_id"])]
        await transaction.rollback()


async def test_member_sees_membership_only_in_shared_workspaces(profile_database):
    engine, url = profile_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            ids = await _seed(session)
            from src.modules.ideas.adapters.postgres import IdeaMembership

            session.add(
                IdeaMembership(idea_id=ids["idea_id"], user_id=ids["person_id"], role="dev")
            )
            await session.flush()
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, str(ids["viewer_id"])) as client:
                read = await client.get(f"/users/{ids['person_id']}")
                assert read.status_code == 200
                assert read.json()["memberships"] == [
                    {
                        "idea_id": str(ids["idea_id"]),
                        "idea_title": "Cargo bikes coop",
                        "role": "dev",
                    }
                ]
        await transaction.rollback()


async def test_outsider_gets_localized_not_found(profile_database):
    engine, url = profile_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            ids = await _seed(session)
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, str(ids["outsider_id"])) as client:
                denied = await client.get(
                    f"/users/{ids['person_id']}", headers={"Accept-Language": "fr"}
                )
                assert denied.status_code == 404
                assert "introuvable" in denied.json()["detail"]
        await transaction.rollback()
