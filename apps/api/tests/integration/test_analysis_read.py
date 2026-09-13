import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration, PostgresIterations
from src.modules.iterations.store import store_raw_analysis
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def analysis_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


def _seed_users(session, workspace_id, owner_id, member_id, outsider_id):
    session.add_all(
        [
            Workspace(id=workspace_id, name="Read workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=member_id, auth_subject=str(member_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=member_id, role="member"),
        ]
    )


def _seed_idea_with_branches(session, workspace_id, owner_id):
    idea_id, main_id, branch_id = (uuid4() for _ in range(3))
    session.add_all(
        [
            Idea(
                id=idea_id,
                slug=f"read-idea-{idea_id.hex[:8]}",
                title="Shared cargo bikes",
                pitch="A coop fleet",
                owner_id=owner_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
            Iteration(
                id=main_id,
                idea_id=idea_id,
                parent_id=None,
                author_id=owner_id,
                message="Initial deposit",
                lang="en",
                payload={"title": "Shared cargo bikes", "pitch": "A coop fleet", "stage": "seed"},
                branch="main",
                proposal_status=None,
                short_hash=main_id.hex[:12],
                revision=1,
            ),
            Iteration(
                id=branch_id,
                idea_id=idea_id,
                parent_id=main_id,
                author_id=owner_id,
                message="Proposal",
                lang="en",
                payload={"title": "Shared cargo bikes", "pitch": "A coop fleet", "stage": "seed"},
                branch="proposal-1",
                proposal_status="pending",
                short_hash=branch_id.hex[:12],
                revision=2,
            ),
        ]
    )
    return idea_id, main_id, branch_id


def _analysis_payload(**overrides):
    def dimension(score=70):
        return {"score": score, "note": "Evidence shows room."}

    payload = {
        "realism_score": 62,
        "concurrence": dimension(),
        "cout": dimension(),
        "temps": dimension(),
        "defendabilite": dimension(),
        "acquisition": dimension(),
        "locale": "en",
        "source_ids": ["evidence-1"],
        "established_facts": ["A coop fleet exists downtown."],
    }
    payload.update(overrides)
    return payload


async def test_read_serves_analysis_bound_to_iteration(analysis_database):
    engine, url = analysis_database
    workspace_id, owner_id, member_id, outsider_id = (uuid4() for _ in range(4))
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            _seed_users(session, workspace_id, owner_id, member_id, outsider_id)
            await session.flush()
            idea_id, main_id, branch_id = _seed_idea_with_branches(session, workspace_id, owner_id)
            await session.flush()
            await store_raw_analysis(
                PostgresIterations(session),
                idea_id,
                main_id,
                _analysis_payload(),
                model="test",
            )

            app = create_app(Settings(_env_file=None))
            app.dependency_overrides[current_identity] = lambda: Identity(str(member_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                read = await client.get(f"/ideas/{idea_id}")
                assert read.status_code == 200
                body = read.json()
                assert body["analysis"]["iteration_id"] == str(main_id)
                assert body["analysis"]["realism_score"] == 62
                assert body["analysis"]["constraints"]["concurrence"]["score"] == 70
                assert body["analysis"]["constraints"]["concurrence"]["note"]
                assert body["analysis"]["state"] == "resolved"

        await transaction.rollback()


async def test_read_shows_running_state_without_analysis(analysis_database):
    engine, url = analysis_database
    workspace_id, owner_id, member_id, outsider_id = (uuid4() for _ in range(4))
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            _seed_users(session, workspace_id, owner_id, member_id, outsider_id)
            await session.flush()
            idea_id, _, _ = _seed_idea_with_branches(session, workspace_id, owner_id)
            await session.flush()

            app = create_app(Settings(_env_file=None))
            app.dependency_overrides[current_identity] = lambda: Identity(str(member_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                read = await client.get(f"/ideas/{idea_id}")
                assert read.status_code == 200
                body = read.json()
                assert body["analysis"] is not None
                assert body["analysis"]["state"] == "running"

        await transaction.rollback()


async def test_read_proposal_shows_parent_analysis(analysis_database):
    engine, url = analysis_database
    workspace_id, owner_id, member_id, outsider_id = (uuid4() for _ in range(4))
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            _seed_users(session, workspace_id, owner_id, member_id, outsider_id)
            await session.flush()
            idea_id, main_id, _branch_id = _seed_idea_with_branches(session, workspace_id, owner_id)
            await session.flush()
            await store_raw_analysis(
                PostgresIterations(session), idea_id, main_id, _analysis_payload(), model="test"
            )

            app = create_app(Settings(_env_file=None))
            app.dependency_overrides[current_identity] = lambda: Identity(str(member_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                history = await client.get(f"/ideas/{idea_id}/iterations")
                assert history.status_code == 200
                proposal_view = next(
                    item for item in history.json() if item["proposal_status"] == "pending"
                )
                assert proposal_view["analysis"]["realism_score"] == 62

        await transaction.rollback()


async def test_read_abstention_shows_resolved_unknown(analysis_database):
    engine, url = analysis_database
    workspace_id, owner_id, member_id, outsider_id = (uuid4() for _ in range(4))
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            _seed_users(session, workspace_id, owner_id, member_id, outsider_id)
            await session.flush()
            idea_id, main_id, _ = _seed_idea_with_branches(session, workspace_id, owner_id)
            await session.flush()
            payload = _analysis_payload(realism_score=None, source_ids=[], established_facts=[])
            for dimension in (
                payload["concurrence"],
                payload["cout"],
                payload["temps"],
                payload["defendabilite"],
                payload["acquisition"],
            ):
                dimension["score"] = None
                dimension["note"] = "No evidence yet."
            await store_raw_analysis(
                PostgresIterations(session), idea_id, main_id, payload, model="test"
            )

            app = create_app(Settings(_env_file=None))
            app.dependency_overrides[current_identity] = lambda: Identity(str(member_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                read = await client.get(f"/ideas/{idea_id}", headers={"Accept-Language": "en"})
                assert read.status_code == 200
                analysis = read.json()["analysis"]
                assert analysis["state"] == "abstained"
                assert analysis["realism_score"] is None
                assert read.headers["Content-Language"] == "en"

        await transaction.rollback()
