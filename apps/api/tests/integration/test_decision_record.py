import os
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.branches.service.branches import propose_contribution
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.decisions.adapters.postgres import PostgresDecisions
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.modules.options.adapters.postgres import PostgresOptions
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration

CHAIN = ("EXPLORING", "CONVERGING", "READY_TO_DECIDE")


@pytest_asyncio.fixture
async def record_database():
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
            Workspace(id=workspace_id, name="Decision workspace"),
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


async def _advance(session, space, statuses=CHAIN):
    spaces = PostgresDecisionSpaces(session)
    for status in statuses:
        await spaces.append_status_event(
            space, to_status=status, actor_id=space.owner_id, reason=None, lang="en"
        )
    return space


async def _option(session, space_id, owner_id, title="An option"):
    return await PostgresOptions(session).create_option(
        space_id=space_id,
        title=title,
        proposal="Do it this way.",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )


async def _contribution(session, workspace_id, space_id, subject, *, suggestion=False):
    branches = PostgresBranches(session)
    branch = await branches.create_branch(
        space_id=space_id,
        title="Explore",
        summary=None,
        visibility="shared",
        created_by=UUID(subject),
        source_idea_id=None,
        lang="en",
    )
    return await propose_contribution(
        branches,
        workspace_id,
        space_id,
        subject,
        branch_id=branch.id,
        kind="claim",
        title="A claim",
        body=None,
        source=None,
        tool_model=None,
        transformation_history=None,
        as_suggestion=suggestion,
        lang="en",
    )


def _decision_path(workspace_id, space_id):
    return f"/workspaces/{workspace_id}/decision-spaces/{space_id}/decision"


async def test_member_reads_the_record(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Cheaper to test."},
                headers={"Accept-Language": "fr"},
            )
            assert committed.status_code == 201

        async with _client(session, url, str(ids["participant_id"])) as reader:
            read = await reader.get(_decision_path(ids["workspace_id"], space.id))
            assert read.status_code == 200
            body = read.json()
            assert body["version"] == 1
            assert body["lang"] == "fr"
            assert body["selected_option_id"] == str(option.id)


async def test_no_record_yet(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(_decision_path(ids["workspace_id"], space.id))
            assert response.status_code == 404
            assert response.json()["detail"]

            versions = await client.get(f"{_decision_path(ids['workspace_id'], space.id)}/versions")
            assert versions.status_code == 200
            assert versions.json()["items"] == []


async def test_unauthenticated_request_is_unauthorized(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        async with _client(session, url, None) as client:
            assert (
                await client.get(_decision_path(ids["workspace_id"], space.id))
            ).status_code == 401


async def test_non_member_is_refused_everywhere(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (
                await client.get(_decision_path(ids["workspace_id"], space.id))
            ).status_code == 404
            assert (
                await client.get(f"{_decision_path(ids['workspace_id'], space.id)}/versions")
            ).status_code == 404
            assert (
                await client.post(
                    _decision_path(ids["workspace_id"], space.id),
                    json={"selected_option_id": str(option.id), "rationale": "Nope."},
                )
            ).status_code == 404


async def test_records_stay_inside_their_space(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as owner:
            assert (
                await owner.post(
                    _decision_path(ids["workspace_id"], space.id),
                    json={"selected_option_id": str(option.id), "rationale": "Yes."},
                )
            ).status_code == 201

        async with _client(session, url, str(ids["outsider_id"])) as other:
            denied = await other.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}/decision"
            )
            assert denied.status_code == 404


async def test_commit_from_ready_space_moves_it_to_decided(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Committed."},
            )
            assert committed.status_code == 201

            detail = await client.get(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{space.id}"
            )
            assert detail.json()["status"] == "DECIDED"
            assert detail.json()["history"][-1]["to_status"] == "DECIDED"
            assert detail.json()["history"][-1]["actor_id"] == str(ids["owner_id"])


@pytest.mark.parametrize(
    "statuses",
    [
        (),
        ("EXPLORING",),
        ("EXPLORING", "CONVERGING"),
        ("EXPLORING", "CONVERGING", "READY_TO_DECIDE", "DECIDED"),
    ],
)
async def test_commit_outside_ready_to_decide_refused(record_database, statuses):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        spaces = PostgresDecisionSpaces(session)
        for status in statuses:
            await spaces.append_status_event(
                space, to_status=status, actor_id=space.owner_id, reason=None, lang="en"
            )
        history_before = len(await spaces.history(space.id))
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Early."},
            )
            assert refused.status_code == 422
        assert await PostgresDecisions(session).all_versions(space.id) == []
        assert len(await spaces.history(space.id)) == history_before


async def test_full_record_round_trip(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await PostgresDecisionSpaces(session).add_participant(space.id, ids["participant_id"])
        chosen = await _option(session, space.id, ids["owner_id"], "Chosen")
        other = await _option(session, space.id, ids["owner_id"], "Other")
        for_contribution = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"])
        )
        against_contribution = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["participant_id"])
        )
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    "selected_option_id": str(chosen.id),
                    "rationale": "  Chosen because it ships sooner.  ",
                    "critical_assumptions": "Teams keep buying.",
                    "uncertainty": "Conversion is unknown.",
                    "success_criteria": "Three pilots in a quarter.",
                    "revisit_triggers": [
                        {
                            "metric": "  CTR  ",
                            "direction": "above",
                            "threshold": " 2.5% ",
                            "note": "Other becomes preferable",
                        },
                        {"metric": "churn"},
                    ],
                    "rejected_option_ids": [str(other.id)],
                    "arguments": [
                        {"contribution_id": str(for_contribution.id), "side": "for"},
                        {"contribution_id": str(against_contribution.id), "side": "against"},
                    ],
                },
            )
            assert committed.status_code == 201
            body = committed.json()
            assert body["rationale"] == "Chosen because it ships sooner."
            assert body["critical_assumptions"] == "Teams keep buying."
            assert body["uncertainty"] == "Conversion is unknown."
            assert body["success_criteria"] == "Three pilots in a quarter."
            assert body["revisit_triggers"] == [
                {
                    "metric": "CTR",
                    "direction": "above",
                    "threshold": "2.5%",
                    "note": "Other becomes preferable",
                },
                {"metric": "churn", "direction": None, "threshold": None, "note": None},
            ]
            assert body["rejected_option_ids"] == [str(other.id)]
            assert sorted(
                (argument["contribution_id"], argument["side"]) for argument in body["arguments"]
            ) == sorted(
                [
                    (str(for_contribution.id), "for"),
                    (str(against_contribution.id), "against"),
                ]
            )
            assert sorted(body["reviewer_ids"]) == sorted(
                [str(ids["owner_id"]), str(ids["participant_id"])]
            )
            assert body["decided_by"] == str(ids["owner_id"])

            read = await client.get(_decision_path(ids["workspace_id"], space.id))
            assert read.json() == body


async def test_minimal_record_round_trip(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Minimal."},
            )
            assert committed.status_code == 201
            body = committed.json()
            assert body["critical_assumptions"] is None
            assert body["uncertainty"] is None
            assert body["success_criteria"] is None
            assert body["revisit_triggers"] is None
            assert body["rejected_option_ids"] == []
            assert body["arguments"] == []


@pytest.mark.parametrize("rationale", ["", "   "])
async def test_blank_rationale_refused(record_database, rationale):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": rationale},
            )
            assert refused.status_code == 422
        assert await PostgresDecisions(session).all_versions(space.id) == []


async def test_foreign_option_refused(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        other_space = await _space(session, ids["workspace_id"], ids["owner_id"], "Other?")
        foreign = await _option(session, other_space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(foreign.id), "rationale": "Wrong space."},
            )
            assert refused.status_code == 422
        assert await PostgresDecisions(session).all_versions(space.id) == []


async def test_selected_option_cannot_be_rejected(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        chosen = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    "selected_option_id": str(chosen.id),
                    "rationale": "Contradiction.",
                    "rejected_option_ids": [str(chosen.id)],
                },
            )
            assert refused.status_code == 422
        assert await PostgresDecisions(session).all_versions(space.id) == []


async def test_argument_linking_rules(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        other_space = await _space(session, ids["workspace_id"], ids["owner_id"], "Other?")
        option = await _option(session, space.id, ids["owner_id"])
        confirmed = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"])
        )
        suggestion = await _contribution(
            session, ids["workspace_id"], space.id, str(ids["owner_id"]), suggestion=True
        )
        foreign = await _contribution(
            session, ids["workspace_id"], other_space.id, str(ids["owner_id"])
        )
        await _advance(session, space)
        base = {"selected_option_id": str(option.id), "rationale": "Try."}
        async with _client(session, url, str(ids["owner_id"])) as client:
            unknown = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    **base,
                    "arguments": [{"contribution_id": str(uuid4()), "side": "for"}],
                },
            )
            assert unknown.status_code == 422

            suggested = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    **base,
                    "arguments": [{"contribution_id": str(suggestion.id), "side": "for"}],
                },
            )
            assert suggested.status_code == 422

            outside = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    **base,
                    "arguments": [{"contribution_id": str(foreign.id), "side": "for"}],
                },
            )
            assert outside.status_code == 422

            both_ways = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    **base,
                    "arguments": [
                        {"contribution_id": str(confirmed.id), "side": "for"},
                        {"contribution_id": str(confirmed.id), "side": "against"},
                    ],
                },
            )
            assert both_ways.status_code == 422

        assert await PostgresDecisions(session).all_versions(space.id) == []


async def test_revisit_trigger_validation(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        base = {"selected_option_id": str(option.id), "rationale": "Try."}
        async with _client(session, url, str(ids["owner_id"])) as client:
            for trigger in (
                {"metric": ""},
                {"metric": "   "},
                {"threshold": "2.5%"},
                {"metric": "CTR", "direction": "sideways"},
                {"metric": "CTR", "threshold": "  "},
            ):
                refused = await client.post(
                    _decision_path(ids["workspace_id"], space.id),
                    json={**base, "revisit_triggers": [trigger]},
                )
                assert refused.status_code == 422, trigger

            accepted = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={**base, "revisit_triggers": [{"metric": "CTR"}]},
            )
            assert accepted.status_code == 201
            assert accepted.json()["revisit_triggers"] == [
                {"metric": "CTR", "direction": None, "threshold": None, "note": None}
            ]


async def test_reviewer_snapshot_is_frozen(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        spaces = PostgresDecisionSpaces(session)
        await spaces.add_participant(space.id, ids["participant_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Snapshot."},
            )
            assert committed.status_code == 201
            before = sorted(committed.json()["reviewer_ids"])
            assert before == sorted([str(ids["owner_id"]), str(ids["participant_id"])])

        await spaces.remove_participant(space.id, ids["participant_id"])
        async with _client(session, url, str(ids["owner_id"])) as client:
            read = await client.get(_decision_path(ids["workspace_id"], space.id))
            assert sorted(read.json()["reviewer_ids"]) == before


async def test_second_version_after_reopening(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        spaces = PostgresDecisionSpaces(session)
        first_option = await _option(session, space.id, ids["owner_id"], "First")
        second_option = await _option(session, space.id, ids["owner_id"], "Second")
        await _advance(session, space)
        async with _client(session, url, str(ids["owner_id"])) as client:
            first = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(first_option.id), "rationale": "First call."},
            )
            assert first.status_code == 201
            first_body = first.json()

            reopened = await client.post(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{space.id}/transitions",
                json={"to_status": "REOPENED", "reason": "New evidence arrived."},
            )
            assert reopened.status_code == 200
            resumed = await client.post(
                f"/workspaces/{ids['workspace_id']}/decision-spaces/{space.id}/transitions",
                json={"to_status": "EXPLORING"},
            )
            assert resumed.status_code == 200
            await spaces.append_status_event(
                space,
                to_status="CONVERGING",
                actor_id=ids["owner_id"],
                reason=None,
                lang="en",
            )
            await spaces.append_status_event(
                space,
                to_status="READY_TO_DECIDE",
                actor_id=ids["owner_id"],
                reason=None,
                lang="en",
            )

            second = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={
                    "selected_option_id": str(second_option.id),
                    "rationale": "Second call.",
                },
            )
            assert second.status_code == 201
            assert second.json()["version"] == 2

            versions = await client.get(f"{_decision_path(ids['workspace_id'], space.id)}/versions")
            assert [item["version"] for item in versions.json()["items"]] == [2, 1]

            current = await client.get(_decision_path(ids["workspace_id"], space.id))
            assert current.json()["version"] == 2

        stored_first = await PostgresDecisions(session).version(space.id, 1)
        assert stored_first is not None
        assert stored_first.rationale == first_body["rationale"]
        assert stored_first.selected_option_id == first_option.id
        assert stored_first.uncertainty is None


async def test_participant_can_commit(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await PostgresDecisionSpaces(session).add_participant(space.id, ids["participant_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["participant_id"])) as client:
            committed = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "By participant."},
            )
            assert committed.status_code == 201
            assert committed.json()["decided_by"] == str(ids["participant_id"])


async def test_uninvolved_member_cannot_commit(record_database):
    engine, url = record_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        await _advance(session, space)
        async with _client(session, url, str(ids["uninvolved_id"])) as client:
            refused = await client.post(
                _decision_path(ids["workspace_id"], space.id),
                json={"selected_option_id": str(option.id), "rationale": "Not mine."},
            )
            assert refused.status_code == 403
        assert await PostgresDecisions(session).all_versions(space.id) == []
