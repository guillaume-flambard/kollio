import os
from time import perf_counter
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = [pytest.mark.performance, pytest.mark.integration]


async def test_workspace_idea_page_has_constant_query_count_and_latency() -> None:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for performance tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Performance tests require a dedicated kollio_test database")

    engine = create_async_engine(url)
    workspace_id, owner_id = uuid4(), uuid4()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        sessions = async_sessionmaker(connection, expire_on_commit=False)
        async with sessions() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Performance workspace"),
                    User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
                ]
            )
            await session.flush()
            session.add(
                WorkspaceMembership(
                    workspace_id=workspace_id,
                    user_id=owner_id,
                    role="admin",
                )
            )
            session.add_all(
                [
                    Idea(
                        id=uuid4(),
                        slug=f"performance-idea-{index}-{uuid4()}",
                        title=f"Performance idea {index}",
                        pitch="A stable payload for query-count regression testing.",
                        owner_id=owner_id,
                        workspace_id=workspace_id,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                        provenance={"domaine": "performance"},
                    )
                    for index in range(250)
                ]
            )
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            statements = 0

            def count_statement(*args: object) -> None:
                nonlocal statements
                statements += 1

            event.listen(connection.sync_connection, "before_cursor_execute", count_statement)
            started = perf_counter()
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/workspaces/{workspace_id}/ideas",
                    params={"limit": 100},
                )
            elapsed = perf_counter() - started
            event.remove(connection.sync_connection, "before_cursor_execute", count_statement)

            assert response.status_code == 200
            assert response.json()["total"] == 250
            assert len(response.json()["items"]) == 100
            assert statements == 4
            assert elapsed < 2.0
        await transaction.rollback()
    await engine.dispose()
