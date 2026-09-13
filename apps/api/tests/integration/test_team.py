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
async def team_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def _seed(session: object, workspace_id, owner_id, member_id, outsider_id, idea_id):
    session.add_all(
        [
            Workspace(id=workspace_id, name="Team workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=member_id, auth_subject=str(member_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=member_id, role="member"),
        ]
    )
    await session.flush()
    session.add_all(
        [
            Idea(
                id=idea_id,
                slug=f"team-idea-{idea_id.hex[:8]}",
                title="Shared cargo bikes",
                pitch="A coop fleet",
                owner_id=owner_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
            Iteration(
                id=uuid4(),
                idea_id=idea_id,
                parent_id=None,
                author_id=owner_id,
                message="Initial deposit",
                lang="en",
                payload={"title": "Shared cargo bikes", "pitch": "A coop fleet", "stage": "seed"},
                branch="main",
                proposal_status=None,
                short_hash=uuid4().hex[:12],
                revision=1,
            ),
        ]
    )
    await session.flush()


async def test_join_handshake_full_loop(team_database):
    engine, url = team_database
    workspace_id, owner_id, member_id, outsider_id, idea_id = (uuid4() for _ in range(5))
    subject = {"value": str(member_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            await _seed(session, workspace_id, owner_id, member_id, outsider_id, idea_id)
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                applied = await client.post(
                    f"/ideas/{idea_id}/join-requests",
                    json={"role": "dev", "note": "Ten years of frontend."},
                )
                assert applied.status_code == 201
                request_id = applied.json()["id"]

                subject["value"] = str(owner_id)
                accepted = await client.post(f"/ideas/{idea_id}/join-requests/{request_id}/accept")
                assert accepted.status_code in (201, 200)

                subject["value"] = str(member_id)
                read = await client.get(f"/ideas/{idea_id}")
                team = read.json()["collaborators"]
                assert any(
                    member["id"] == str(member_id) and member["role"] == "dev" for member in team
                )

                left = await client.post(
                    f"/ideas/{idea_id}/leave",
                    headers={"Accept-Language": "en"},
                )
                assert left.status_code == 200
                assert left.json()["recorded"] is True

                read_after = await client.get(f"/ideas/{idea_id}")
                assert not any(
                    member["id"] == str(member_id) for member in read_after.json()["collaborators"]
                )

                read_before = read.json()
                assert "sought_roles" in read_before

        await transaction.rollback()


async def test_join_reject_with_rationale_and_departure_record(team_database):
    engine, url = team_database
    workspace_id, owner_id, member_id, outsider_id, idea_id = (uuid4() for _ in range(5))
    subject = {"value": str(member_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            await _seed(session, workspace_id, owner_id, member_id, outsider_id, idea_id)
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                applied = await client.post(
                    f"/ideas/{idea_id}/join-requests",
                    json={"role": "growth", "note": "I ran campaigns."},
                )
                assert applied.status_code == 201
                request_id = applied.json()["id"]

                subject["value"] = str(owner_id)
                rejected = await client.post(
                    f"/ideas/{idea_id}/join-requests/{request_id}/reject",
                    json={"rationale": "Team full on growth."},
                    headers={"Accept-Language": "en"},
                )
                assert rejected.status_code == 200
                assert rejected.json()["status"] == "rejected"
                assert rejected.json()["rationale"] == "Team full on growth."

        await transaction.rollback()
