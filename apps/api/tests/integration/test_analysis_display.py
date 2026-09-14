import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.constraint_analysis.adapters.postgres import (
    AnalysisWorkflow,
    ConstraintAnalysis,
)
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def display_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


def _result(overall_score=62, verdict="conditional"):
    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "summary": "Grounded.",
        "factors": [
            {"name": name, "score": 60, "summary": "Evidence shows.", "source_ids": ["e1"]}
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


async def _seed(session):
    workspace_id, owner_id, idea_id = uuid4(), uuid4(), uuid4()
    main_id, branch_id = uuid4(), uuid4()
    session.add_all(
        [
            Workspace(id=workspace_id, name="Display workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
        ]
    )
    await session.flush()
    session.add_all(
        [
            Idea(
                id=idea_id,
                slug=f"display-{idea_id.hex[:8]}",
                title="Cargo bikes",
                pitch="Fleet",
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
                payload={"title": "Cargo bikes", "pitch": "Fleet", "stage": "seed"},
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
                payload={"title": "Cargo bikes", "pitch": "Fleet", "stage": "seed"},
                branch="proposal/offline",
                proposal_status="pending",
                short_hash=branch_id.hex[:12],
                revision=2,
            ),
        ]
    )
    await session.flush()
    return owner_id, idea_id, main_id, branch_id


async def _finish_workflow(session, owner_id, idea_id, iteration_id, result):
    workflow_id = uuid4()
    session.add(
        AnalysisWorkflow(
            id=workflow_id,
            idea_id=idea_id,
            source_iteration_id=iteration_id,
            requested_by_id=owner_id,
            idempotency_key=f"display-{workflow_id}",
            locale="en",
            status="completed",
            current_step="done",
            input_snapshot={},
            evidence=[],
            draft_result=None,
            review_decision=True,
        )
    )
    await session.flush()
    session.add(
        ConstraintAnalysis(
            id=uuid4(),
            workflow_id=workflow_id,
            idea_id=idea_id,
            source_iteration_id=iteration_id,
            result=result,
            model="test",
            locale="en",
        )
    )
    await session.flush()


def _client(session, app, url, owner_id):
    app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_idea_read_shows_head_analysis(display_database):
    engine, url = display_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            owner_id, idea_id, main_id, _ = await _seed(session)
            await _finish_workflow(session, owner_id, idea_id, main_id, _result())
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                body = (await client.get(f"/ideas/{idea_id}")).json()
            assert body["analysis"]["state"] == "resolved"
            assert body["analysis"]["realism_score"] == 62
        await transaction.rollback()


async def test_pending_proposal_shows_parent_analysis(display_database):
    engine, url = display_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            owner_id, idea_id, main_id, branch_id = await _seed(session)
            await _finish_workflow(session, owner_id, idea_id, main_id, _result())
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                history = (await client.get(f"/ideas/{idea_id}/iterations")).json()
            proposal = next(item for item in history if item["branch"] != "main")
            assert proposal["analysis"]["state"] == "resolved"
            assert proposal["analysis"]["iteration_id"] == str(main_id)
        await transaction.rollback()


async def test_open_workflow_reads_as_running(display_database):
    engine, url = display_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            owner_id, idea_id, main_id, _ = await _seed(session)
            session.add(
                AnalysisWorkflow(
                    id=uuid4(),
                    idea_id=idea_id,
                    source_iteration_id=main_id,
                    requested_by_id=owner_id,
                    idempotency_key=f"open-{uuid4()}",
                    locale="en",
                    status="queued",
                    current_step="queued",
                    input_snapshot={},
                    evidence=[],
                    draft_result=None,
                    review_decision=None,
                )
            )
            await session.flush()
            app = create_app(Settings(_env_file=None, database_url=url))
            async with _client(session, app, url, owner_id) as client:
                body = (await client.get(f"/ideas/{idea_id}")).json()
            assert body["analysis"]["state"] == "running"
        await transaction.rollback()
