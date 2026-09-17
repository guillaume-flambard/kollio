import contextlib
import os
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration

FORWARD_CHAIN = (
    "EXPLORING",
    "CONVERGING",
    "READY_TO_DECIDE",
    "DECIDED",
    "TESTING",
    "LEARNED",
)


@pytest_asyncio.fixture
async def space_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


@contextlib.asynccontextmanager
async def _database(engine):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        try:
            async with local() as session:
                yield session
        finally:
            await transaction.rollback()


async def _seed(session: AsyncSession) -> dict[str, UUID]:
    workspace_id, other_workspace_id = uuid4(), uuid4()
    owner_id, participant_id, uninvolved_id, outsider_id = (uuid4() for _ in range(4))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Decision workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=participant_id, auth_subject=str(participant_id), display_name="Participant"),
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
        "workspace": workspace_id,
        "other_workspace": other_workspace_id,
        "owner": owner_id,
        "participant": participant_id,
        "uninvolved": uninvolved_id,
        "outsider": outsider_id,
    }


def _client(session: AsyncSession, url: str, subject: str | None):
    app = create_app(Settings(_env_file=None, database_url=url))
    if subject is not None:
        app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


def _base(workspace_id: UUID) -> str:
    return f"/workspaces/{workspace_id}/decision-spaces"


async def _open(client: httpx.AsyncClient, workspace_id: UUID, question: str = "Launch?"):
    return await client.post(_base(workspace_id), json={"question": question})


async def _advance(
    client: httpx.AsyncClient,
    workspace_id: UUID,
    space_id: str,
    to_status: str,
    reason: str | None = None,
):
    return await client.post(
        f"{_base(workspace_id)}/{space_id}/transitions",
        json={"to_status": to_status, "reason": reason},
    )


async def _walk_to(
    client: httpx.AsyncClient, workspace_id: UUID, space_id: str, target: str
) -> None:
    for status in FORWARD_CHAIN:
        response = await _advance(client, workspace_id, space_id, status)
        assert response.status_code == 200, response.text
        if status == target:
            return
    raise AssertionError(f"{target} is not on the declared forward chain")


async def test_member_reads_space(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            opened = await _open(client, ids["workspace"], "Do we enter Germany?")
            space_id = opened.json()["id"]
        async with _client(session, url, str(ids["participant"])) as client:
            response = await client.get(
                f"{_base(ids['workspace'])}/{space_id}", headers={"Accept-Language": "en"}
            )
        assert response.status_code == 200
        assert response.headers["Content-Language"] == "en"
        body = response.json()
        assert body["question"] == "Do we enter Germany?"
        assert body["owner_id"] == str(ids["owner"])
        assert body["status"] == "OPEN"
        assert [participant["user_id"] for participant in body["participants"]] == [
            str(ids["owner"])
        ]
        assert [event["to_status"] for event in body["history"]] == ["OPEN"]


async def test_non_member_is_refused_everywhere(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        owner_client = _client(session, url, str(ids["owner"]))
        async with owner_client as client:
            opened = await _open(client, ids["workspace"])
            space_id = opened.json()["id"]
        async with _client(session, url, str(ids["outsider"])) as client:
            base = _base(ids["workspace"])
            assert (await client.get(base)).status_code == 404
            assert (await _open(client, ids["workspace"])).status_code == 404
            assert (await client.get(f"{base}/{space_id}")).status_code == 404
            assert (
                await _advance(client, ids["workspace"], space_id, "EXPLORING")
            ).status_code == 404
            assert (
                await client.post(
                    f"{base}/{space_id}/participants", json={"user_id": str(ids["outsider"])}
                )
            ).status_code == 404
            assert (
                await client.delete(f"{base}/{space_id}/participants/{ids['outsider']}")
            ).status_code == 404


async def test_unauthenticated_request_is_unauthorized(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, None) as client:
            response = await client.get(_base(ids["workspace"]))
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_spaces_stay_inside_their_workspace(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            opened = await _open(client, ids["workspace"])
            space_id = opened.json()["id"]
        async with _client(session, url, str(ids["outsider"])) as client:
            assert (
                await client.get(f"{_base(ids['other_workspace'])}/{space_id}")
            ).status_code == 404
        async with _client(session, url, str(ids["outsider"])) as client:
            assert (
                await client.get(f"{_base(ids['other_workspace'])}/{space_id}")
            ).status_code == 404


async def test_open_round_trip(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            french = await _open(client, ids["workspace"], "Faut-il lever des fonds ?")
            assert french.status_code == 201
            body = french.json()
            assert body["status"] == "OPEN"
            assert body["lang"] == "fr"
            assert body["workspace_id"] == str(ids["workspace"])
            assert body["owner_id"] == str(ids["owner"])
            assert body["deadline"] is None

            english = await client.post(
                _base(ids["workspace"]),
                json={"question": "Should we raise?"},
                headers={"Accept-Language": "en"},
            )
            assert english.json()["lang"] == "en"

            detail = await client.get(f"{_base(ids['workspace'])}/{body['id']}")
        history = detail.json()["history"]
        assert [event["to_status"] for event in history] == ["OPEN"]
        assert history[0]["from_status"] is None
        assert history[0]["actor_id"] == str(ids["owner"])
        assert history[0]["created_at"]


async def test_empty_question_refused(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            assert (await _open(client, ids["workspace"], "")).status_code == 422
            assert (await _open(client, ids["workspace"], "   ")).status_code == 422
            listed = await client.get(_base(ids["workspace"]))
        assert listed.json()["items"] == []


async def test_open_with_description_and_deadline(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            response = await client.post(
                _base(ids["workspace"]),
                json={
                    "question": "Should we reprice?",
                    "description": "Margin is falling",
                    "deadline": "2026-10-01",
                },
            )
        assert response.status_code == 201
        body = response.json()
        assert body["description"] == "Margin is falling"
        assert body["deadline"] == "2026-10-01"


async def test_declared_chain_walked_end_to_end(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            statuses = []
            for target in FORWARD_CHAIN:
                response = await _advance(client, ids["workspace"], space_id, target)
                assert response.status_code == 200, response.text
                statuses.append(response.json()["status"])
        assert statuses == list(FORWARD_CHAIN)
        assert statuses[-1] == "LEARNED"


async def test_undeclared_transition_refused(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            skipped = await _advance(client, ids["workspace"], space_id, "DECIDED")
            assert skipped.status_code == 422
            for candidate in ("OPEN", "EXPLORING", "CONVERGING", "READY_TO_DECIDE"):
                refused = await _advance(client, ids["workspace"], space_id, "REOPENED", "back")
                assert refused.status_code == 422, candidate
            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        body = detail.json()
        assert body["status"] == "OPEN"
        assert [event["to_status"] for event in body["history"]] == ["OPEN"]


async def test_unknown_status_refused(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            response = await _advance(client, ids["workspace"], space_id, "ARCHIVED")
            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        assert response.status_code == 422
        assert detail.json()["status"] == "OPEN"
        assert len(detail.json()["history"]) == 1


async def test_reopen_requires_reason(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            await _walk_to(client, ids["workspace"], space_id, "DECIDED")

            assert (
                await _advance(client, ids["workspace"], space_id, "REOPENED")
            ).status_code == 422
            assert (
                await _advance(client, ids["workspace"], space_id, "REOPENED", "   ")
            ).status_code == 422
            still_decided = await client.get(f"{_base(ids['workspace'])}/{space_id}")
            assert still_decided.json()["status"] == "DECIDED"

            reopened = await _advance(
                client, ids["workspace"], space_id, "REOPENED", "New pricing evidence"
            )
            assert reopened.status_code == 200
            assert reopened.json()["status"] == "REOPENED"
            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        history = detail.json()["history"]
        assert history[-1]["reason"] == "New pricing evidence"
        assert history[-1]["from_status"] == "DECIDED"


async def test_reopened_space_resumes_at_exploring(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            await _walk_to(client, ids["workspace"], space_id, "LEARNED")
            await _advance(client, ids["workspace"], space_id, "REOPENED", "Outcome contradicted")
            resumed = await _advance(client, ids["workspace"], space_id, "EXPLORING")
        assert resumed.status_code == 200
        assert resumed.json()["status"] == "EXPLORING"


async def test_status_history_is_ordered_and_immutable(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            await _walk_to(client, ids["workspace"], space_id, "TESTING")
            first = await client.get(f"{_base(ids['workspace'])}/{space_id}")
            await _advance(client, ids["workspace"], space_id, "LEARNED")
            second = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        history = second.json()["history"]
        assert [event["to_status"] for event in history] == [
            "OPEN",
            *FORWARD_CHAIN,
        ]
        assert [event["from_status"] for event in history] == [
            None,
            "OPEN",
            "EXPLORING",
            "CONVERGING",
            "READY_TO_DECIDE",
            "DECIDED",
            "TESTING",
        ]
        assert all(event["created_at"] for event in history)
        assert first.json()["history"] == history[:6]


async def test_participant_lifecycle(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            base = f"{_base(ids['workspace'])}/{space_id}/participants"

            added = await client.post(base, json={"user_id": str(ids["participant"])})
            assert added.status_code == 201
            assert sorted(p["user_id"] for p in added.json()) == sorted(
                [str(ids["owner"]), str(ids["participant"])]
            )

            again = await client.post(base, json={"user_id": str(ids["participant"])})
            assert again.status_code == 201
            assert len(again.json()) == 2

            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
            assert str(ids["owner"]) in [p["user_id"] for p in detail.json()["participants"]]

            removing_owner = await client.delete(f"{base}/{ids['owner']}")
            assert removing_owner.status_code == 422

            removed = await client.delete(f"{base}/{ids['participant']}")
            assert removed.status_code == 200
            assert [p["user_id"] for p in removed.json()] == [str(ids["owner"])]


async def test_participant_must_belong_to_workspace(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            response = await client.post(
                f"{_base(ids['workspace'])}/{space_id}/participants",
                json={"user_id": str(ids["outsider"])},
            )
            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        assert response.status_code == 422
        assert [p["user_id"] for p in detail.json()["participants"]] == [str(ids["owner"])]


async def test_participant_can_transition_status(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            await client.post(
                f"{_base(ids['workspace'])}/{space_id}/participants",
                json={"user_id": str(ids["participant"])},
            )
        async with _client(session, url, str(ids["participant"])) as client:
            response = await _advance(client, ids["workspace"], space_id, "EXPLORING")
        assert response.status_code == 200
        assert response.json()["status"] == "EXPLORING"


async def test_uninvolved_member_cannot_write(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
        async with _client(session, url, str(ids["uninvolved"])) as client:
            refused = await _advance(client, ids["workspace"], space_id, "EXPLORING")
            assert refused.status_code == 403
            assert (
                await client.post(
                    f"{_base(ids['workspace'])}/{space_id}/participants",
                    json={"user_id": str(ids["uninvolved"])},
                )
            ).status_code == 403
            detail = await client.get(f"{_base(ids['workspace'])}/{space_id}")
        assert detail.status_code == 200
        assert detail.json()["status"] == "OPEN"
        assert len(detail.json()["history"]) == 1


async def test_only_owner_manages_participants(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            space_id = (await _open(client, ids["workspace"])).json()["id"]
            await client.post(
                f"{_base(ids['workspace'])}/{space_id}/participants",
                json={"user_id": str(ids["participant"])},
            )
        async with _client(session, url, str(ids["participant"])) as client:
            response = await client.post(
                f"{_base(ids['workspace'])}/{space_id}/participants",
                json={"user_id": str(ids["uninvolved"])},
            )
        assert response.status_code == 403


async def test_list_returns_only_this_workspace(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            await _open(client, ids["workspace"], "First?")
            await _open(client, ids["workspace"], "Second?")
            listed = await client.get(_base(ids["workspace"]))
        async with _client(session, url, str(ids["outsider"])) as client:
            elsewhere = await _open(client, ids["other_workspace"], "Other?")
        assert listed.status_code == 200
        assert sorted(item["question"] for item in listed.json()["items"]) == [
            "First?",
            "Second?",
        ]
        assert len(listed.json()["items"]) == 2
        assert listed.json()["items"][0]["id"] != elsewhere.json()["id"]


async def test_list_is_empty_not_an_error(space_database):
    engine, url = space_database
    async with _database(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner"])) as client:
            response = await client.get(_base(ids["workspace"]))
        assert response.status_code == 200
        assert response.json() == {"items": []}
