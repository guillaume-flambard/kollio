import os
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.modules.constraint_analysis.adapters.postgres import PostgresAnalysisWorkflows
from src.modules.constraint_analysis.service.operations import launch_analysis
from src.modules.experiments.adapters.postgres import (
    Experiment,
    Learning,
    PostgresExperiments,
)
from src.modules.experiments.service.operations import write_learning
from src.modules.experiments.service.reuse import reusable_learning_ids
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.config import Settings
from src.platform.embeddings import (
    LearningEmbedding,
    LearningEmbeddingRecord,
    store_learning_embeddings,
)

pytestmark = pytest.mark.integration

VIEWER_TEXT = "Offline first field app Offline field crews"
OTHER_TEXT = "Pricing page rewrite"


@pytest_asyncio.fixture
async def reuse_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


def _vector(dimensions: int, axis: int) -> list[float]:
    vector = [0.0] * dimensions
    vector[axis] = 1.0
    return vector


async def test_confirmed_learnings_are_embedded_and_reused_within_the_workspace(
    reuse_database, monkeypatch
):
    engine, url = reuse_database
    settings = Settings(_env_file=None, database_url=url)
    dimensions = settings.embedding_dimensions
    mine = _vector(dimensions, 0)
    theirs = _vector(dimensions, 1)

    async def fake_embed(texts, _settings):
        return [
            mine if VIEWER_TEXT.split()[0] in text or "margin" in text else theirs for text in texts
        ]

    monkeypatch.setattr("src.modules.experiments.service.reuse.embed", fake_embed)

    workspace_id, other_workspace_id, user_id, other_user_id = (uuid4() for _ in range(4))
    idea_id, other_idea_id, experiment_id, other_experiment_id = (uuid4() for _ in range(4))

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Faktus"),
                    Workspace(id=other_workspace_id, name="Other"),
                    User(id=user_id, auth_subject=str(user_id), display_name="Owner"),
                    User(id=other_user_id, auth_subject=str(other_user_id), display_name="Other"),
                    WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role="admin"),
                    WorkspaceMembership(
                        workspace_id=other_workspace_id, user_id=other_user_id, role="admin"
                    ),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    Idea(
                        id=idea_id,
                        slug=f"reuse-{idea_id.hex[:8]}",
                        title="Offline first field app",
                        pitch="Works without signal",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                    Idea(
                        id=other_idea_id,
                        slug=f"reuse-{other_idea_id.hex[:8]}",
                        title="Pricing page rewrite",
                        pitch="Cheaper plans",
                        owner_id=other_user_id,
                        workspace_id=other_workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    Experiment(
                        id=experiment_id,
                        idea_id=idea_id,
                        created_by_id=user_id,
                        title="Offline trial",
                        hypothesis="Crews accept conflicts when the app never blocks",
                        success_metric="offline sessions",
                        baseline="0",
                        target="40",
                        status="completed",
                    ),
                    Experiment(
                        id=other_experiment_id,
                        idea_id=other_idea_id,
                        created_by_id=other_user_id,
                        title="Pricing trial",
                        hypothesis="Cheaper plans convert",
                        success_metric="signups",
                        baseline="0",
                        target="50",
                        status="completed",
                    ),
                ]
            )
            await session.flush()

            # confirming a learning embeds it, with the workspace in provenance
            mine_learning = await write_learning(
                PostgresExperiments(session),
                experiment_id=experiment_id,
                subject=str(user_id),
                text="Crews tolerate sync conflicts when the app never blocks.",
                confirm=True,
            )
            stored = await session.scalar(
                select(LearningEmbedding).where(LearningEmbedding.learning_id == mine_learning.id)
            )
            assert stored is not None
            assert stored.provenance == {
                "workspace_id": str(workspace_id),
                "idea_id": str(idea_id),
                "experiment_id": str(experiment_id),
            }

            # the other workspace's confirmed learning, embedded directly
            their_learning = Learning(
                id=uuid4(),
                experiment_id=other_experiment_id,
                idea_id=other_idea_id,
                status="confirmed",
                text="Cheaper plans did not convert the enterprise segment.",
                outcome_ids=[],
                confirmed_by_id=other_user_id,
            )
            session.add(their_learning)
            await session.flush()
            await store_learning_embeddings(
                session,
                [
                    LearningEmbeddingRecord(
                        learning_id=their_learning.id,
                        text=their_learning.text,
                        source_language="en",
                        source_identifier="learning.confirmed",
                        provenance={"workspace_id": str(other_workspace_id)},
                    )
                ],
                [theirs],
                settings,
            )
            await session.flush()

            # retrieval never crosses the workspace boundary
            assert await reusable_learning_ids(
                session,
                text=VIEWER_TEXT,
                workspace_ids=frozenset({workspace_id}),
                settings=settings,
            ) == [mine_learning.id]
            assert await reusable_learning_ids(
                session,
                text=VIEWER_TEXT,
                workspace_ids=frozenset({other_workspace_id}),
                settings=settings,
            ) == [their_learning.id]
            assert (
                await reusable_learning_ids(
                    session, text=VIEWER_TEXT, workspace_ids=frozenset(), settings=settings
                )
                == []
            )

            # launching the analysis injects the reusable learning as evidence
            outcome = await launch_analysis(
                PostgresAnalysisWorkflows(session),
                idea_id,
                str(user_id),
                idempotency_key="reuse-1",
                locale="en",
                evidence=[],
                trace_context={},
            )
            assert outcome.workflow.input_snapshot["reused_learning_ids"] == [str(mine_learning.id)]
            injected = {
                item["id"]
                for item in outcome.workflow.evidence
                if item["id"].startswith("learning:")
            }
            assert injected == {f"learning:{mine_learning.id}"}

            # an outsider cannot launch on the other workspace's idea at all
            with pytest.raises(LookupError):
                await launch_analysis(
                    PostgresAnalysisWorkflows(session),
                    other_idea_id,
                    str(user_id),
                    idempotency_key="reuse-2",
                    locale="en",
                    evidence=[],
                    trace_context={},
                )

        await transaction.rollback()
