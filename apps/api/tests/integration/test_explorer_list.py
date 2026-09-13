import os
from datetime import UTC, datetime, timedelta
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
async def explorer_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


def _dimension(score=70):
    return {"score": score, "note": "Evidence shows room."}


def _analysis_payload(realism_score=72):
    return {
        "realism_score": realism_score,
        "concurrence": {"score": 70, "note": "Evidence shows room."},
        "cout": {"score": 60, "note": "The build cost is shared."},
        "temps": {"score": 55, "note": "Time to market is short."},
        "defendabilite": {"score": 50, "note": "Defensible through the coop."},
        "acquisition": {"score": 65, "note": "Crews ask around."},
        "locale": "en",
        "source_ids": ["evidence-1"],
        "established_facts": ["A coop fleet exists downtown."],
    }


async def _seed(session, count=3):
    workspace_id, owner_id = uuid4(), uuid4()
    session.add_all(
        [
            Workspace(id=workspace_id, name="Explorer workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
        ]
    )
    await session.flush()
    ideas = []
    latest = []
    for index in range(count):
        idea_id = uuid4()
        iteration_id = uuid4()
        extra = uuid4()
        ideas.append(
            Idea(
                id=idea_id,
                slug=f"explorer-idea-{index}-{idea_id.hex[:8]}",
                title=f"Explorer idea {index}",
                pitch="A coop fleet",
                owner_id=owner_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
                sought_roles=["dev"] if index % 2 == 0 else ["growth"],
            )
        )
        latest.append(
            Iteration(
                id=iteration_id,
                idea_id=idea_id,
                parent_id=None,
                author_id=owner_id,
                message="Initial deposit",
                lang="en",
                payload={
                    "title": f"Explorer idea {index}",
                    "pitch": "A coop fleet",
                    "stage": "seed",
                },
                branch="main",
                proposal_status=None,
                short_hash=iteration_id.hex[:12],
                revision=1,
                created_at=datetime.now(UTC) - timedelta(hours=(30 - index)),
            )
        )
        latest.append(
            Iteration(
                id=extra,
                idea_id=idea_id,
                parent_id=iteration_id,
                author_id=owner_id,
                message="A later tweak",
                lang="en",
                payload={
                    "title": f"Explorer idea {index}",
                    "pitch": "A coop fleet",
                    "stage": "seed",
                },
                branch="main",
                proposal_status=None,
                short_hash=extra.hex[:12],
                revision=2,
                created_at=datetime.now(UTC) - timedelta(minutes=(50 - index * 5)),
            )
        )
    session.add_all(ideas + latest)
    await session.flush()
    return workspace_id, owner_id, ideas, latest


def _client(session, app, url, owner_id):
    app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_list_orders_by_recent_activity_with_fallback(explorer_database):
    engine, url = explorer_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, ideas, _ = await _seed(session)
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                listed = await client.get(f"/workspaces/{workspace_id}/ideas")
                assert listed.status_code == 200
                items = listed.json()["items"]
                titles = [item["title"] for item in items]
                # Idea 2 carries the globally latest extra iteration; the
                # ordering tracks that, not the creation order.
                assert titles[0] == "Explorer idea 2"
                assert all(item["last_activity_at"] for item in items)
                scores = {item["title"]: item["realism_score"] for item in items}
                assert set(scores.values()) == {None}
        await transaction.rollback()


async def test_list_filters_by_sought_role_and_realism(explorer_database):
    engine, url = explorer_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, ideas, latest = await _seed(session)
            repository = PostgresIterations(session)
            await store_raw_analysis(
                repository,
                ideas[0].id,
                latest[1].id,
                _analysis_payload(realism_score=75),
                model="test",
            )
            await store_raw_analysis(
                repository,
                ideas[2].id,
                latest[-1].id,
                _analysis_payload(realism_score=40),
                model="test",
            )
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                by_role = await client.get(f"/workspaces/{workspace_id}/ideas?sought_role=dev")
                assert by_role.status_code == 200
                assert {tuple(item["sought_roles"]) for item in by_role.json()["items"]} == {
                    ("dev",)
                }

                grounded = await client.get(f"/workspaces/{workspace_id}/ideas?realism_min=60")
                assert grounded.status_code == 200
                titles = [item["title"] for item in grounded.json()["items"]]
                assert titles == ["Explorer idea 0"]

                everything = await client.get(f"/workspaces/{workspace_id}/ideas")
                # Recent-activity order is idea 2, 1, 0.
                assert [item["realism_score"] for item in everything.json()["items"]] == [
                    40,
                    None,
                    75,
                ]
        await transaction.rollback()


async def test_list_still_filters_by_stage(explorer_database):
    engine, url = explorer_database

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, owner_id, ideas, _ = await _seed(session)
            ideas[1].stage = "iterating"
            await session.flush()
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                iterating = await client.get(f"/workspaces/{workspace_id}/ideas?stage=iterating")
                assert [item["title"] for item in iterating.json()["items"]] == ["Explorer idea 1"]
        await transaction.rollback()
