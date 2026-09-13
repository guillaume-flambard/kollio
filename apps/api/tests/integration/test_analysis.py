import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.agents.schemas import ConstraintAnalysis
from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import (
    IdeaAnalysis,
    Iteration,
    PostgresIterations,
)
from src.modules.iterations.store import save_analysis
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session
from src.platform.queue import get_analysis_queue

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


async def _seed_idea(session):
    workspace_id, owner_id, idea_id, iteration_id = (uuid4() for _ in range(4))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Analysis workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
        ]
    )
    await session.flush()
    session.add_all(
        [
            Idea(
                id=idea_id,
                slug=f"analysis-idea-{idea_id.hex[:8]}",
                title="Shared cargo bikes",
                pitch="A coop fleet",
                owner_id=owner_id,
                workspace_id=workspace_id,
                stage="seed",
                lang="en",
                visibility="workspace",
            ),
            Iteration(
                id=iteration_id,
                idea_id=idea_id,
                parent_id=None,
                author_id=owner_id,
                message="Initial deposit",
                lang="en",
                payload={"title": "Shared cargo bikes", "pitch": "A coop fleet", "stage": "seed"},
                branch="main",
                proposal_status=None,
                short_hash=iteration_id.hex[:12],
                revision=1,
            ),
        ]
    )
    await session.flush()
    return workspace_id, owner_id, idea_id, iteration_id


async def test_analysis_storage_is_bound_and_idempotent(analysis_database):
    engine, url = analysis_database
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            _, _, idea_id, iteration_id = await _seed_idea(session)
            analyses = PostgresIterations(session)

            analysis = ConstraintAnalysis.model_validate(_analysis_payload())
            stored = await save_analysis(analyses, idea_id, iteration_id, analysis, model="test")
            assert stored.iteration_id == iteration_id
            assert stored.realism_score == 62

            again = await save_analysis(analyses, idea_id, iteration_id, analysis, model="other")
            assert again.id == stored.id
            assert again.realism_score == 62

            rows = (
                await session.scalars(
                    select(IdeaAnalysis).where(IdeaAnalysis.iteration_id == iteration_id)
                )
            ).all()
            assert len(rows) == 1

        await transaction.rollback()


async def test_malformed_analysis_is_rejected_before_insert(analysis_database):
    engine, url = analysis_database
    del url

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            from pydantic import ValidationError

            from src.modules.iterations.store import store_raw_analysis

            _, _, idea_id, iteration_id = await _seed_idea(session)
            payload = _analysis_payload()
            del payload["acquisition"]
            with pytest.raises(ValidationError):
                await store_raw_analysis(
                    PostgresIterations(session), idea_id, iteration_id, payload, model="test"
                )

        await transaction.rollback()


async def test_deposit_enqueues_analysis(analysis_database):
    engine, url = analysis_database
    workspace_id, member_id, outsider_id = (uuid4() for _ in range(3))
    subject = {"value": str(member_id)}
    enqueued = []

    class FakeQueue:
        async def enqueue(self, **job):
            enqueued.append(job)

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Deposit workspace"),
                    User(id=member_id, auth_subject=str(member_id), display_name="Member"),
                    User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
                    WorkspaceMembership(
                        workspace_id=workspace_id, user_id=member_id, role="member"
                    ),
                ]
            )
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])
            app.dependency_overrides[get_analysis_queue] = lambda: FakeQueue()

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                deposited = await client.post(
                    f"/workspaces/{workspace_id}/ideas",
                    json={"title": "Shared cargo bikes", "pitch": "A coop fleet", "lang": "en"},
                )
                assert deposited.status_code == 201
                assert len(enqueued) == 1
                job = enqueued[0]
                assert job["idea_id"] == deposited.json()["id"]
                assert job["locale"] == "en"
                assert job["title"] == "Shared cargo bikes"

        await transaction.rollback()
