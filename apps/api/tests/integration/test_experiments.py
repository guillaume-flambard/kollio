import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def experiments_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def _seed(session, workspace_id, owner_id, member_id, outsider_id, idea_id):
    session.add_all(
        [
            Workspace(id=workspace_id, name="Loop workspace"),
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
                slug=f"loop-idea-{idea_id.hex[:8]}",
                title="Offline first field app",
                pitch="Works without signal",
                owner_id=owner_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
        ]
    )
    await session.flush()


async def _harness(engine, url, seed_ids, subject):
    connection = await engine.connect()
    transaction = await connection.begin()
    local = async_sessionmaker(connection, expire_on_commit=False)
    session = local()
    await _seed(session, *seed_ids)
    await session.flush()
    app = create_app(Settings(_env_file=None, database_url=url))
    app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
    return client, session, transaction, connection


async def test_the_learning_loop_records_outcomes_and_confirms_a_learning(experiments_database):
    engine, url = experiments_database
    seed_ids = tuple(uuid4() for _ in range(5))
    owner_id, member_id, idea_id = seed_ids[1], seed_ids[2], seed_ids[4]
    subject = {"value": str(owner_id)}
    client, session, transaction, connection = await _harness(engine, url, seed_ids, subject)
    async with client:
        created = await client.post(
            f"/ideas/{idea_id}/experiments",
            json={
                "title": "Offline trial with five crews",
                "hypothesis": "Crews accept sync conflicts if the app never blocks",
                "success_metric": "field sessions completed offline",
                "baseline": "0",
                "target": "40",
            },
        )
        assert created.status_code == 201
        experiment_id = created.json()["id"]
        assert created.json()["status"] == "proposed"

        skipped = await client.post(
            f"/experiments/{experiment_id}/status", json={"status": "completed"}
        )
        assert skipped.status_code == 422

        running = await client.post(
            f"/experiments/{experiment_id}/status", json={"status": "running"}
        )
        assert running.status_code == 200
        assert running.json()["started_at"] is not None

        subject["value"] = str(member_id)
        first = await client.post(
            f"/experiments/{experiment_id}/outcomes",
            json={"metric": "sessions", "value": "18", "unit": "sessions", "comment": "two crews"},
        )
        assert first.status_code == 201
        second = await client.post(
            f"/experiments/{experiment_id}/outcomes",
            json={
                "metric": "conflicts",
                "value": "3",
                "qualitative": "all resolved without data loss",
            },
        )
        assert second.status_code == 201

        detail = await client.get(f"/experiments/{experiment_id}")
        assert len(detail.json()["outcomes"]) == 2
        assert detail.json()["learning"] is None

        subject["value"] = str(owner_id)
        completed = await client.post(
            f"/experiments/{experiment_id}/status", json={"status": "completed"}
        )
        assert completed.status_code == 200
        assert completed.json()["ended_at"] is not None

        detail = await client.get(f"/experiments/{experiment_id}")
        learning = detail.json()["learning"]
        assert learning["status"] == "draft"
        assert "Hypothesis: Crews accept sync conflicts" in learning["text"]
        assert "Target: 40" in learning["text"]
        assert len(learning["outcome_ids"]) == 2

        confirmed = await client.post(
            f"/experiments/{experiment_id}/learnings",
            json={"text": "Crews tolerate conflicts when the app never blocks.", "confirm": True},
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["status"] == "confirmed"
        assert confirmed.json()["confirmed_by_id"] == str(owner_id)

        by_idea = await client.get(f"/ideas/{idea_id}/learnings")
        assert [item["experiment_id"] for item in by_idea.json()] == [experiment_id]

        listed = await client.get(f"/ideas/{idea_id}/experiments")
        assert [item["id"] for item in listed.json()] == [experiment_id]

        subject["value"] = str(seed_ids[3])
        denied = await client.get(f"/experiments/{experiment_id}")
        assert denied.status_code == 404
        denied_write = await client.post(
            f"/experiments/{experiment_id}/outcomes", json={"metric": "x", "value": "1"}
        )
        assert denied_write.status_code == 404

    await session.close()
    await transaction.rollback()
    await connection.close()
