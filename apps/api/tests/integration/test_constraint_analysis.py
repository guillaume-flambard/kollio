import os
from collections.abc import Mapping
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.constraint_analysis.adapters.postgres import (
    AnalysisWorkflow,
    ConstraintAnalysis,
    PostgresAnalysisWorkflows,
)
from src.modules.constraint_analysis.agent.graph import build_constraint_analysis_graph
from src.modules.constraint_analysis.api.routes import get_analysis_queue
from src.modules.constraint_analysis.domain.lifecycle import AnalysisStatus
from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


class RecordedQueue:
    def __init__(self) -> None:
        self.launches: list[UUID] = []
        self.reviews: list[tuple[UUID, bool]] = []
        self.launch_trace_contexts: list[dict[str, str]] = []
        self.review_trace_contexts: list[dict[str, str]] = []

    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None:
        self.launches.append(workflow_id)
        self.launch_trace_contexts.append(dict(trace_context))

    async def dispatch_review(
        self,
        workflow_id: UUID,
        approved: bool,
        trace_context: Mapping[str, str],
    ) -> None:
        self.reviews.append((workflow_id, approved))
        self.review_trace_contexts.append(dict(trace_context))


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


async def test_workflow_launch_is_idempotent_and_review_is_owner_controlled(
    analysis_database,
) -> None:
    engine, url = analysis_database
    workspace_id, owner_id, member_id, outsider_id, idea_id = (uuid4() for _ in range(5))
    subject = {"value": str(member_id)}
    queue = RecordedQueue()

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Analysis workspace"),
                    User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
                    User(id=member_id, auth_subject=str(member_id), display_name="Member"),
                    User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
                    WorkspaceMembership(
                        workspace_id=workspace_id, user_id=member_id, role="member"
                    ),
                    Idea(
                        id=idea_id,
                        slug=f"analysis-{idea_id}",
                        title="A durable idea",
                        pitch="Test the important constraints.",
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
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])
            app.dependency_overrides[get_analysis_queue] = lambda: queue

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                trace_id = "0af7651916cd43dd8448eb211c80319c"
                headers = {
                    "Idempotency-Key": "analysis-request-1",
                    "traceparent": f"00-{trace_id}-b7ad6b7169203331-01",
                }
                launched = await client.post(
                    f"/ideas/{idea_id}/analyses", json={"evidence": []}, headers=headers
                )
                assert launched.status_code == 202
                workflow_id = UUID(launched.json()["id"])
                assert queue.launches == [workflow_id]
                assert queue.launch_trace_contexts[0]["traceparent"].split("-")[1] == trace_id

                repeated = await client.post(
                    f"/ideas/{idea_id}/analyses", json={"evidence": []}, headers=headers
                )
                assert repeated.status_code == 202
                assert repeated.json()["id"] == str(workflow_id)
                assert queue.launches == [workflow_id]

                subject["value"] = str(outsider_id)
                hidden = await client.get(f"/ideas/{idea_id}/analyses/{workflow_id}")
                assert hidden.status_code == 404

                workflow = await session.get(AnalysisWorkflow, workflow_id)
                assert workflow is not None
                workflow.status = AnalysisStatus.AWAITING_REVIEW.value
                workflow.current_step = "human_review"
                await session.flush()

                subject["value"] = str(member_id)
                denied = await client.post(
                    f"/ideas/{idea_id}/analyses/{workflow_id}/review",
                    json={"approved": True},
                )
                assert denied.status_code == 403

                subject["value"] = str(owner_id)
                approved = await client.post(
                    f"/ideas/{idea_id}/analyses/{workflow_id}/review",
                    json={"approved": True},
                )
                assert approved.status_code == 202
                assert approved.json()["status"] == "review_queued"
                assert queue.reviews == [(workflow_id, True)]

                repeated_review = await client.post(
                    f"/ideas/{idea_id}/analyses/{workflow_id}/review",
                    json={"approved": True},
                )
                assert repeated_review.status_code == 409

                result = {
                    "overall_score": 50,
                    "verdict": "unknown",
                    "summary": "More evidence is required.",
                    "factors": [
                        {
                            "name": name,
                            "score": 50,
                            "summary": "No evidence was supplied.",
                            "source_ids": [],
                        }
                        for name in (
                            "competition",
                            "build_cost",
                            "time_to_market",
                            "defensibility",
                            "acquisition",
                        )
                    ],
                    "locale": "en",
                }
                repository = PostgresAnalysisWorkflows(session)
                first_result = await repository.store_final(
                    ConstraintAnalysis(
                        id=uuid4(),
                        workflow_id=workflow_id,
                        idea_id=idea_id,
                        source_iteration_id=None,
                        result=result,
                        model="recorded-model",
                        locale="en",
                    )
                )
                second_result = await repository.store_final(
                    ConstraintAnalysis(
                        id=uuid4(),
                        workflow_id=workflow_id,
                        idea_id=idea_id,
                        source_iteration_id=None,
                        result=result,
                        model="recorded-model",
                        locale="en",
                    )
                )
                assert second_result.id == first_result.id
        await transaction.rollback()


async def test_constraint_graph_resumes_without_repeating_model_call(analysis_database) -> None:
    _, url = analysis_database
    workflow_id = str(uuid4())
    factor_names = (
        "competition",
        "build_cost",
        "time_to_market",
        "defensibility",
        "acquisition",
    )

    class RecordedGateway:
        async def analyze(self, *, title, pitch, locale, evidence):
            return ConstraintAnalysisResult.model_validate(
                {
                    "overall_score": 50,
                    "verdict": "unknown",
                    "summary": "More evidence is required.",
                    "factors": [
                        {
                            "name": name,
                            "score": 50,
                            "summary": "No evidence was supplied.",
                            "source_ids": [],
                        }
                        for name in factor_names
                    ],
                    "locale": locale,
                }
            )

    config = {"configurable": {"thread_id": workflow_id}}
    checkpoint_url = url.replace("postgresql+asyncpg://", "postgresql://")
    async with AsyncPostgresSaver.from_conn_string(checkpoint_url) as saver:
        await saver.setup()
        graph = build_constraint_analysis_graph(RecordedGateway(), saver)
        paused = await graph.ainvoke(
            {
                "workflow_id": workflow_id,
                "locale": "fr",
                "title": "Test",
                "pitch": "Test",
                "evidence": [],
                "result": {},
                "approved": None,
            },
            config,
        )
        assert paused["__interrupt__"]

    class NoSecondCall:
        async def analyze(self, **kwargs):
            raise AssertionError("Checkpoint resume must not call the model again")

    async with AsyncPostgresSaver.from_conn_string(checkpoint_url) as saver:
        graph = build_constraint_analysis_graph(NoSecondCall(), saver)
        completed = await graph.ainvoke(Command(resume=True), config)
        assert completed["locale"] == "fr"
        assert completed["result"]["overall_score"] == 50
        state = await graph.aget_state(config)
        assert state.next == ()
