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
from src.modules.ideas.adapters.postgres import (
    Idea,
    IdeaMembership,
    User,
    Workspace,
    WorkspaceMembership,
)
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
from src.platform.import_legacy import IMPORTER_ID, WORKSPACE_ID
from src.platform.map_identity import map_identity_in_session
from src.platform.seed_demo import DEMO_PROFILES, reset_demo_data, seed_demo_data

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
    settings = settings.model_copy(
        update={
            "embedding_model": "kollio-embedding",
            "embedding_source_model": "text-embedding-3-large",
            "embedding_dimensions": 1536,
        }
    )
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
            matches = await similar_idea_ids(
                session, expected_vector, settings, workspace_ids=frozenset({workspace_id})
            )
            assert matches[:2] == [expected_id, unrelated_id]
            assert (
                await similar_idea_ids(
                    session, expected_vector, settings, workspace_ids=frozenset({uuid4()})
                )
                == []
            )
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


async def test_embedding_spaces_exclude_each_other_in_both_directions(database):
    engine, _, _ = database
    workspace_id, user_id, local_id, openai_id = (uuid4() for _ in range(4))
    local_settings = Settings(_env_file=None, database_url="postgresql+asyncpg://unused")
    assert local_settings.embedding_dimensions == 384
    openai_settings = local_settings.model_copy(
        update={
            "embedding_model": "kollio-embedding",
            "embedding_source_model": "text-embedding-3-large",
            "embedding_dimensions": 1536,
        }
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Two-space workspace"),
                    User(id=user_id, auth_subject=None, display_name="Space owner"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    Idea(
                        id=local_id,
                        slug=str(local_id),
                        title="Local idea",
                        pitch="Local content",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                    Idea(
                        id=openai_id,
                        slug=str(openai_id),
                        title="OpenAI idea",
                        pitch="OpenAI content",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()
            await store_embeddings(
                session,
                [EmbeddingRecord(local_id, "Local", "en", "local", {})],
                [[1.0] + [0.0] * 383],
                local_settings,
            )
            await store_embeddings(
                session,
                [EmbeddingRecord(openai_id, "OpenAI", "en", "openai", {})],
                [[1.0] + [0.0] * 1535],
                openai_settings,
            )
            await session.flush()
            local_matches = await similar_idea_ids(
                session,
                [1.0] + [0.0] * 383,
                local_settings,
                workspace_ids=frozenset({workspace_id}),
            )
            assert local_matches == [local_id]
            openai_matches = await similar_idea_ids(
                session,
                [1.0] + [0.0] * 1535,
                openai_settings,
                workspace_ids=frozenset({workspace_id}),
            )
            assert openai_matches == [openai_id]
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


async def test_member_discovers_only_their_workspaces(database):
    engine, _, url = database
    included_workspace, excluded_workspace, user_id = (uuid4() for _ in range(3))
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=included_workspace, name="Included workspace"),
                    Workspace(id=excluded_workspace, name="Excluded workspace"),
                    User(id=user_id, auth_subject=str(user_id), display_name="Workspace member"),
                ]
            )
            await session.flush()
            session.add(
                WorkspaceMembership(
                    workspace_id=included_workspace,
                    user_id=user_id,
                    role="admin",
                )
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
                response = await client.get("/workspaces")

            assert response.status_code == 200
            assert response.json() == [
                {
                    "id": str(included_workspace),
                    "name": "Included workspace",
                    "role": "admin",
                }
            ]
        await transaction.rollback()


async def test_member_browses_only_their_workspace_ideas(database):
    from datetime import UTC, datetime

    engine, _, url = database
    workspace_id, other_workspace_id, user_id, older_id, newer_id, hidden_id = (
        uuid4() for _ in range(6)
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Product workspace"),
                    Workspace(id=other_workspace_id, name="Hidden workspace"),
                    User(id=user_id, auth_subject=str(user_id), display_name="Product member"),
                ]
            )
            await session.flush()
            session.add(
                WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role="member")
            )
            session.add_all(
                [
                    Idea(
                        id=older_id,
                        slug="older-idea",
                        title="Older idea",
                        pitch="Older pitch",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                        created_at=datetime(2026, 1, 1, tzinfo=UTC),
                    ),
                    Idea(
                        id=newer_id,
                        slug="newer-idea",
                        title="Newer idea",
                        pitch="Newer pitch",
                        owner_id=user_id,
                        workspace_id=workspace_id,
                        stage="iterating",
                        lang="fr",
                        visibility="workspace",
                        created_at=datetime(2026, 2, 1, tzinfo=UTC),
                        provenance={"domaine": "Developer tools"},
                    ),
                    Idea(
                        id=hidden_id,
                        slug="hidden-idea",
                        title="Hidden idea",
                        pitch="Hidden pitch",
                        owner_id=user_id,
                        workspace_id=other_workspace_id,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                        created_at=datetime(2026, 3, 1, tzinfo=UTC),
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
                page = await client.get(
                    f"/workspaces/{workspace_id}/ideas", params={"limit": 1, "offset": 0}
                )
                denied = await client.get(f"/workspaces/{other_workspace_id}/ideas")
                searched = await client.get(
                    f"/workspaces/{workspace_id}/ideas", params={"q": "newer"}
                )
                searched_by_domain = await client.get(
                    f"/workspaces/{workspace_id}/ideas", params={"q": "developer"}
                )
                staged = await client.get(
                    f"/workspaces/{workspace_id}/ideas", params={"stage": "seed"}
                )
                domain = await client.get(
                    f"/workspaces/{workspace_id}/ideas",
                    params={"domain": "Developer tools"},
                )

            assert page.status_code == 200
            assert page.json() == {
                "items": [
                    {
                        "id": str(newer_id),
                        "slug": "newer-idea",
                        "title": "Newer idea",
                        "pitch": "Newer pitch",
                        "stage": "iterating",
                        "initiative_type": "idea",
                        "lang": "fr",
                        "created_at": "2026-02-01T00:00:00Z",
                        "sought_roles": [],
                        "realism_score": None,
                        "last_activity_at": None,
                        "collaborators": [],
                    }
                ],
                "total": 2,
                "limit": 1,
                "offset": 0,
            }
            assert denied.status_code == 404
            assert "Hidden" not in denied.text
            assert searched.status_code == 200
            assert searched.json()["total"] == 1
            assert searched.json()["items"][0]["id"] == str(newer_id)
            assert searched_by_domain.status_code == 200
            assert searched_by_domain.json()["total"] == 1
            assert searched_by_domain.json()["items"][0]["id"] == str(newer_id)
            assert staged.status_code == 200
            assert staged.json()["total"] == 1
            assert staged.json()["items"][0]["id"] == str(older_id)
            assert domain.status_code == 200
            assert domain.json()["total"] == 2
            assert domain.json()["items"][0]["id"] == str(newer_id)
        await transaction.rollback()


async def test_demo_collaborators_seed_idempotently_and_appear_on_idea(database):
    engine, _, url = database
    identity_id, idea_id = uuid4(), uuid4()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=WORKSPACE_ID, name="Prospecteur import"),
                    User(
                        id=IMPORTER_ID,
                        auth_subject=None,
                        display_name="Legacy importer",
                    ),
                    User(
                        id=identity_id,
                        auth_subject=str(identity_id),
                        display_name="Test member",
                    ),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    WorkspaceMembership(
                        workspace_id=WORKSPACE_ID,
                        user_id=identity_id,
                        role="member",
                    ),
                    Idea(
                        id=idea_id,
                        slug="seeded-collaboration",
                        title="Seeded collaboration",
                        pitch="A private idea with a real persisted demo team.",
                        owner_id=IMPORTER_ID,
                        workspace_id=WORKSPACE_ID,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                        source="prospecteur",
                        source_id="seeded-collaboration",
                        provenance={"cle": "seeded-collaboration"},
                    ),
                ]
            )
            await session.flush()

            first = await seed_demo_data(session)
            second = await seed_demo_data(session)
            assert first == second
            assert first["users"] == len(DEMO_PROFILES)
            assert first["ideas"] == 1
            assert await session.scalar(
                select(func.count()).select_from(User).where(User.is_demo.is_(True))
            ) == len(DEMO_PROFILES)
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(IdeaMembership)
                    .where(IdeaMembership.idea_id == idea_id)
                )
                == first["memberships"]
            )

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(str(identity_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(f"/ideas/{idea_id}")
                page_response = await client.get(f"/workspaces/{WORKSPACE_ID}/ideas")

            assert response.status_code == 200
            collaborators = response.json()["collaborators"]
            assert len(collaborators) == first["memberships"]
            assert all(collaborator["handle"] for collaborator in collaborators)
            assert all(collaborator["avatar_key"] for collaborator in collaborators)
            assert page_response.status_code == 200
            assert page_response.json()["items"][0]["collaborators"] == collaborators

            reset = await reset_demo_data(session)
            assert reset["users"] == len(DEMO_PROFILES)
            assert await session.scalar(select(func.count()).select_from(IdeaMembership)) == 0
            assert (await session.get(Idea, idea_id)).stage == "seed"
        await transaction.rollback()
