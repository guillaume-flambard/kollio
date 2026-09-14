import os
import re
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def deposit_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def _seed_client(engine, url, session, subject, workspace_id, member_id, outsider_id):
    session.add_all(
        [
            Workspace(id=workspace_id, name="Deposit workspace"),
            User(id=member_id, auth_subject=str(member_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=member_id, role="member"),
        ]
    )
    await session.flush()
    app = create_app(Settings(_env_file=None, database_url=url))
    app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_deposit_creates_private_idea_with_initial_iteration(deposit_database):
    engine, url = deposit_database
    workspace_id, member_id, outsider_id = (uuid4() for _ in range(3))
    subject = {"value": str(member_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            client = await _seed_client(
                engine, url, session, subject, workspace_id, member_id, outsider_id
            )
            async with client:
                deposited = await client.post(
                    f"/workspaces/{workspace_id}/ideas",
                    json={"title": "Shared cargo bikes", "pitch": "A coop fleet", "lang": "en"},
                    headers={"Accept-Language": "en"},
                )
                assert deposited.status_code == 201
                body = deposited.json()
                assert body["workspace_id"] == str(workspace_id)
                assert body["stage"] == "seed"
                assert body["visibility"] == "workspace"
                assert body["lang"] == "en"
                assert body["owner_id"] == str(member_id)
                assert re.fullmatch(r"[a-z0-9-]+-[0-9a-f]{8}", body["slug"])
                assert body["slug"].startswith("shared-cargo-bikes-")
                idea_id = body["id"]

                stored_idea = await session.get(Idea, idea_id)
                assert stored_idea is not None
                assert stored_idea.owner_id == member_id
                iterations = list(
                    (
                        await session.scalars(
                            select(Iteration)
                            .where(Iteration.idea_id == stored_idea.id)
                            .order_by(Iteration.revision)
                        )
                    ).all()
                )
                assert len(iterations) == 1
                initial = iterations[0]
                assert initial.parent_id is None
                assert initial.branch == "main"
                assert initial.revision == 1
                assert initial.author_id == member_id
                assert initial.message == "Initial deposit"

        await transaction.rollback()


async def test_deposit_defaults_to_request_locale(deposit_database):
    engine, url = deposit_database
    workspace_id, member_id, outsider_id = (uuid4() for _ in range(3))
    subject = {"value": str(member_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            client = await _seed_client(
                engine, url, session, subject, workspace_id, member_id, outsider_id
            )
            async with client:
                deposited = await client.post(
                    f"/workspaces/{workspace_id}/ideas",
                    json={"title": "Vélos cargo partagés", "pitch": "Une flotte coopérative"},
                    headers={"Accept-Language": "fr"},
                )
                assert deposited.status_code == 201
                assert deposited.json()["lang"] == "fr"
                assert deposited.headers["Content-Language"] == "fr"

        await transaction.rollback()


async def test_deposit_rejects_outsiders_and_invalid_payloads(deposit_database):
    engine, url = deposit_database
    workspace_id, member_id, outsider_id = (uuid4() for _ in range(3))
    subject = {"value": str(outsider_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            client = await _seed_client(
                engine, url, session, subject, workspace_id, member_id, outsider_id
            )
            async with client:
                denied = await client.post(
                    f"/workspaces/{workspace_id}/ideas",
                    json={"title": "Sneaky", "pitch": "No access", "lang": "en"},
                )
                assert denied.status_code == 404

                subject["value"] = str(member_id)
                invalid = await client.post(
                    f"/workspaces/{workspace_id}/ideas",
                    json={"title": "", "pitch": "Missing title", "lang": "en"},
                    headers={"Accept-Language": "fr"},
                )
                assert invalid.status_code == 422
                assert invalid.json() == {"detail": "Requête invalide"}

        await transaction.rollback()
