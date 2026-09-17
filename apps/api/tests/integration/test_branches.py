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
from src.modules.branches.service.mapping import MappingNotFoundError, map_idea
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def branch_database():
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
            Workspace(id=workspace_id, name="Branch workspace"),
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
    spaces = PostgresDecisionSpaces(session)
    space = await spaces.create(
        workspace_id=workspace_id,
        question=question,
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )
    await session.flush()
    return space


async def _insert_idea(session, workspace_id, owner_id, title="A seeded idea", public=False):
    idea = Idea(
        id=uuid4(),
        slug=f"idea-{uuid4().hex[:8]}",
        title=title,
        pitch="A pitch worth exploring.",
        owner_id=owner_id,
        workspace_id=None if public else workspace_id,
        stage="seed",
        initiative_type="idea",
        lang="en",
        visibility="public" if public else "workspace",
    )
    session.add(idea)
    await session.flush()
    return idea


def _space_paths(workspace_id, space_id):
    base = f"/workspaces/{workspace_id}/decision-spaces/{space_id}"
    return base


async def test_shared_branch_round_trip(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                f"{base}/branches",
                json={"title": "Explore pricing", "visibility": "shared"},
                headers={"Accept-Language": "fr"},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["title"] == "Explore pricing"
            assert body["visibility"] == "shared"
            assert body["space_id"] == str(space.id)
            assert body["lang"] == "fr"

            read = await client.get(f"{base}/branches/{body['id']}")
            assert read.status_code == 200
            assert read.json() == body


async def test_private_branch_hidden_from_other_members(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as owner:
            created = await owner.post(
                f"{base}/branches",
                json={"title": "My private notes", "visibility": "private"},
            )
            assert created.status_code == 201
            branch_id = created.json()["id"]

            read = await owner.get(f"{base}/branches/{branch_id}")
            assert read.status_code == 200

        async with _client(session, url, str(ids["participant_id"])) as member:
            denied = await member.get(f"{base}/branches/{branch_id}")
            assert denied.status_code == 404


async def test_blank_branch_title_refused(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            for title in ("", "   "):
                refused = await client.post(
                    f"{base}/branches",
                    json={"title": title, "visibility": "shared"},
                )
                assert refused.status_code == 422

            listed = await client.get(f"{base}/branches")
            assert listed.status_code == 200
            assert listed.json()["items"] == []


async def test_branches_listed_per_space(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        first = await _open_space(session, ids["workspace_id"], ids["owner_id"], "First?")
        second = await _open_space(session, ids["workspace_id"], ids["owner_id"], "Second?")
        async with _client(session, url, str(ids["owner_id"])) as client:
            for title in ("Branch one", "Branch two"):
                response = await client.post(
                    f"/workspaces/{ids['workspace_id']}/decision-spaces/{first.id}/branches",
                    json={"title": title, "visibility": "shared"},
                )
                assert response.status_code == 201
            response = await client.post(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{second.id}/branches",
                json={"title": "Elsewhere", "visibility": "shared"},
            )
            assert response.status_code == 201

            listed = await client.get(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{first.id}/branches"
            )
            assert {item["title"] for item in listed.json()["items"]} == {
                "Branch one",
                "Branch two",
            }
            listed = await client.get(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{second.id}/branches"
            )
            assert [item["title"] for item in listed.json()["items"]] == ["Elsewhere"]


async def test_workspace_idea_mapped_to_branch(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        idea = await _insert_idea(session, ids["workspace_id"], ids["owner_id"])
        branch, created = await map_idea(
            PostgresBranches(session),
            PostgresDecisionSpaces(session),
            ids["workspace_id"],
            idea.id,
            str(ids["owner_id"]),
        )
        assert created is True
        assert branch.title == idea.title
        assert branch.summary == idea.pitch
        assert branch.source_idea_id == idea.id
        assert branch.visibility == "shared"
        assert branch.lang == "en"

        spaces = PostgresDecisionSpaces(session)
        space = await spaces.space(ids["workspace_id"], branch.space_id)
        assert space is not None
        assert space.question == idea.title
        assert space.owner_id == ids["owner_id"]
        assert space.workspace_id == ids["workspace_id"]


async def test_mapping_skips_already_mapped_idea(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        idea = await _insert_idea(session, ids["workspace_id"], ids["owner_id"])
        branches = PostgresBranches(session)
        spaces = PostgresDecisionSpaces(session)
        first, created = await map_idea(
            branches, spaces, ids["workspace_id"], idea.id, str(ids["owner_id"])
        )
        assert created is True
        second, created = await map_idea(
            branches, spaces, ids["workspace_id"], idea.id, str(ids["owner_id"])
        )
        assert created is False
        assert second.id == first.id


async def test_public_idea_not_mapped(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        idea = await _insert_idea(session, ids["workspace_id"], ids["owner_id"], public=True)
        with pytest.raises(MappingNotFoundError):
            await map_idea(
                PostgresBranches(session),
                PostgresDecisionSpaces(session),
                ids["workspace_id"],
                idea.id,
                str(ids["owner_id"]),
            )
        assert await PostgresBranches(session).branch_for_idea(idea.id) is None


async def test_mapped_idea_still_reads_as_before(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        idea = await _insert_idea(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            before = await client.get(f"/ideas/{idea.id}")
            assert before.status_code == 200

            await map_idea(
                PostgresBranches(session),
                PostgresDecisionSpaces(session),
                ids["workspace_id"],
                idea.id,
                str(ids["owner_id"]),
            )

            after = await client.get(f"/ideas/{idea.id}")
            assert after.status_code == 200
            assert after.json() == before.json()


async def test_human_proposal_confirmed_with_provenance(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            branch = await client.post(
                f"{base}/branches",
                json={"title": "Explore", "visibility": "shared"},
            )
            branch_id = branch.json()["id"]

            proposed = await client.post(
                f"{base}/contributions",
                json={
                    "branch_id": branch_id,
                    "kind": "claim",
                    "title": "Teams pay for memory",
                    "body": "Selected from the branch notes.",
                    "source": "https://example.test/memory",
                    "tool_model": "claude/test",
                    "transformation_history": {"selected": "two paragraphs"},
                },
            )
            assert proposed.status_code == 201
            body = proposed.json()
            assert body["status"] == "confirmed"
            assert body["author_id"] == str(ids["owner_id"])
            assert body["kind"] == "claim"
            assert body["source"] == "https://example.test/memory"
            assert body["tool_model"] == "claude/test"
            assert body["transformation_history"] == {"selected": "two paragraphs"}


async def test_ai_suggestion_not_canonical_until_confirmed(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        branches = PostgresBranches(session)
        branch = await branches.create_branch(
            space_id=space.id,
            title="Explore",
            summary=None,
            visibility="shared",
            created_by=ids["owner_id"],
            source_idea_id=None,
            lang="en",
        )
        suggestion = await propose_contribution(
            branches,
            ids["workspace_id"],
            space.id,
            str(ids["owner_id"]),
            branch_id=branch.id,
            kind="evidence",
            title="A suggested signal",
            body=None,
            source=None,
            tool_model="model/test",
            transformation_history=None,
            as_suggestion=True,
            lang="en",
        )
        assert suggestion.status == "suggested"


async def test_confirmation_flips_status_and_author(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        spaces = PostgresDecisionSpaces(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        await spaces.add_participant(space.id, ids["participant_id"])
        branches = PostgresBranches(session)
        branch = await branches.create_branch(
            space_id=space.id,
            title="Explore",
            summary=None,
            visibility="shared",
            created_by=ids["owner_id"],
            source_idea_id=None,
            lang="en",
        )
        suggestion = await propose_contribution(
            branches,
            ids["workspace_id"],
            space.id,
            str(ids["owner_id"]),
            branch_id=branch.id,
            kind="objection",
            title="A suggested objection",
            body=None,
            source=None,
            tool_model=None,
            transformation_history=None,
            as_suggestion=True,
            lang="en",
        )
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["participant_id"])) as client:
            confirmed = await client.post(f"{base}/contributions/{suggestion.id}/confirmation")
            assert confirmed.status_code == 200
            body = confirmed.json()
            assert body["status"] == "confirmed"
            assert body["author_id"] == str(ids["participant_id"])


async def test_unknown_contribution_kind_refused(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            branch = await client.post(
                f"{base}/branches",
                json={"title": "Explore", "visibility": "shared"},
            )
            refused = await client.post(
                f"{base}/contributions",
                json={
                    "branch_id": branch.json()["id"],
                    "kind": "fact",
                    "title": "Not a kind",
                },
            )
            assert refused.status_code == 422

            listed = await client.get(f"{base}/contributions")
            assert listed.json()["items"] == []


async def test_proposal_from_unreadable_branch_refused(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        spaces = PostgresDecisionSpaces(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        await spaces.add_participant(space.id, ids["participant_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as owner:
            branch = await owner.post(
                f"{base}/branches",
                json={"title": "Private notes", "visibility": "private"},
            )
            branch_id = branch.json()["id"]

        async with _client(session, url, str(ids["participant_id"])) as member:
            refused = await member.post(
                f"{base}/contributions",
                json={"branch_id": branch_id, "kind": "idea", "title": "Sneaky"},
            )
            assert refused.status_code == 404


async def test_non_member_is_refused_everywhere(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (await client.get(f"{base}/branches")).status_code == 404
            assert (await client.get(f"{base}/contributions")).status_code == 404
            assert (
                await client.post(
                    f"{base}/branches",
                    json={"title": "Nope", "visibility": "shared"},
                )
            ).status_code == 404
            assert (
                await client.post(
                    f"{base}/contributions",
                    json={"branch_id": str(uuid4()), "kind": "idea", "title": "Nope"},
                )
            ).status_code == 404


async def test_uninvolved_member_cannot_write(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["uninvolved_id"])) as client:
            assert (
                await client.post(
                    f"{base}/branches",
                    json={"title": "Nope", "visibility": "shared"},
                )
            ).status_code == 403


async def test_branches_stay_inside_their_workspace(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as owner:
            branch = await owner.post(
                f"{base}/branches",
                json={"title": "Explore", "visibility": "shared"},
            )
            branch_id = branch.json()["id"]

        async with _client(session, url, str(ids["outsider_id"])) as other:
            denied = await other.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}"
                f"/branches/{branch_id}"
            )
            assert denied.status_code == 404


async def test_contribution_provenance_round_trip(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            branch = await client.post(
                f"{base}/branches",
                json={"title": "Explore", "visibility": "shared"},
            )
            proposed = await client.post(
                f"{base}/contributions",
                json={
                    "branch_id": branch.json()["id"],
                    "kind": "evidence",
                    "title": "Churn dropped 4 points",
                    "body": "Observed after the onboarding change.",
                    "source": "https://example.test/churn",
                    "tool_model": "analyst/v2",
                    "transformation_history": {"trimmed": "chart to one line"},
                },
            )
            listed = await client.get(f"{base}/contributions")
            items = listed.json()["items"]
            assert len(items) == 1
            item = items[0]
            assert item["id"] == proposed.json()["id"]
            assert item["branch_id"] == branch.json()["id"]
            assert item["author_id"] == str(ids["owner_id"])
            assert item["source"] == "https://example.test/churn"
            assert item["tool_model"] == "analyst/v2"
            assert item["transformation_history"] == {"trimmed": "chart to one line"}


async def test_unauthenticated_request_is_unauthorized(branch_database):
    engine, url = branch_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _open_space(session, ids["workspace_id"], ids["owner_id"])
        base = _space_paths(ids["workspace_id"], space.id)
        async with _client(session, url, None) as client:
            response = await client.get(f"{base}/branches")
            assert response.status_code == 401
