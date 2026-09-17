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

FIELDS = {
    "mechanism": "Sell the workflow to three design partners first.",
    "upside": "Revenue before the roadmap grows.",
    "cost": "Two engineer-months.",
    "risks": "Partners may not convert.",
    "critical_assumptions": "Teams already pay for adjacent tools.",
    "success_metrics": "Three signed pilots in one quarter.",
}


@pytest_asyncio.fixture
async def option_database():
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
            Workspace(id=workspace_id, name="Option workspace"),
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


async def _space(session, workspace_id, owner_id, question="Which path do we commit to?"):
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


async def _branch(session, space_id, owner_id):
    return await PostgresBranches(session).create_branch(
        space_id=space_id,
        title="Explore",
        summary=None,
        visibility="shared",
        created_by=owner_id,
        source_idea_id=None,
        lang="en",
    )


async def _contribution(session, workspace_id, space_id, subject, branch_id, *, suggestion=False):
    return await propose_contribution(
        PostgresBranches(session),
        workspace_id,
        space_id,
        subject,
        branch_id=branch_id,
        kind="claim",
        title="A claim",
        body=None,
        source=None,
        tool_model=None,
        transformation_history=None,
        as_suggestion=suggestion,
        lang="en",
    )


def _paths(workspace_id, space_id):
    return f"/workspaces/{workspace_id}/decision-spaces/{space_id}/options"


async def test_option_round_trip_with_every_field(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={
                    "title": "Design partners first",
                    "proposal": "Sell before building.",
                    **FIELDS,
                },
                headers={"Accept-Language": "fr"},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["title"] == "Design partners first"
            assert body["proposal"] == "Sell before building."
            for field, value in FIELDS.items():
                assert body[field] == value
            assert body["lang"] == "fr"
            assert body["created_by"] == str(ids["owner_id"])
            assert body["evidence"] == []

            read = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{body['id']}")
            assert read.status_code == 200
            assert read.json() == body


async def test_option_minimal_fields_read_as_absent(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Bare", "proposal": "Only the essentials."},
            )
            assert created.status_code == 201
            body = created.json()
            for field in FIELDS:
                assert body[field] is None


async def test_option_response_carries_no_score(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "No score", "proposal": "Nothing ranks this."},
            )
            keys = set(created.json())
            assert keys == {
                "id",
                "space_id",
                "title",
                "proposal",
                "mechanism",
                "upside",
                "cost",
                "risks",
                "critical_assumptions",
                "success_metrics",
                "created_by",
                "lang",
                "created_at",
                "updated_at",
                "evidence",
            }


async def test_blank_title_and_proposal_refused(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            for payload in (
                {"title": "", "proposal": "Fine"},
                {"title": "  ", "proposal": "Fine"},
                {"title": "Fine", "proposal": ""},
                {"title": "Fine", "proposal": "   "},
            ):
                refused = await client.post(_paths(ids["workspace_id"], space.id), json=payload)
                assert refused.status_code == 422, payload

            listed = await client.get(_paths(ids["workspace_id"], space.id))
            assert listed.json()["items"] == []


async def test_option_update(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "First", "proposal": "Start here."},
            )
            option_id = created.json()["id"]

            updated = await client.patch(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}",
                json={"title": "Second", "cost": "One week.", "upside": None},
                headers={"Accept-Language": "fr"},
            )
            assert updated.status_code == 200
            body = updated.json()
            assert body["title"] == "Second"
            assert body["cost"] == "One week."
            assert body["proposal"] == "Start here."
            assert body["lang"] == "fr"

            read = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert read.json() == body


async def test_option_delete(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Doomed", "proposal": "Remove me."},
            )
            option_id = created.json()["id"]

            removed = await client.delete(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert removed.status_code == 204

            gone = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert gone.status_code == 404
            listed = await client.get(_paths(ids["workspace_id"], space.id))
            assert listed.json()["items"] == []


async def test_evidence_link_round_trip(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        branch = await _branch(session, space.id, ids["owner_id"])
        supporting = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), branch.id
        )
        contradicting = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), branch.id
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Linked", "proposal": "With evidence."},
            )
            option_id = created.json()["id"]

            linked = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(supporting.id), "side": "for"},
            )
            assert linked.status_code == 201
            assert linked.json()["evidence"] == [
                {
                    "contribution_id": str(supporting.id),
                    "side": "for",
                    "created_at": linked.json()["evidence"][0]["created_at"],
                }
            ]

            second = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(contradicting.id), "side": "against"},
            )
            assert second.status_code == 201
            sides = {link["contribution_id"]: link["side"] for link in second.json()["evidence"]}
            assert sides == {
                str(supporting.id): "for",
                str(contradicting.id): "against",
            }

            read = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert len(read.json()["evidence"]) == 2


async def test_suggested_contribution_cannot_be_linked(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        branch = await _branch(session, space.id, ids["owner_id"])
        suggestion = await _contribution(
            session,
            ids["workspace_id"],
            space.id,
            str(ids["owner_id"]),
            branch.id,
            suggestion=True,
        )
        assert suggestion.status == "suggested"
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Strict", "proposal": "Only confirmed evidence."},
            )
            option_id = created.json()["id"]
            refused = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(suggestion.id), "side": "for"},
            )
            assert refused.status_code == 422

            read = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert read.json()["evidence"] == []


async def test_foreign_contribution_cannot_be_linked(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        home = await _space(session, ids["workspace_id"], ids["owner_id"], "Home?")
        elsewhere = await _space(session, ids["workspace_id"], ids["owner_id"], "Elsewhere?")
        branch = await _branch(session, elsewhere.id, ids["owner_id"])
        foreign = await _contribution(
            session, ids["workspace_id"], elsewhere.id, str(ids["owner_id"]), branch.id
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], home.id),
                json={"title": "Scoped", "proposal": "Evidence must be local."},
            )
            option_id = created.json()["id"]
            refused = await client.post(
                f"{_paths(ids['workspace_id'], home.id)}/{option_id}/evidence",
                json={"contribution_id": str(foreign.id), "side": "for"},
            )
            assert refused.status_code == 422


async def test_unknown_side_refused(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        branch = await _branch(session, space.id, ids["owner_id"])
        contribution = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), branch.id
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Sides", "proposal": "Two sides only."},
            )
            option_id = created.json()["id"]
            refused = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(contribution.id), "side": "support"},
            )
            assert refused.status_code == 422


async def test_duplicate_link_refused(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        branch = await _branch(session, space.id, ids["owner_id"])
        contribution = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), branch.id
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Once", "proposal": "One link per contribution."},
            )
            option_id = created.json()["id"]
            first = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(contribution.id), "side": "for"},
            )
            assert first.status_code == 201
            second = await client.post(
                f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence",
                json={"contribution_id": str(contribution.id), "side": "against"},
            )
            assert second.status_code == 422

            read = await client.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert len(read.json()["evidence"]) == 1
            assert read.json()["evidence"][0]["side"] == "for"


async def test_evidence_unlink(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        branch = await _branch(session, space.id, ids["owner_id"])
        contribution = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), branch.id
        )
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Unlink", "proposal": "Links come and go."},
            )
            option_id = created.json()["id"]
            base = f"{_paths(ids['workspace_id'], space.id)}/{option_id}/evidence"
            await client.post(base, json={"contribution_id": str(contribution.id), "side": "for"})

            unlinked = await client.delete(f"{base}/{contribution.id}")
            assert unlinked.status_code == 200
            assert unlinked.json()["evidence"] == []

            again = await client.delete(f"{base}/{contribution.id}")
            assert again.status_code == 422

            contributions = await client.get(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{space.id}/contributions"
            )
            assert len(contributions.json()["items"]) == 1


async def test_options_stay_inside_their_space(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        first = await _space(session, ids["workspace_id"], ids["owner_id"], "First?")
        second = await _space(session, ids["workspace_id"], ids["owner_id"], "Second?")
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], first.id),
                json={"title": "Only here", "proposal": "Belongs to the first space."},
            )
            option_id = created.json()["id"]

            other = await client.get(f"{_paths(ids['workspace_id'], second.id)}/{option_id}")
            assert other.status_code == 404
            listed = await client.get(_paths(ids["workspace_id"], second.id))
            assert listed.json()["items"] == []
            patched = await client.patch(
                f"{_paths(ids['workspace_id'], second.id)}/{option_id}", json={"title": "Nope"}
            )
            assert patched.status_code == 404


async def test_no_leak_across_workspaces(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Private", "proposal": "Not for other workspaces."},
            )
            option_id = created.json()["id"]

        async with _client(session, url, str(ids["outsider_id"])) as other:
            denied = await other.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}"
                f"/options/{option_id}"
            )
            assert denied.status_code == 404


async def test_uninvolved_member_cannot_write(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as owner:
            created = await owner.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Guarded", "proposal": "Owners and participants only."},
            )
            option_id = created.json()["id"]

        async with _client(session, url, str(ids["uninvolved_id"])) as member:
            assert (
                await member.post(
                    _paths(ids["workspace_id"], space.id),
                    json={"title": "Nope", "proposal": "Nope."},
                )
            ).status_code == 403
            assert (
                await member.patch(
                    f"{_paths(ids['workspace_id'], space.id)}/{option_id}",
                    json={"title": "Nope"},
                )
            ).status_code == 403
            assert (
                await member.delete(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            ).status_code == 403

        async with _client(session, url, str(ids["owner_id"])) as owner:
            read = await owner.get(f"{_paths(ids['workspace_id'], space.id)}/{option_id}")
            assert read.json()["title"] == "Guarded"


async def test_participant_can_write(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await PostgresDecisionSpaces(session).add_participant(space.id, ids["participant_id"])
        async with _client(session, url, str(ids["participant_id"])) as client:
            created = await client.post(
                _paths(ids["workspace_id"], space.id),
                json={"title": "Participant option", "proposal": "A participant wrote this."},
            )
            assert created.status_code == 201


async def test_non_member_is_refused_everywhere(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        base = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (await client.get(base)).status_code == 404
            assert (await client.get(f"{base}/{uuid4()}")).status_code == 404
            assert (
                await client.post(base, json={"title": "Nope", "proposal": "Nope."})
            ).status_code == 404
            assert (
                await client.patch(f"{base}/{uuid4()}", json={"title": "Nope"})
            ).status_code == 404
            assert (await client.delete(f"{base}/{uuid4()}")).status_code == 404
            assert (
                await client.post(
                    f"{base}/{uuid4()}/evidence",
                    json={"contribution_id": str(uuid4()), "side": "for"},
                )
            ).status_code == 404


async def test_unauthenticated_request_is_unauthorized(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, None) as client:
            response = await client.get(_paths(ids["workspace_id"], space.id))
            assert response.status_code == 401


async def test_list_returns_only_this_space(option_database):
    engine, url = option_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        first = await _space(session, ids["workspace_id"], ids["owner_id"], "First?")
        second = await _space(session, ids["workspace_id"], ids["owner_id"], "Second?")
        async with _client(session, url, str(ids["owner_id"])) as client:
            for title, space_id in (("One", first.id), ("Two", first.id), ("Three", second.id)):
                await client.post(
                    _paths(ids["workspace_id"], space_id),
                    json={"title": title, "proposal": "A path."},
                )
            first_list = await client.get(_paths(ids["workspace_id"], first.id))
            second_list = await client.get(_paths(ids["workspace_id"], second.id))
            assert {item["title"] for item in first_list.json()["items"]} == {"One", "Two"}
            assert [item["title"] for item in second_list.json()["items"]] == ["Three"]
