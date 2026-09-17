import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import Branch, Contribution
from src.modules.challenge.adapters.postgres import ChallengeFinding, ChallengeRun
from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.decisions.adapters.postgres import Decision
from src.modules.experiments.adapters.postgres import Experiment, ExperimentOutcome, Learning
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.options.adapters.postgres import Option
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration

EARLIER = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
LATER = datetime(2026, 1, 2, 9, 0, tzinfo=UTC)
LATEST = datetime(2026, 1, 3, 9, 0, tzinfo=UTC)


@pytest_asyncio.fixture
async def inbox_database():
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


def _space(workspace_id, owner_id, question, status, created_at=None):
    return DecisionSpace(
        id=uuid4(),
        workspace_id=workspace_id,
        question=question,
        description=None,
        owner_id=owner_id,
        status=status,
        deadline=None,
        lang="en",
        created_at=created_at,
    )


async def _seed(session):
    workspace_id, other_workspace_id, quiet_workspace_id = uuid4(), uuid4(), uuid4()
    owner_id, participant_id, uninvolved_id, outsider_id, quiet_id = (uuid4() for _ in range(5))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Inbox workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            Workspace(id=quiet_workspace_id, name="Quiet workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=participant_id, auth_subject=str(participant_id), display_name="Member"),
            User(id=uninvolved_id, auth_subject=str(uninvolved_id), display_name="Uninvolved"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            User(id=quiet_id, auth_subject=str(quiet_id), display_name="Quiet"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=participant_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=uninvolved_id, role="member"),
            WorkspaceMembership(
                workspace_id=other_workspace_id, user_id=outsider_id, role="member"
            ),
            WorkspaceMembership(workspace_id=quiet_workspace_id, user_id=quiet_id, role="member"),
        ]
    )
    await session.flush()

    converging = _space(workspace_id, owner_id, "Should we ship the inbox?", "CONVERGING", EARLIER)
    converging_second = _space(
        workspace_id, owner_id, "Should we ship the second inbox?", "CONVERGING", LATER
    )
    converging_third = _space(
        workspace_id, owner_id, "Should we ship a third inbox?", "CONVERGING", LATEST
    )
    ready = _space(workspace_id, owner_id, "Decide on pricing", "READY_TO_DECIDE")
    ready_decided = _space(workspace_id, owner_id, "Already decided", "READY_TO_DECIDE")
    exploring = _space(workspace_id, owner_id, "Still exploring", "EXPLORING")
    foreign = _space(other_workspace_id, outsider_id, "Their convergence", "CONVERGING")
    session.add_all(
        [
            converging,
            converging_second,
            converging_third,
            ready,
            ready_decided,
            exploring,
            foreign,
        ]
    )
    await session.flush()

    session.add_all(
        [
            DecisionSpaceParticipant(space_id=converging.id, user_id=owner_id),
            DecisionSpaceParticipant(space_id=converging.id, user_id=participant_id),
        ]
    )
    await session.flush()

    idea = Idea(
        id=uuid4(),
        slug=f"idea-{uuid4().hex[:8]}",
        title="The inbox idea",
        pitch="A pitch.",
        owner_id=owner_id,
        workspace_id=workspace_id,
        stage="seed",
        initiative_type="idea",
        lang="en",
        visibility="workspace",
    )
    session.add(idea)
    await session.flush()

    branch = Branch(
        space_id=converging.id,
        title="Exploration",
        summary=None,
        source_idea_id=idea.id,
        visibility="shared",
        created_by=owner_id,
        lang="en",
    )
    session.add(branch)
    await session.flush()

    suggested = Contribution(
        space_id=converging.id,
        branch_id=branch.id,
        kind="claim",
        title="A suggested claim",
        body=None,
        author_id=owner_id,
        source=None,
        tool_model=None,
        transformation_history=None,
        status="suggested",
        lang="en",
    )
    confirmed = Contribution(
        space_id=converging.id,
        branch_id=branch.id,
        kind="evidence",
        title="A confirmed piece of evidence",
        body=None,
        author_id=owner_id,
        source=None,
        tool_model=None,
        transformation_history=None,
        status="confirmed",
        lang="en",
    )
    session.add_all([suggested, confirmed])
    await session.flush()

    option = Option(
        space_id=converging.id,
        title="An option",
        proposal="A proposal",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )
    option_ready = Option(
        space_id=ready.id,
        title="The pricing option",
        proposal="Charge monthly",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )
    option_decided = Option(
        space_id=ready_decided.id,
        title="The decided option",
        proposal="Charge yearly",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )
    session.add_all([option, option_ready, option_decided])
    await session.flush()

    run = ChallengeRun(
        space_id=converging.id,
        option_id=option.id,
        status="OPEN",
        opened_by=owner_id,
        model=None,
        lang="en",
    )
    session.add(run)
    await session.flush()

    session.add_all(
        [
            ChallengeFinding(
                run_id=run.id,
                kind="failure_mode",
                severity="high",
                detail="A proposed failure mode",
                origin="human",
                status="proposed",
                contribution_id=None,
                lang="en",
            ),
            ChallengeFinding(
                run_id=run.id,
                kind="causal_claim",
                severity="low",
                detail="An already confirmed finding",
                origin="human",
                status="confirmed",
                contribution_id=None,
                lang="en",
            ),
        ]
    )

    session.add(
        Decision(
            space_id=ready_decided.id,
            version=1,
            selected_option_id=option_decided.id,
            rationale="Because.",
            critical_assumptions=None,
            uncertainty=None,
            success_criteria=None,
            revisit_triggers=None,
            reviewer_ids=[str(owner_id)],
            decided_by=owner_id,
            lang="en",
        )
    )

    awaiting_outcome = Experiment(
        id=uuid4(),
        idea_id=idea.id,
        decision_space_id=converging.id,
        option_id=None,
        created_by_id=owner_id,
        title="A completed experiment",
        hypothesis="It will work",
        success_metric="CTR",
        baseline=None,
        target=None,
        status="completed",
    )
    with_outcome = Experiment(
        id=uuid4(),
        idea_id=idea.id,
        decision_space_id=converging.id,
        option_id=None,
        created_by_id=owner_id,
        title="An experiment with a result",
        hypothesis="It will work",
        success_metric="CTR",
        baseline=None,
        target=None,
        status="completed",
    )
    running = Experiment(
        id=uuid4(),
        idea_id=idea.id,
        decision_space_id=converging.id,
        option_id=None,
        created_by_id=owner_id,
        title="A running experiment",
        hypothesis="It will work",
        success_metric="CTR",
        baseline=None,
        target=None,
        status="running",
    )
    session.add_all([awaiting_outcome, with_outcome, running])
    await session.flush()

    session.add(
        ExperimentOutcome(
            id=uuid4(),
            experiment_id=with_outcome.id,
            recorded_by_id=owner_id,
            metric="CTR",
            value="4.2",
            unit="%",
            observed_at=None,
            comment=None,
            qualitative=None,
        )
    )
    await session.flush()

    session.add_all(
        [
            Learning(
                id=uuid4(),
                experiment_id=with_outcome.id,
                idea_id=idea.id,
                status="draft",
                text="A draft learning",
                outcome_ids=[],
                confirmed_by_id=None,
            ),
            Learning(
                id=uuid4(),
                experiment_id=awaiting_outcome.id,
                idea_id=idea.id,
                status="confirmed",
                text="A confirmed learning",
                outcome_ids=[],
                confirmed_by_id=owner_id,
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
        "quiet_id": quiet_id,
        "converging": converging.id,
        "converging_second": converging_second.id,
        "converging_third": converging_third.id,
        "ready": ready.id,
        "ready_decided": ready_decided.id,
        "exploring": exploring.id,
        "foreign": foreign.id,
        "suggested": suggested.id,
        "confirmed": confirmed.id,
        "awaiting_outcome": awaiting_outcome.id,
        "with_outcome": with_outcome.id,
        "running": running.id,
    }


def _kinds(section):
    return [entry["kind"] for entry in section["entries"]]


def _spaces(section):
    return {entry["space_id"] for entry in section["entries"]}


def _subjects(section):
    return {entry["subject_id"] for entry in section["entries"]}


async def _inbox(session, url, subject, **params):
    async with _client(session, url, str(subject)) as client:
        return await client.get("/inbox", params=params)


async def test_converging_spaces_appear_oldest_first_with_their_total(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        response = await _inbox(session, url, ids["owner_id"])
        assert response.status_code == 200
        section = response.json()["needs_convergence"]
        assert section["total"] == 3
        assert [entry["space_id"] for entry in section["entries"]] == [
            str(ids["converging"]),
            str(ids["converging_second"]),
            str(ids["converging_third"]),
        ]
        assert _kinds(section) == ["space_needs_convergence"] * 3
        assert section["entries"][0]["space_question"] == "Should we ship the inbox?"
        assert section["entries"][0]["space_status"] == "CONVERGING"


async def test_an_exploring_space_is_quoted_by_no_section(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        body = (await _inbox(session, url, ids["owner_id"])).json()
        for section in body.values():
            subjects = {entry["space_id"] for entry in section["entries"]}
            assert str(ids["exploring"]) not in subjects


async def test_a_ready_space_awaits_commitment(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"])).json()["ready_to_decide"]
        assert _spaces(section) == {str(ids["ready"])}
        assert _kinds(section) == ["decision_awaits_commitment"]
        assert section["total"] == 1


async def test_a_space_that_already_holds_a_decision_is_not_prompted(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"])).json()["ready_to_decide"]
        assert str(ids["ready_decided"]) not in _spaces(section)


async def test_suggested_contributions_await_my_input(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"])).json()["needs_my_input"]
        kinds = set(_kinds(section))
        assert "contribution_awaits_confirmation" in kinds
        assert "finding_awaits_resolution" in kinds
        assert str(ids["suggested"]) in _subjects(section)
        assert str(ids["confirmed"]) not in _subjects(section)


async def test_needs_my_input_is_personal_to_owner_and_participants(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        participant = (await _inbox(session, url, ids["participant_id"])).json()
        assert str(ids["suggested"]) in _subjects(participant["needs_my_input"])

        uninvolved = (await _inbox(session, url, ids["uninvolved_id"])).json()
        assert str(ids["suggested"]) not in _subjects(uninvolved["needs_my_input"])
        assert uninvolved["needs_my_input"]["entries"] == []
        assert uninvolved["needs_my_input"]["total"] == 0


async def test_a_completed_experiment_without_an_outcome_awaits_learning(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"])).json()["needs_learning"]
        subjects = _subjects(section)
        assert str(ids["awaiting_outcome"]) in subjects
        assert str(ids["with_outcome"]) not in subjects
        assert str(ids["running"]) not in subjects
        assert "experiment_awaits_outcome" in set(_kinds(section))
        assert "learning_awaits_confirmation" in set(_kinds(section))


async def test_a_draft_learning_awaits_confirmation_and_a_confirmed_one_does_not(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"])).json()["needs_learning"]
        drafts = [
            entry for entry in section["entries"] if entry["kind"] == "learning_awaits_confirmation"
        ]
        assert len(drafts) == 1
        assert drafts[0]["detail"] == "A draft learning"


async def test_the_inbox_never_leaks_across_workspaces(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        body = (await _inbox(session, url, ids["owner_id"])).json()
        for section in body.values():
            for entry in section["entries"]:
                assert entry["workspace_id"] == str(ids["workspace_id"])
                assert entry["space_id"] != str(ids["foreign"])


async def test_an_empty_inbox_is_an_empty_answer_not_an_error(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        response = await _inbox(session, url, ids["quiet_id"])
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {
            "needs_convergence",
            "needs_my_input",
            "ready_to_decide",
            "needs_learning",
        }
        for section in body.values():
            assert section["entries"] == []
            assert section["total"] == 0


async def test_the_memory_section_is_absent_because_it_cannot_be_answered(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        body = (await _inbox(session, url, ids["owner_id"])).json()
        assert "relevant_prior_memory" not in body


async def test_the_limit_bounds_each_section_and_the_total_still_speaks(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        section = (await _inbox(session, url, ids["owner_id"], limit=2)).json()["needs_convergence"]
        assert section["total"] == 3
        assert len(section["entries"]) == 2
        assert [entry["space_id"] for entry in section["entries"]] == [
            str(ids["converging"]),
            str(ids["converging_second"]),
        ]


@pytest.mark.parametrize("limit", ["0", "51", "-1"])
async def test_an_out_of_range_limit_is_refused(inbox_database, limit: str):
    engine, url = inbox_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        response = await _inbox(session, url, ids["owner_id"], limit=limit)
        assert response.status_code == 422


async def test_unauthenticated_request_is_unauthorized(inbox_database):
    engine, url = inbox_database
    async with _tx(engine) as session:
        await _seed(session)
        async with _client(session, url, None) as client:
            response = await client.get("/inbox")
            assert response.status_code == 401
