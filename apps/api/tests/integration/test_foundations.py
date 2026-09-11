import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.agents.graph import build_graph
from src.agents.schemas import GateFinding
from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session
from src.platform.effects import save_result
from src.platform.embeddings import (
    EmbeddingRecord,
    IdeaEmbedding,
    similar_idea_ids,
    store_embeddings,
)
from src.platform.map_identity import map_identity_in_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, async_sessionmaker(engine, expire_on_commit=False), url
    await engine.dispose()


async def test_http_workspace_isolation(database):
    engine, sessions, url = database
    workspace, other, user_id, idea_id = (uuid4() for _ in range(4))
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace, name="Test workspace"),
                    Workspace(id=other, name="Other workspace"),
                    User(id=user_id, auth_subject=str(user_id), display_name="Test user"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    WorkspaceMembership(workspace_id=other, user_id=user_id),
                    Idea(
                        id=idea_id,
                        slug=str(idea_id),
                        title="Private idea",
                        pitch="Private content",
                        owner_id=user_id,
                        workspace_id=workspace,
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()
            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(str(user_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                denied = await client.get(f"/ideas/{idea_id}")
                assert denied.status_code == 404
                assert "Private content" not in denied.text
                session.add(WorkspaceMembership(workspace_id=workspace, user_id=user_id))
                await session.flush()
                allowed = await client.get(f"/ideas/{idea_id}", headers={"Accept-Language": "fr"})
                assert allowed.status_code == 200
                assert allowed.json()["lang"] == "en"
                assert allowed.json()["pitch"] == "Private content"
                assert allowed.headers["Content-Language"] == "fr"
        await transaction.rollback()


async def test_logto_subject_mapping_is_idempotent_and_private(database):
    engine, _, _ = database
    workspace_id, other_workspace_id = uuid4(), uuid4()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Imported workspace"),
                    Workspace(id=other_workspace_id, name="Other workspace"),
                ]
            )
            await session.flush()
            first_user_id = await map_identity_in_session(
                session, "logto-owner", "Workspace owner", workspace_id
            )
            second_user_id = await map_identity_in_session(
                session, "logto-owner", "Workspace owner", workspace_id
            )
            assert first_user_id == second_user_id
            memberships = (
                await session.scalars(
                    select(WorkspaceMembership.workspace_id).where(
                        WorkspaceMembership.user_id == first_user_id
                    )
                )
            ).all()
            assert memberships == [workspace_id]
            assert (
                await session.scalar(
                    select(func.count()).select_from(User).where(User.auth_subject == "logto-owner")
                )
                == 1
            )
        await transaction.rollback()


async def test_embeddings_store_provenance_and_exclude_incompatible_space(database):
    engine, _, _ = database
    workspace_id, user_id, expected_id, unrelated_id = (uuid4() for _ in range(4))
    expected_vector = [1.0] + [0.0] * 1535
    unrelated_vector = [0.0, 1.0] + [0.0] * 1534
    settings = Settings(_env_file=None, database_url="postgresql+asyncpg://unused")
    incompatible_settings = settings.model_copy(
        update={"embedding_source_model": "another-embedding-model"}
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Embedding workspace"),
                    User(id=user_id, auth_subject=None, display_name="Embedding owner"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    Idea(
                        id=expected_id,
                        slug=str(expected_id),
                        title="Expected result",
                        pitch="Expected content",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                    Idea(
                        id=unrelated_id,
                        slug=str(unrelated_id),
                        title="Unrelated result",
                        pitch="Unrelated content",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()
            records = [
                EmbeddingRecord(expected_id, "Expected", "en", "expected", {"version": 1}),
                EmbeddingRecord(unrelated_id, "Unrelated", "en", "unrelated", {"version": 1}),
            ]
            await store_embeddings(session, records, [expected_vector, unrelated_vector], settings)
            await store_embeddings(
                session,
                [records[1]],
                [expected_vector],
                incompatible_settings,
            )
            await session.flush()
            matches = await similar_idea_ids(session, expected_vector, settings)
            assert matches[:2] == [expected_id, unrelated_id]
            stored = await session.scalar(
                select(IdeaEmbedding).where(
                    IdeaEmbedding.idea_id == expected_id,
                    IdeaEmbedding.model == settings.embedding_source_model,
                )
            )
            assert stored is not None
            assert stored.source_identifier == "expected"
            assert stored.provenance == {"version": 1}
            with pytest.raises(ValueError, match="dimension"):
                await store_embeddings(session, [records[0]], [[1.0]], settings)
            count = await session.scalar(select(func.count()).select_from(IdeaEmbedding))
            assert count == 3
        await transaction.rollback()


async def test_effect_is_idempotent_and_rejects_key_reuse(database):
    _, sessions, _ = database
    workflow = str(uuid4())
    first = await save_result(sessions, workflow, "persist", {"idea": "a"}, {"value": "first"})
    second = await save_result(sessions, workflow, "persist", {"idea": "a"}, {"value": "second"})
    assert first == second == {"value": "first"}
    with pytest.raises(ValueError, match="different input"):
        await save_result(sessions, workflow, "persist", {"idea": "b"}, {"value": "third"})


async def test_graph_resumes_after_checkpointer_reopens(database):
    _, sessions, url = database
    workflow = str(uuid4())

    class RecordedGateway:
        async def assess(self, title, pitch, locale, evidence):
            return GateFinding(
                verdict="unknown",
                reason="Insufficient evidence",
                source_ids=[],
                established_facts=[],
                locale=locale,
            )

    config = {"configurable": {"thread_id": workflow}}
    connection_url = url.replace("postgresql+asyncpg://", "postgresql://")
    async with AsyncPostgresSaver.from_conn_string(connection_url) as saver:
        await saver.setup()
        graph = build_graph(RecordedGateway(), saver, sessions)
        result = await graph.ainvoke(
            {
                "workflow_id": workflow,
                "locale": "en",
                "title": "Test",
                "pitch": "Test",
                "evidence": [],
                "finding": {},
            },
            config,
        )
        assert result["__interrupt__"]

    class NoSecondCall:
        async def assess(self, *args):
            raise AssertionError("A checkpoint resume must not call the LLM again")

    async with AsyncPostgresSaver.from_conn_string(connection_url) as saver:
        graph = build_graph(NoSecondCall(), saver, sessions)
        result = await graph.ainvoke(Command(resume=True), config)
        assert result["locale"] == "en"
        assert result["finding"]["verdict"] == "unknown"
        state = await graph.aget_state(config)
        assert state.next == ()
