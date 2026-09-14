import os
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.modules.company_context.adapters.postgres import CompanyConstraint, CompanyObjective
from src.modules.constraint_analysis.adapters.postgres import (
    ConstraintAnalysis,
    PostgresAnalysisWorkflows,
)
from src.modules.constraint_analysis.domain.models import AnalysisEvidence
from src.modules.constraint_analysis.service.operations import launch_analysis
from src.modules.constraint_analysis.service.read_model import display_from
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def context_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def test_context_is_injected_and_a_correction_runs_again_without_touching_the_first_run(
    context_database,
):
    engine, url = context_database
    workspace_id, user_id, idea_id = (uuid4() for _ in range(3))
    active_objective, archived_objective, active_constraint = (uuid4() for _ in range(3))

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Faktus"),
                    User(id=user_id, auth_subject=str(user_id), display_name="Owner"),
                    WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role="admin"),
                ]
            )
            await session.flush()
            session.add(
                Idea(
                    id=idea_id,
                    slug=f"context-{idea_id.hex[:8]}",
                    title="Deep discount campaign",
                    pitch="Fund growth with a 60 percent discount.",
                    owner_id=user_id,
                    workspace_id=workspace_id,
                    stage="seed",
                    lang="en",
                    visibility="workspace",
                )
            )
            session.add_all(
                [
                    CompanyObjective(
                        id=active_objective,
                        workspace_id=workspace_id,
                        title="Reach five paying pilots",
                        state="active",
                        priority=True,
                        lang="en",
                    ),
                    CompanyObjective(
                        id=archived_objective,
                        workspace_id=workspace_id,
                        title="Old objective",
                        state="archived",
                        priority=False,
                        lang="en",
                    ),
                    CompanyConstraint(
                        id=active_constraint,
                        workspace_id=workspace_id,
                        title="Gross margin stays above 60 percent",
                        detail="Board constraint",
                        state="active",
                        lang="en",
                    ),
                ]
            )
            await session.flush()
            repository = PostgresAnalysisWorkflows(session)

            first = await launch_analysis(
                repository,
                idea_id,
                str(user_id),
                idempotency_key="run-1",
                locale="en",
                evidence=[],
                trace_context={},
            )
            context = first.workflow.input_snapshot["company_context"]
            assert [item["id"] for item in context["objectives"]] == [
                f"objective:{active_objective}"
            ]
            assert [item["id"] for item in context["constraints"]] == [
                f"constraint:{active_constraint}"
            ]
            assert all(
                item["id"] != f"objective:{archived_objective}" for item in context["objectives"]
            )

            await repository.store_final(
                ConstraintAnalysis(
                    id=uuid4(),
                    workflow_id=first.workflow.id,
                    idea_id=idea_id,
                    source_iteration_id=None,
                    result={
                        "overall_score": None,
                        "verdict": "unknown",
                        "summary": "No evidence yet",
                        "contradictions": [],
                        "factors": [],
                        "locale": "en",
                    },
                    model="recorded",
                    locale="en",
                )
            )
            first_final = await repository.final_result(first.workflow.id)

            corrected = await launch_analysis(
                repository,
                idea_id,
                str(user_id),
                idempotency_key="run-2",
                locale="en",
                evidence=[
                    AnalysisEvidence(
                        id="e1",
                        url="https://example.test/margin",
                        text="Discounting above 40 percent breaks the margin target.",
                    )
                ],
                trace_context={},
            )
            assert corrected.workflow.id != first.workflow.id
            assert corrected.workflow.input_snapshot["company_context"]["constraints"][0]["id"] == (
                f"constraint:{active_constraint}"
            )

            unchanged = await repository.final_result(first.workflow.id)
            assert unchanged is not None
            assert unchanged.result == first_final.result
            assert unchanged.result["verdict"] == "unknown"

            display = display_from(
                corrected.workflow,
                ConstraintAnalysis(
                    id=uuid4(),
                    workflow_id=corrected.workflow.id,
                    idea_id=idea_id,
                    source_iteration_id=None,
                    result={
                        "overall_score": 35,
                        "verdict": "not_viable",
                        "summary": "The discount breaks the margin constraint.",
                        "contradictions": [
                            {
                                "target": "constraint",
                                "ref_id": f"constraint:{active_constraint}",
                                "detail": "Sixty percent off cannot hold the margin.",
                            }
                        ],
                        "factors": [
                            {
                                "name": name,
                                "basis": "unknown",
                                "score": None,
                                "gap": "No evidence",
                                "summary": "Unknown",
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
                    },
                    model="recorded",
                    locale="en",
                ),
            )
            assert display.contradictions == [
                {
                    "target": "constraint",
                    "ref_id": f"constraint:{active_constraint}",
                    "detail": "Sixty percent off cannot hold the margin.",
                }
            ]
            assert display.constraints["competition"]["basis"] == "unknown"
            assert display.constraints["competition"]["gap"] == "No evidence"

        await transaction.rollback()
    await engine.dispose()
