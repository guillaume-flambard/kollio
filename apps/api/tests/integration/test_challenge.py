import os
from collections.abc import Mapping
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.challenge.adapters.postgres import PostgresChallenge
from src.modules.challenge.service.challenge import open_challenge, record_finding
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.modules.options.adapters.postgres import PostgresOptions
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def challenge_database():
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
            Workspace(id=workspace_id, name="Challenge workspace"),
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


class _FakeQueue:
    def __init__(self) -> None:
        self.dispatched: list[UUID] = []

    async def dispatch(self, run_id: UUID, trace_context: Mapping[str, str]) -> None:
        self.dispatched.append(run_id)


def _client(session, url, subject: str | None):
    app = create_app(Settings(_env_file=None, database_url=url))
    if subject is not None:
        app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    app.state.challenge_queue = _FakeQueue()
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def _create_option(session, *, space_id, created_by, title, proposal):
    return await PostgresOptions(session).create_option(
        space_id=space_id,
        title=title,
        proposal=proposal,
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=created_by,
        lang="en",
    )


async def _scaffold(session, ids, *, with_contribution=False):
    """A Space, an Option on it, and optionally a confirmed Contribution."""
    spaces = PostgresDecisionSpaces(session)
    space = await spaces.create(
        workspace_id=ids["workspace_id"],
        question="Which pricing should we pick?",
        description=None,
        deadline=None,
        owner_id=ids["owner_id"],
        lang="en",
    )
    option = await _create_option(
        session,
        space_id=space.id,
        created_by=ids["owner_id"],
        title="Raise prices",
        proposal="Raise the entry price by 20%.",
    )
    contribution_id = None
    if with_contribution:
        branches = PostgresBranches(session)
        branch = await branches.create_branch(
            space_id=space.id,
            title="Pricing notes",
            summary=None,
            visibility="shared",
            created_by=ids["owner_id"],
            source_idea_id=None,
            lang="en",
        )
        contribution = await branches.create_contribution(
            space_id=space.id,
            branch_id=branch.id,
            kind="evidence",
            title="Churn is price insensitive",
            body=None,
            author_id=ids["owner_id"],
            source=None,
            tool_model=None,
            transformation_history=None,
            status="confirmed",
            lang="en",
        )
        contribution_id = contribution.id
    await session.flush()
    return space, option, contribution_id


def _base(workspace_id, space_id, option_id, run_id=None):
    path = f"/workspaces/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges"
    return f"{path}/{run_id}" if run_id else path


async def test_member_reads_a_challenge(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            assert opened.status_code == 201
            run_id = opened.json()["id"]

            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            assert read.status_code == 200
            body = read.json()
            assert body["run"]["status"] == "RUNNING"
            assert body["findings"] == []
            assert body["coverage"]["covered"] == []
            assert len(body["coverage"]["uncovered"]) == 6


async def test_open_round_trip(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(
                _base(ids["workspace_id"], space.id, option.id),
                headers={"Accept-Language": "fr"},
            )
            assert opened.status_code == 201
            body = opened.json()
            assert body["status"] == "RUNNING"
            assert body["opened_by"] == str(ids["owner_id"])
            assert body["model"] is None
            assert body["lang"] == "fr"
            assert body["option_id"] == str(option.id)

            listed = await client.get(_base(ids["workspace_id"], space.id, option.id))
            assert listed.status_code == 200
            assert [run["id"] for run in listed.json()["runs"]] == [body["id"]]


async def test_every_kind_recorded(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        kinds = [
            "unsupported_assumption",
            "contradictory_evidence",
            "hidden_dependency",
            "failure_mode",
            "causal_claim",
            "missing_success_criteria",
        ]
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            for kind in kinds:
                recorded = await client.post(
                    _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings",
                    json={"kind": kind, "severity": "high", "detail": f"About {kind}"},
                )
                assert recorded.status_code == 201
                assert recorded.json()["status"] == "confirmed"
                assert recorded.json()["origin"] == "human"

            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            body = read.json()
            assert {finding["kind"] for finding in body["findings"]} == set(kinds)
            assert len(body["findings"]) == 6
            assert sorted(body["coverage"]["covered"]) == sorted(kinds)
            assert body["coverage"]["uncovered"] == []


async def test_unknown_kind_or_severity_refused(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            path = _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings"
            bad_kind = await client.post(
                path, json={"kind": "weakness", "severity": "high", "detail": "Nope"}
            )
            assert bad_kind.status_code == 422
            bad_severity = await client.post(
                path, json={"kind": "failure_mode", "severity": "blocker", "detail": "Nope"}
            )
            assert bad_severity.status_code == 422

            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            assert read.json()["findings"] == []


async def test_blank_detail_refused(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            path = _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings"
            for detail in ("", "   "):
                refused = await client.post(
                    path,
                    json={"kind": "failure_mode", "severity": "low", "detail": detail},
                )
                assert refused.status_code == 422
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            assert read.json()["findings"] == []


async def test_contribution_reference_round_trip(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, contribution_id = await _scaffold(session, ids, with_contribution=True)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            recorded = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings",
                json={
                    "kind": "contradictory_evidence",
                    "severity": "medium",
                    "detail": "The churn evidence contradicts the pricing claim.",
                    "contribution_id": str(contribution_id),
                },
            )
            assert recorded.status_code == 201
            assert recorded.json()["contribution_id"] == str(contribution_id)


async def test_foreign_contribution_refused(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            refused = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings",
                json={
                    "kind": "hidden_dependency",
                    "severity": "low",
                    "detail": "Depends on something elsewhere.",
                    "contribution_id": str(uuid4()),
                },
            )
            assert refused.status_code == 422
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            assert read.json()["findings"] == []


async def test_critic_finding_arrives_proposed(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        repository = PostgresChallenge(session)
        run = await open_challenge(
            repository,
            ids["workspace_id"],
            space.id,
            option.id,
            str(ids["owner_id"]),
            lang="en",
            queue=_FakeQueue(),
            trace_context={},
        )
        finding = await record_finding(
            repository,
            ids["workspace_id"],
            space.id,
            option.id,
            run.id,
            str(ids["owner_id"]),
            kind="causal_claim",
            severity="high",
            detail="The proposal assumes price drives retention, which is unproven.",
            contribution_id=None,
            origin="critic",
            lang="en",
        )
        assert finding.status == "proposed"
        assert finding.origin == "critic"

        read = await PostgresChallenge(session).findings(run.id)
        assert [item.status for item in read] == ["proposed"]


async def test_confirm_and_dismiss_keep_the_record(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        await PostgresDecisionSpaces(session).add_participant(space.id, ids["participant_id"])
        repository = PostgresChallenge(session)
        run = await open_challenge(
            repository,
            ids["workspace_id"],
            space.id,
            option.id,
            str(ids["owner_id"]),
            lang="en",
            queue=_FakeQueue(),
            trace_context={},
        )
        proposed = await record_finding(
            repository,
            ids["workspace_id"],
            space.id,
            option.id,
            run.id,
            str(ids["owner_id"]),
            kind="failure_mode",
            severity="high",
            detail="A competitor could undercut us within a quarter.",
            contribution_id=None,
            origin="critic",
            lang="en",
        )
        dismissed_seed = await record_finding(
            repository,
            ids["workspace_id"],
            space.id,
            option.id,
            run.id,
            str(ids["owner_id"]),
            kind="hidden_dependency",
            severity="low",
            detail="Depends on a vendor we do not use.",
            contribution_id=None,
            origin="critic",
            lang="en",
        )
        await session.flush()

        async with _client(session, url, str(ids["participant_id"])) as client:
            confirmed = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run.id)
                + f"/findings/{proposed.id}/resolution",
                json={"resolution": "confirmed"},
            )
            assert confirmed.status_code == 200
            assert confirmed.json()["status"] == "confirmed"

            dismissed = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run.id)
                + f"/findings/{dismissed_seed.id}/resolution",
                json={"resolution": "dismissed"},
            )
            assert dismissed.status_code == 200
            assert dismissed.json()["status"] == "dismissed"
            assert dismissed.json()["origin"] == "critic"

            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run.id))
            body = read.json()
            assert len(body["findings"]) == 2
            assert "failure_mode" in body["coverage"]["covered"]
            assert "hidden_dependency" in body["coverage"]["uncovered"]


async def test_dismissed_findings_do_not_cover(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            recorded = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings",
                json={"kind": "causal_claim", "severity": "low", "detail": "A claim"},
            )
            finding_id = recorded.json()["id"]
            await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id)
                + f"/findings/{finding_id}/resolution",
                json={"resolution": "dismissed"},
            )
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            body = read.json()
            assert body["coverage"]["covered"] == []
            assert len(body["coverage"]["uncovered"]) == 6
            assert body["findings"][0]["status"] == "dismissed"


async def test_coverage_gates_nothing(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            first = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = first.json()["id"]
            completed = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/completion"
            )
            assert completed.status_code == 200
            assert completed.json()["status"] == "COMPLETED"

            second = await client.post(_base(ids["workspace_id"], space.id, option.id))
            assert second.status_code == 201
            assert second.json()["id"] != run_id


async def test_unchallenged_option(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            listed = await client.get(_base(ids["workspace_id"], space.id, option.id))
            assert listed.status_code == 200
            body = listed.json()
            assert body["runs"] == []
            assert body["findings"] == []
            assert len(body["coverage"]["uncovered"]) == 6


async def test_run_lifecycle_is_closed(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            first = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/completion"
            )
            assert first.status_code == 200
            again = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/completion"
            )
            assert again.status_code == 422


async def test_completed_run_keeps_its_findings(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]
            recorded = await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/findings",
                json={"kind": "unsupported_assumption", "severity": "high", "detail": "A"},
            )
            await client.post(
                _base(ids["workspace_id"], space.id, option.id, run_id) + "/completion"
            )
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run_id))
            body = read.json()
            assert body["run"]["status"] == "COMPLETED"
            assert [f["id"] for f in body["findings"]] == [recorded.json()["id"]]
            assert body["coverage"]["covered"] == ["unsupported_assumption"]


async def test_run_never_leaks_across_spaces_or_options(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        other_option = await _create_option(
            session,
            space_id=space.id,
            created_by=ids["owner_id"],
            title="Keep prices",
            proposal="Hold the entry price where it is.",
        )
        await session.flush()
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(_base(ids["workspace_id"], space.id, option.id))
            run_id = opened.json()["id"]

            wrong_option = await client.get(
                _base(ids["workspace_id"], space.id, other_option.id, run_id)
            )
            assert wrong_option.status_code == 404

        async with _client(session, url, str(ids["outsider_id"])) as other:
            denied = await other.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}"
                f"/options/{option.id}/challenges/{run_id}"
            )
            assert denied.status_code == 404


async def test_non_member_is_refused_everywhere(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        base = _base(ids["workspace_id"], space.id, option.id)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (await client.get(base)).status_code == 404
            assert (await client.post(base)).status_code == 404
            assert (
                await client.post(
                    base + f"/{uuid4()}/findings",
                    json={"kind": "failure_mode", "severity": "low", "detail": "Nope"},
                )
            ).status_code == 404


async def test_uninvolved_member_cannot_write(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        base = _base(ids["workspace_id"], space.id, option.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            opened = await client.post(base)
            run_id = opened.json()["id"]
            recorded = await client.post(
                base + f"/{run_id}/findings",
                json={"kind": "failure_mode", "severity": "high", "detail": "Real"},
            )
            finding_id = recorded.json()["id"]

        async with _client(session, url, str(ids["uninvolved_id"])) as member:
            assert (await member.post(base)).status_code == 403
            assert (
                await member.post(
                    base + f"/{run_id}/findings",
                    json={"kind": "failure_mode", "severity": "high", "detail": "Nope"},
                )
            ).status_code == 403
            assert (
                await member.post(
                    base + f"/{run_id}/findings/{finding_id}/resolution",
                    json={"resolution": "dismissed"},
                )
            ).status_code == 403
            assert (await member.post(base + f"/{run_id}/completion")).status_code == 403

            read = await member.get(base + f"/{run_id}")
            assert read.status_code == 200
            assert read.json()["findings"][0]["status"] == "confirmed"


async def test_participant_can_write(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        spaces = PostgresDecisionSpaces(session)
        await spaces.add_participant(space.id, ids["participant_id"])
        await session.flush()
        base = _base(ids["workspace_id"], space.id, option.id)
        async with _client(session, url, str(ids["participant_id"])) as client:
            opened = await client.post(base)
            assert opened.status_code == 201
            run_id = opened.json()["id"]
            recorded = await client.post(
                base + f"/{run_id}/findings",
                json={"kind": "failure_mode", "severity": "high", "detail": "Ours"},
            )
            assert recorded.status_code == 201
            assert (await client.post(base + f"/{run_id}/completion")).status_code == 200


async def test_unauthenticated_request_is_unauthorized(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        async with _client(session, url, None) as client:
            response = await client.get(_base(ids["workspace_id"], space.id, option.id))
            assert response.status_code == 401


async def test_messages_are_localized(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        base = _base(ids["workspace_id"], space.id, option.id)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            french = await client.get(base, headers={"Accept-Language": "fr"})
            english = await client.get(base, headers={"Accept-Language": "en"})
            assert french.status_code == english.status_code == 404
            assert french.json()["detail"] == "Option introuvable"
            assert english.json()["detail"] == "Option not found"
            assert french.headers["content-language"] == "fr"
            assert english.headers["content-language"] == "en"


async def test_finding_lookup_is_scoped_to_its_run(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        base = _base(ids["workspace_id"], space.id, option.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            first = await client.post(base)
            first_id = first.json()["id"]
            recorded = await client.post(
                base + f"/{first_id}/findings",
                json={"kind": "failure_mode", "severity": "high", "detail": "Real"},
            )
            finding_id = recorded.json()["id"]
            second = await client.post(base)
            second_id = second.json()["id"]

            wrong_run = await client.post(
                base + f"/{second_id}/findings/{finding_id}/resolution",
                json={"resolution": "dismissed"},
            )
            assert wrong_run.status_code == 404

            unchanged = await client.get(base + f"/{first_id}")
            assert unchanged.json()["findings"][0]["status"] == "confirmed"


async def test_option_lookup_is_scoped_to_its_space(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        spaces = PostgresDecisionSpaces(session)
        other_space = await spaces.create(
            workspace_id=ids["workspace_id"],
            question="Another question entirely?",
            description=None,
            deadline=None,
            owner_id=ids["owner_id"],
            lang="en",
        )
        await session.flush()
        async with _client(session, url, str(ids["owner_id"])) as client:
            assert (
                await client.get(_base(ids["workspace_id"], other_space.id, option.id))
            ).status_code == 404
