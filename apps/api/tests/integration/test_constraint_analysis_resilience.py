import asyncio
import os
from collections.abc import Mapping
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.constraint_analysis.adapters.postgres import AnalysisWorkflow
from src.modules.constraint_analysis.api.routes import get_analysis_queue
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


class RecoveringQueue:
    def __init__(self) -> None:
        self.launch_attempts = 0
        self.review_attempts = 0

    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None:
        self.launch_attempts += 1
        if self.launch_attempts == 1:
            raise ConnectionError("simulated Redis outage")

    async def dispatch_review(
        self,
        workflow_id: UUID,
        approved: bool,
        trace_context: Mapping[str, str],
    ) -> None:
        self.review_attempts += 1
        if self.review_attempts == 1:
            raise ConnectionError("simulated Redis outage")


class SlowRecordedQueue:
    def __init__(self) -> None:
        self.launch_attempts = 0

    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None:
        self.launch_attempts += 1
        await asyncio.sleep(0.05)

    async def dispatch_review(
        self,
        workflow_id: UUID,
        approved: bool,
        trace_context: Mapping[str, str],
    ) -> None:
        raise AssertionError("Review dispatch is outside this test")


async def test_dispatch_outages_can_be_retried_without_duplicate_workflows() -> None:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")

    engine = create_async_engine(url)
    workspace_id, owner_id, idea_id = (uuid4() for _ in range(3))
    queue = RecoveringQueue()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        sessions = async_sessionmaker(connection, expire_on_commit=False)
        async with sessions() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Resilience workspace"),
                    User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    WorkspaceMembership(
                        workspace_id=workspace_id,
                        user_id=owner_id,
                        role="admin",
                    ),
                    Idea(
                        id=idea_id,
                        slug=f"resilience-{idea_id}",
                        title="A resilient idea",
                        pitch="Recover queue dispatch safely.",
                        owner_id=owner_id,
                        workspace_id=workspace_id,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))
            app.dependency_overrides[get_analysis_queue] = lambda: queue

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                headers = {"Idempotency-Key": "resilient-launch"}
                failed_launch = await client.post(
                    f"/ideas/{idea_id}/analyses", json={"evidence": []}, headers=headers
                )
                assert failed_launch.status_code == 503

                recovered_launch = await client.post(
                    f"/ideas/{idea_id}/analyses", json={"evidence": []}, headers=headers
                )
                assert recovered_launch.status_code == 202
                workflow_id = UUID(recovered_launch.json()["id"])
                assert queue.launch_attempts == 2
                assert await session.get(AnalysisWorkflow, workflow_id) is not None

                workflow = await session.get(AnalysisWorkflow, workflow_id)
                assert workflow is not None
                workflow.status = "awaiting_review"
                workflow.current_step = "human_review"
                await session.flush()

                failed_review = await client.post(
                    f"/ideas/{idea_id}/analyses/{workflow_id}/review",
                    json={"approved": True},
                )
                assert failed_review.status_code == 503

                recovered_review = await client.post(
                    f"/ideas/{idea_id}/analyses/{workflow_id}/review",
                    json={"approved": True},
                )
                assert recovered_review.status_code == 202
                assert queue.review_attempts == 2

        await transaction.rollback()
    await engine.dispose()


async def test_concurrent_idempotent_launches_create_and_dispatch_once() -> None:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")

    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    workspace_id, owner_id, idea_id = (uuid4() for _ in range(3))
    async with sessions() as session:
        session.add_all(
            [
                Workspace(id=workspace_id, name="Concurrent launch workspace"),
                User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            ]
        )
        await session.flush()
        session.add_all(
            [
                WorkspaceMembership(
                    workspace_id=workspace_id,
                    user_id=owner_id,
                    role="admin",
                ),
                Idea(
                    id=idea_id,
                    slug=f"concurrent-{idea_id}",
                    title="A concurrent idea",
                    pitch="Deduplicate simultaneous launch requests.",
                    owner_id=owner_id,
                    workspace_id=workspace_id,
                    stage="seed",
                    lang="en",
                    visibility="workspace",
                ),
            ]
        )
        await session.commit()

    queue = SlowRecordedQueue()
    app = create_app(Settings(_env_file=None, database_url=url))
    app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))
    app.dependency_overrides[get_analysis_queue] = lambda: queue
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:

            async def launch() -> httpx.Response:
                return await client.post(
                    f"/ideas/{idea_id}/analyses",
                    json={"evidence": []},
                    headers={"Idempotency-Key": "concurrent-idempotency-key"},
                )

            first, second = await asyncio.gather(launch(), launch())

    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    assert queue.launch_attempts == 1
    async with sessions() as session:
        count = await session.scalar(
            select(func.count())
            .select_from(AnalysisWorkflow)
            .where(AnalysisWorkflow.idea_id == idea_id)
        )
        assert count == 1
    await engine.dispose()
