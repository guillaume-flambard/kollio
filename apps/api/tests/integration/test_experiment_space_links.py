import os
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.experiments.adapters.postgres import Learning
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.options.adapters.postgres import PostgresOptions
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def link_database():
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


def _client(session, url, subject: str | None):
    app = create_app(Settings(_env_file=None, database_url=url))
    if subject is not None:
        app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def _seed(session):
    workspace_id, other_workspace_id = uuid4(), uuid4()
    owner_id, member_id, outsider_id = (uuid4() for _ in range(3))
    idea_id = uuid4()
    session.add_all(
        [
            Workspace(id=workspace_id, name="Link workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=member_id, auth_subject=str(member_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="admin"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=member_id, role="member"),
            WorkspaceMembership(
                workspace_id=other_workspace_id, user_id=outsider_id, role="member"
            ),
        ]
    )
    await session.flush()

    session.add(
        Idea(
            id=idea_id,
            slug=f"link-idea-{idea_id.hex[:8]}",
            title="Offline first field app",
            pitch="Works without signal",
            owner_id=owner_id,
            workspace_id=workspace_id,
            stage="seed",
            lang="en",
            visibility="workspace",
        )
    )
    await session.flush()

    spaces = PostgresDecisionSpaces(session)
    space = await spaces.create(
        workspace_id=workspace_id,
        question="Should we build offline first?",
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )
    other_space = await spaces.create(
        workspace_id=workspace_id,
        question="A sibling space",
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )
    foreign_space = await spaces.create(
        workspace_id=other_workspace_id,
        question="Another workspace's space",
        description=None,
        deadline=None,
        owner_id=outsider_id,
        lang="en",
    )

    options = PostgresOptions(session)
    option = await options.create_option(
        space_id=space.id,
        title="Ship offline first",
        proposal="Build the offline layer before the sync layer.",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )
    foreign_option = await options.create_option(
        space_id=other_space.id,
        title="A sibling option",
        proposal="Belongs to the sibling space.",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )
    await session.flush()

    return {
        "workspace_id": workspace_id,
        "other_workspace_id": other_workspace_id,
        "owner_id": owner_id,
        "member_id": member_id,
        "outsider_id": outsider_id,
        "idea_id": idea_id,
        "space_id": space.id,
        "other_space_id": other_space.id,
        "foreign_space_id": foreign_space.id,
        "option_id": option.id,
        "foreign_option_id": foreign_option.id,
    }


def _body(title: str, **overrides):
    payload = {
        "title": title,
        "hypothesis": "Offline first reduces drop-off.",
        "success_metric": "completion rate",
    }
    payload.update(overrides)
    return payload


def _space_base(ids):
    return f"/workspaces/{ids['workspace_id']}/decision-spaces/{ids['space_id']}"


async def test_linking_a_space_makes_the_experiment_visible_to_the_space(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Offline pilot", decision_space_id=str(ids["space_id"])),
            )
            assert created.status_code == 201
            assert created.json()["decision_space_id"] == str(ids["space_id"])
            assert created.json()["option_id"] is None

            listed = await client.get(f"{_space_base(ids)}/experiments")
            assert listed.status_code == 200
            titles = [item["title"] for item in listed.json()]
            assert titles == ["Offline pilot"]


async def test_linking_an_option_of_the_space(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body(
                    "Option pilot",
                    decision_space_id=str(ids["space_id"]),
                    option_id=str(ids["option_id"]),
                ),
            )
            assert created.status_code == 201
            assert created.json()["option_id"] == str(ids["option_id"])

            listed = await client.get(f"{_space_base(ids)}/experiments")
            assert [item["option_id"] for item in listed.json()] == [str(ids["option_id"])]


async def test_an_unlinked_experiment_stays_out_of_the_space(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"/ideas/{ids['idea_id']}/experiments", json=_body("Free experiment")
            )
            assert created.status_code == 201
            assert created.json()["decision_space_id"] is None

            listed = await client.get(f"{_space_base(ids)}/experiments")
            assert listed.status_code == 200
            assert listed.json() == []

            by_idea = await client.get(f"/ideas/{ids['idea_id']}/experiments")
            assert by_idea.status_code == 200
            assert [item["title"] for item in by_idea.json()] == ["Free experiment"]


async def test_learnings_are_read_through_the_linked_experiment(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Learning pilot", decision_space_id=str(ids["space_id"])),
            )
            experiment_id = created.json()["id"]
            session.add(
                Learning(
                    id=uuid4(),
                    experiment_id=experiment_id,
                    idea_id=ids["idea_id"],
                    status="confirmed",
                    text="Offline first pays for itself below two bars of signal.",
                    confirmed_by_id=ids["owner_id"],
                )
            )
            await session.flush()

            listed = await client.get(f"{_space_base(ids)}/learnings")
            assert listed.status_code == 200
            learnings = listed.json()
            assert len(learnings) == 1
            assert learnings[0]["experiment_id"] == experiment_id
            assert learnings[0]["status"] == "confirmed"

            unlinked = await client.get(f"{_space_base(ids)}/learnings")
            assert len(unlinked.json()) == 1


async def test_unknown_space_refused(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Nowhere", decision_space_id=str(uuid4())),
            )
            assert refused.status_code == 422

            listed = await client.get(f"/ideas/{ids['idea_id']}/experiments")
            assert listed.json() == []


async def test_space_of_another_workspace_refused(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Foreign", decision_space_id=str(ids["foreign_space_id"])),
            )
            assert refused.status_code == 422


async def test_option_of_another_space_refused(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body(
                    "Wrong option",
                    decision_space_id=str(ids["space_id"]),
                    option_id=str(ids["foreign_option_id"]),
                ),
            )
            assert refused.status_code == 422


async def test_option_without_a_space_refused(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Orphan option", option_id=str(ids["option_id"])),
            )
            assert refused.status_code == 422


async def test_a_non_member_sees_no_space_experiments(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Owner pilot", decision_space_id=str(ids["space_id"])),
            )

        async with _client(session, url, str(ids["outsider_id"])) as outsider:
            denied = await outsider.get(f"{_space_base(ids)}/experiments")
            assert denied.status_code == 404
            denied = await outsider.get(f"{_space_base(ids)}/learnings")
            assert denied.status_code == 404


async def test_spaces_stay_inside_their_workspaces(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["outsider_id"])) as outsider:
            denied = await outsider.get(
                f"/workspaces/{ids['other_workspace_id']}"
                f"/decision-spaces/{ids['space_id']}/experiments"
            )
            assert denied.status_code == 404


async def test_a_member_reads_the_space_experiments(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, str(ids["owner_id"])) as client:
            await client.post(
                f"/ideas/{ids['idea_id']}/experiments",
                json=_body("Owner pilot", decision_space_id=str(ids["space_id"])),
            )

        async with _client(session, url, str(ids["member_id"])) as member:
            listed = await member.get(f"{_space_base(ids)}/experiments")
            assert listed.status_code == 200
            assert [item["title"] for item in listed.json()] == ["Owner pilot"]


async def test_unauthenticated_request_is_unauthorized(link_database):
    engine, url = link_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        async with _client(session, url, None) as anonymous:
            response = await anonymous.get(f"{_space_base(ids)}/experiments")
            assert response.status_code == 401
