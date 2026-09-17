import os
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.branches.service.branches import propose_contribution
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def converge_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


@asynccontextmanager
async def _tx(engine):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            local = async_sessionmaker(connection, expire_on_commit=False)
            async with local() as session:
                yield session
        finally:
            await transaction.rollback()


async def _seed(session):
    workspace_id, other_workspace_id = uuid4(), uuid4()
    owner_id, participant_id, uninvolved_id, outsider_id = (uuid4() for _ in range(4))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Converge workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=participant_id, auth_subject=str(participant_id), display_name="Member"),
            User(id=uninvolved_id, auth_subject=str(uninvolved_id), display_name="Uninvolved"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=participant_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=uninvolved_id, role="member"),
            WorkspaceMembership(
                workspace_id=other_workspace_id, user_id=outsider_id, role="member"
            ),
        ]
    )
    await session.flush()
    return {
        "workspace_id": workspace_id,
        "other_workspace_id": other_workspace_id,
        "owner_id": owner_id,
        "participant_id": participant_id,
        "uninvolved_id": uninvolved_id,
        "outsider_id": outsider_id,
    }


def _client(session, url, subject: str | None):
    app = create_app(Settings(_env_file=None, database_url=url))
    if subject is not None:
        app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def _open_space(session, workspace_id, owner_id, question="What should we build?"):
    space = await PostgresDecisionSpaces(session).create(
        workspace_id=workspace_id,
        question=question,
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )
    await session.flush()
    return space


async def _two_contributions(session, url, ids):
    space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
    base = f"/workspaces/{ids['workspace_id']}/decision-spaces/{space.id}"
    async with _client(session, url, str(ids["owner_id"])) as client:
        branch = (
            await client.post(
                f"{base}/branches",
                json={"title": "Explore", "visibility": "shared"},
            )
        ).json()
        first = (
            await client.post(
                f"{base}/contributions",
                json={"branch_id": branch["id"], "kind": "claim", "title": "First"},
            )
        ).json()
        second = (
            await client.post(
                f"{base}/contributions",
                json={"branch_id": branch["id"], "kind": "evidence", "title": "Second"},
            )
        ).json()
    return base, space, branch, first, second


async def test_member_reads_map(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            linked = await client.post(
                f"{base}/relations",
                json={
                    "from_contribution_id": first["id"],
                    "to_contribution_id": second["id"],
                    "relation_type": "SUPPORTS",
                },
            )
            assert linked.status_code == 201
            assert linked.json()["created_by"] == str(ids["owner_id"])

            clustered = await client.post(f"{base}/clusters", json={"title": "Agreement"})
            assert clustered.status_code == 201

            response = await client.get(f"{base}/converge/map", headers={"Accept-Language": "fr"})
            assert response.status_code == 200
            body = response.json()
            assert {c["id"] for c in body["contributions"]} == {first["id"], second["id"]}
            assert len(body["relations"]) == 1
            assert body["relations"][0]["relation_type"] == "SUPPORTS"
            assert len(body["clusters"]) == 1
            assert body["clusters"][0]["member_ids"] == []


async def test_non_member_is_refused_everywhere(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (await client.get(f"{base}/converge/map")).status_code == 404
            assert (
                await client.post(
                    f"{base}/relations",
                    json={
                        "from_contribution_id": first["id"],
                        "to_contribution_id": second["id"],
                        "relation_type": "SUPPORTS",
                    },
                )
            ).status_code == 404
            assert (
                await client.post(f"{base}/clusters", json={"title": "Nope"})
            ).status_code == 404


async def test_unauthenticated_request_is_unauthorized(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, None) as client:
            assert (await client.get(f"{base}/converge/map")).status_code == 401


async def test_suggested_contributions_excluded(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        branches = PostgresBranches(session)
        await propose_contribution(
            branches,
            ids["workspace_id"],
            space.id,
            str(ids["owner_id"]),
            branch_id=branch["id"],
            kind="objection",
            title="A suggestion",
            body=None,
            source=None,
            tool_model="model/test",
            transformation_history=None,
            as_suggestion=True,
            lang="en",
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            body = (await client.get(f"{base}/converge/map")).json()
            assert {c["id"] for c in body["contributions"]} == {first["id"], second["id"]}


async def test_relation_round_trip(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"{base}/relations",
                json={
                    "from_contribution_id": first["id"],
                    "to_contribution_id": second["id"],
                    "relation_type": "CONTRADICTS",
                },
            )
            assert created.status_code == 201
            body = created.json()
            assert body["space_id"] == str(space.id)
            assert body["relation_type"] == "CONTRADICTS"

            seen = (await client.get(f"{base}/converge/map")).json()
            assert [r["id"] for r in seen["relations"]] == [body["id"]]


async def test_unknown_relation_type_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"{base}/relations",
                json={
                    "from_contribution_id": first["id"],
                    "to_contribution_id": second["id"],
                    "relation_type": "AGREES_WITH",
                },
            )
            assert refused.status_code == 422
            seen = (await client.get(f"{base}/converge/map")).json()
            assert seen["relations"] == []


async def test_self_relation_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"{base}/relations",
                json={
                    "from_contribution_id": first["id"],
                    "to_contribution_id": first["id"],
                    "relation_type": "SUPPORTS",
                },
            )
            assert refused.status_code == 422
            seen = (await client.get(f"{base}/converge/map")).json()
            assert seen["relations"] == []


async def test_cross_space_pair_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base_a, _, _, first_a, _ = await _two_contributions(session, url, ids)
        space_b = await _open_space(session, ids["workspace_id"], ids["owner_id"], "Another?")
        base_b = f"/workspaces/{ids['workspace_id']}/decision-spaces/{space_b.id}"
        async with _client(session, url, str(ids["owner_id"])) as client:
            branch_b = (
                await client.post(
                    f"{base_b}/branches",
                    json={"title": "Elsewhere", "visibility": "shared"},
                )
            ).json()
            only_b = (
                await client.post(
                    f"{base_b}/contributions",
                    json={"branch_id": branch_b["id"], "kind": "idea", "title": "Away"},
                )
            ).json()

            refused = await client.post(
                f"{base_a}/relations",
                json={
                    "from_contribution_id": first_a["id"],
                    "to_contribution_id": only_b["id"],
                    "relation_type": "SUPPORTS",
                },
            )
            assert refused.status_code == 404
            seen = (await client.get(f"{base_a}/converge/map")).json()
            assert seen["relations"] == []


async def test_duplicate_pair_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            payload = {
                "from_contribution_id": first["id"],
                "to_contribution_id": second["id"],
                "relation_type": "SUPPORTS",
            }
            assert (await client.post(f"{base}/relations", json=payload)).status_code == 201
            refused = await client.post(f"{base}/relations", json=payload)
            assert refused.status_code == 422
            seen = (await client.get(f"{base}/converge/map")).json()
            assert len(seen["relations"]) == 1


async def test_uninvolved_member_cannot_write(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["uninvolved_id"])) as client:
            assert (
                await client.post(
                    f"{base}/relations",
                    json={
                        "from_contribution_id": first["id"],
                        "to_contribution_id": second["id"],
                        "relation_type": "SUPPORTS",
                    },
                )
            ).status_code == 403
            assert (
                await client.post(f"{base}/clusters", json={"title": "Nope"})
            ).status_code == 403


async def test_relation_removed(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = (
                await client.post(
                    f"{base}/relations",
                    json={
                        "from_contribution_id": first["id"],
                        "to_contribution_id": second["id"],
                        "relation_type": "DUPLICATES",
                    },
                )
            ).json()
            deleted = await client.delete(f"{base}/relations/{created['id']}")
            assert deleted.status_code == 204
            seen = (await client.get(f"{base}/converge/map")).json()
            assert seen["relations"] == []
            assert {c["id"] for c in seen["contributions"]} == {first["id"], second["id"]}


async def test_unknown_relation_removal_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            assert (await client.delete(f"{base}/relations/{uuid4()}")).status_code == 404


async def test_cluster_lifecycle(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(f"{base}/clusters", json={"title": "Theme"})
            assert created.status_code == 201
            assert created.json()["member_ids"] == []
            seen = (await client.get(f"{base}/converge/map")).json()
            assert [c["title"] for c in seen["clusters"]] == ["Theme"]


async def test_blank_cluster_title_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            for title in ("", "   "):
                assert (
                    await client.post(f"{base}/clusters", json={"title": title})
                ).status_code == 422
            seen = (await client.get(f"{base}/converge/map")).json()
            assert seen["clusters"] == []


async def test_member_assigned_and_moved(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            one = (await client.post(f"{base}/clusters", json={"title": "One"})).json()
            two = (await client.post(f"{base}/clusters", json={"title": "Two"})).json()

            assigned = await client.post(
                f"{base}/clusters/{one['id']}/members",
                json={"contribution_id": first["id"]},
            )
            assert assigned.status_code == 200
            assert assigned.json()["member_ids"] == [first["id"]]

            moved = await client.post(
                f"{base}/clusters/{two['id']}/members",
                json={"contribution_id": first["id"]},
            )
            assert moved.json()["member_ids"] == [first["id"]]
            seen = (await client.get(f"{base}/converge/map")).json()
            by_id = {c["id"]: c for c in seen["clusters"]}
            assert by_id[one["id"]]["member_ids"] == []
            assert by_id[two["id"]]["member_ids"] == [first["id"]]


async def test_member_unassigned(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            cluster = (await client.post(f"{base}/clusters", json={"title": "Theme"})).json()
            await client.post(
                f"{base}/clusters/{cluster['id']}/members",
                json={"contribution_id": first["id"]},
            )
            removed = await client.delete(f"{base}/clusters/{cluster['id']}/members/{first['id']}")
            assert removed.status_code == 200
            assert removed.json()["member_ids"] == []
            seen = (await client.get(f"{base}/converge/map")).json()
            assert {c["id"] for c in seen["contributions"]} == {first["id"], second["id"]}


async def test_cluster_deleted_members_kept(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            cluster = (await client.post(f"{base}/clusters", json={"title": "Theme"})).json()
            await client.post(
                f"{base}/clusters/{cluster['id']}/members",
                json={"contribution_id": first["id"]},
            )
            deleted = await client.delete(f"{base}/clusters/{cluster['id']}")
            assert deleted.status_code == 204
            seen = (await client.get(f"{base}/converge/map")).json()
            assert seen["clusters"] == []
            assert {c["id"] for c in seen["contributions"]} == {first["id"], second["id"]}
            assert all(c["cluster_id"] is None for c in seen["contributions"])


async def test_foreign_member_refused(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        other = await _open_space(session, ids["workspace_id"], ids["owner_id"], "Another?")
        other_base = f"/workspaces/{ids['workspace_id']}/decision-spaces/{other.id}"
        async with _client(session, url, str(ids["owner_id"])) as client:
            cluster = (await client.post(f"{base}/clusters", json={"title": "Theme"})).json()
            other_branch = (
                await client.post(
                    f"{other_base}/branches",
                    json={"title": "Elsewhere", "visibility": "shared"},
                )
            ).json()
            foreign = (
                await client.post(
                    f"{other_base}/contributions",
                    json={
                        "branch_id": other_branch["id"],
                        "kind": "idea",
                        "title": "Away",
                    },
                )
            ).json()
            refused = await client.post(
                f"{base}/clusters/{cluster['id']}/members",
                json={"contribution_id": foreign["id"]},
            )
            assert refused.status_code == 404


async def test_maps_stay_inside_their_space(converge_database):
    engine, url = converge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        base, space, branch, first, second = await _two_contributions(session, url, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            wrong_workspace = await client.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}/converge/map"
            )
            assert wrong_workspace.status_code == 404
