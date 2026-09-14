import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

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


async def _seed(session):
    workspace_id, other_workspace_id, member_id, outsider_id = (uuid4() for _ in range(4))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Context workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            User(id=member_id, auth_subject=str(member_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=member_id, role="member"),
            WorkspaceMembership(
                workspace_id=other_workspace_id, user_id=outsider_id, role="member"
            ),
        ]
    )
    await session.flush()
    return workspace_id, other_workspace_id, member_id, outsider_id


def _client(session, url, subject: str):
    app = create_app(Settings(_env_file=None, database_url=url))
    app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_member_reads_empty_context(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, _ = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                response = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert response.status_code == 200
            body = response.json()
            assert body["profile"]["name"] is None
            assert body["objectives"] == []
            assert body["constraints"] == []
        await transaction.rollback()


async def test_profile_round_trip_and_upsert(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, _ = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                saved = await client.put(
                    f"/workspaces/{workspace_id}/company-context/profile",
                    json={
                        "name": "Faktus",
                        "description": "B2B marketing analytics",
                        "business_model": "Subscription",
                        "products_services": "Analytics suite",
                        "customer_segments": "Marketing leaders",
                        "markets": "France",
                        "structure": "12 people",
                    },
                    headers={"Accept-Language": "fr"},
                )
                assert saved.status_code == 200
                assert saved.json()["name"] == "Faktus"
                assert saved.json()["lang"] == "fr"

                updated = await client.put(
                    f"/workspaces/{workspace_id}/company-context/profile",
                    json={"name": "Faktus SAS", "description": "Updated"},
                    headers={"Accept-Language": "en"},
                )
                assert updated.status_code == 200
                assert updated.json()["name"] == "Faktus SAS"
                assert updated.json()["lang"] == "en"

                read = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert read.status_code == 200
            assert read.json()["profile"]["name"] == "Faktus SAS"
            assert read.json()["profile"]["description"] == "Updated"
            assert read.json()["profile"]["markets"] is None
        await transaction.rollback()


async def test_objective_lifecycle(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, _ = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                created = await client.post(
                    f"/workspaces/{workspace_id}/company-context/objectives",
                    json={"title": "Grow enterprise pipeline"},
                )
                assert created.status_code == 201
                objective = created.json()
                assert objective["state"] == "active"
                assert objective["priority"] is False
                assert objective["lang"] == "fr"

                updated = await client.patch(
                    f"/workspaces/{workspace_id}/company-context/objectives/{objective['id']}",
                    json={"state": "archived", "priority": True},
                    headers={"Accept-Language": "en"},
                )
                assert updated.status_code == 200
                assert updated.json()["state"] == "archived"
                assert updated.json()["priority"] is True
                assert updated.json()["lang"] == "en"

                invalid = await client.patch(
                    f"/workspaces/{workspace_id}/company-context/objectives/{objective['id']}",
                    json={"state": "paused"},
                    headers={"Accept-Language": "fr"},
                )
                assert invalid.status_code == 422

                read = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert [item["id"] for item in read.json()["objectives"]] == [objective["id"]]
            assert read.json()["objectives"][0]["state"] == "archived"
        await transaction.rollback()


async def test_constraint_lifecycle(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, _ = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                created = await client.post(
                    f"/workspaces/{workspace_id}/company-context/constraints",
                    json={
                        "title": "Two-person marketing team",
                        "detail": "No more hires this year",
                    },
                )
                assert created.status_code == 201
                constraint = created.json()
                assert constraint["state"] == "active"
                assert constraint["lang"] == "fr"

                updated = await client.patch(
                    f"/workspaces/{workspace_id}/company-context/constraints/{constraint['id']}",
                    json={"state": "archived"},
                )
                assert updated.status_code == 200
                assert updated.json()["state"] == "archived"
                assert updated.json()["detail"] == "No more hires this year"
        await transaction.rollback()


async def test_non_member_is_refused_everywhere(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, outsider_id = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                objective_id = (
                    await client.post(
                        f"/workspaces/{workspace_id}/company-context/objectives",
                        json={"title": "Real objective"},
                    )
                ).json()["id"]
                constraint_id = (
                    await client.post(
                        f"/workspaces/{workspace_id}/company-context/constraints",
                        json={"title": "Real constraint"},
                    )
                ).json()["id"]

            async with _client(session, url, str(outsider_id)) as client:
                read = await client.get(
                    f"/workspaces/{workspace_id}/company-context",
                    headers={"Accept-Language": "fr"},
                )
                assert read.status_code == 404
                assert "introuvable" in read.json()["detail"]

                write = await client.put(
                    f"/workspaces/{workspace_id}/company-context/profile",
                    json={"name": "Intruder"},
                )
                assert write.status_code == 404

                objective = await client.post(
                    f"/workspaces/{workspace_id}/company-context/objectives",
                    json={"title": "Intruder objective"},
                )
                assert objective.status_code == 404

                for path in (
                    f"/workspaces/{workspace_id}/company-context/objectives/{objective_id}",
                    f"/workspaces/{workspace_id}/company-context/constraints/{constraint_id}",
                ):
                    refused = await client.patch(path, json={"state": "archived"})
                    assert refused.status_code == 404
        await transaction.rollback()


async def test_update_refuses_explicit_nulls(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, member_id, _ = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                objective_id = (
                    await client.post(
                        f"/workspaces/{workspace_id}/company-context/objectives",
                        json={"title": "Objective"},
                    )
                ).json()["id"]
                constraint_id = (
                    await client.post(
                        f"/workspaces/{workspace_id}/company-context/constraints",
                        json={"title": "Constraint"},
                    )
                ).json()["id"]

                null_state = await client.patch(
                    f"/workspaces/{workspace_id}/company-context/objectives/{objective_id}",
                    json={"state": None},
                )
                assert null_state.status_code == 422
                null_title = await client.patch(
                    f"/workspaces/{workspace_id}/company-context/constraints/{constraint_id}",
                    json={"title": None},
                )
                assert null_title.status_code == 422

                read = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert read.json()["objectives"][0]["state"] == "active"
            assert read.json()["constraints"][0]["title"] == "Constraint"
        await transaction.rollback()


async def test_context_items_stay_inside_their_workspace(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, other_workspace_id, member_id, outsider_id = await _seed(session)
            async with _client(session, url, str(member_id)) as client:
                created = await client.post(
                    f"/workspaces/{workspace_id}/company-context/objectives",
                    json={"title": "Mine"},
                )
                assert created.status_code == 201
                objective_id = created.json()["id"]
                constraint_id = (
                    await client.post(
                        f"/workspaces/{workspace_id}/company-context/constraints",
                        json={"title": "Mine too"},
                    )
                ).json()["id"]

            # The outsider belongs to the other workspace, so authorization passes there:
            # the refusal below can only come from identifier scoping, not from access control.
            async with _client(session, url, str(outsider_id)) as client:
                cross = await client.patch(
                    f"/workspaces/{other_workspace_id}/company-context/objectives/{objective_id}",
                    json={"state": "archived"},
                )
                assert cross.status_code == 404
                cross_constraint = await client.patch(
                    f"/workspaces/{other_workspace_id}/company-context/constraints/{constraint_id}",
                    json={"state": "archived"},
                )
                assert cross_constraint.status_code == 404

                other_view = await client.get(f"/workspaces/{other_workspace_id}/company-context")
            assert other_view.json()["objectives"] == []
            assert other_view.json()["constraints"] == []

            async with _client(session, url, str(member_id)) as client:
                own = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert [item["title"] for item in own.json()["objectives"]] == ["Mine"]
            assert own.json()["objectives"][0]["state"] == "active"
        await transaction.rollback()


async def test_unauthenticated_request_is_unauthorized(context_database):
    engine, url = context_database
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            workspace_id, _, _, _ = await _seed(session)
            app = create_app(Settings(_env_file=None, database_url=url))

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(f"/workspaces/{workspace_id}/company-context")
            assert response.status_code == 401
        await transaction.rollback()
