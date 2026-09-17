import os
from collections.abc import Mapping
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.challenge.adapters.postgres import PostgresChallenge
from src.modules.challenge.service.challenge import (
    EMPTY_RESULT_REASON,
    QUEUE_FAILED_REASON,
    execute_run,
    open_challenge,
)
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
    owner_id, participant_id, outsider_id = (uuid4() for _ in range(3))
    session.add_all(
        [
            Workspace(id=workspace_id, name="Challenge workspace"),
            Workspace(id=other_workspace_id, name="Other workspace"),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            User(id=participant_id, auth_subject=str(participant_id), display_name="Member"),
            User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="member"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=participant_id, role="member"),
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
        "outsider_id": outsider_id,
    }


class _FakeQueue:
    def __init__(self, error: Exception | None = None) -> None:
        self.dispatched: list[UUID] = []
        self.error = error

    async def dispatch(self, run_id: UUID, trace_context: Mapping[str, str]) -> None:
        if self.error is not None:
            raise self.error
        self.dispatched.append(run_id)


class _FakeGateway:
    model = "fake-critic"

    def __init__(
        self,
        findings: list[Mapping[str, object]] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.findings: list[Mapping[str, object]] = findings if findings is not None else []
        self.error = error
        self.briefs: list[Mapping[str, object]] = []
        self.locales: list[str] = []

    async def challenge(
        self, *, brief: Mapping[str, object], locale: str
    ) -> list[Mapping[str, object]]:
        self.briefs.append(brief)
        self.locales.append(locale)
        if self.error is not None:
            raise self.error
        return self.findings


def _client(session, url, subject: str | None):
    app = create_app(Settings(_env_file=None, database_url=url))
    if subject is not None:
        app.dependency_overrides[current_identity] = lambda: Identity(subject)

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    app.state.challenge_queue = _FakeQueue()
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


def _base(workspace_id, space_id, option_id, run_id=None):
    path = f"/workspaces/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges"
    return f"{path}/{run_id}" if run_id else path


async def _scaffold(session, ids, *, contributions=()):
    spaces = PostgresDecisionSpaces(session)
    space = await spaces.create(
        workspace_id=ids["workspace_id"],
        question="Which pricing should we pick?",
        description=None,
        deadline=None,
        owner_id=ids["owner_id"],
        lang="en",
    )
    option = await PostgresOptions(session).create_option(
        space_id=space.id,
        title="Raise prices",
        proposal="Raise the entry price by 20%.",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=ids["owner_id"],
        lang="en",
    )
    branches = PostgresBranches(session)
    linked: dict[str, UUID] = {}
    for name, status, side in contributions:
        branch = await branches.create_branch(
            space_id=space.id,
            title=f"{name} branch",
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
            title=name,
            body=None,
            author_id=ids["owner_id"],
            source=None,
            tool_model=None,
            transformation_history=None,
            status=status,
            lang="en",
        )
        await PostgresOptions(session).link_evidence(option.id, contribution.id, side)
        linked[name] = contribution.id
    await session.flush()
    return space, option, linked


async def _open(session, ids, space, option, *, lang="en"):
    return await open_challenge(
        PostgresChallenge(session),
        ids["workspace_id"],
        space.id,
        option.id,
        str(ids["owner_id"]),
        lang=lang,
        queue=_FakeQueue(),
        trace_context={},
    )


def _finding(**overrides: Any) -> dict[str, object]:
    payload: dict[str, object] = {
        "kind": "unsupported_assumption",
        "severity": "medium",
        "detail": "Nothing supports the claim that churn stays flat.",
        "contribution_id": None,
    }
    payload.update(overrides)
    return payload


async def test_opening_a_challenge_dispatches_the_run(challenge_database):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        assert run.status == "RUNNING"


async def test_a_dispatch_that_cannot_be_queued_fails_the_run(challenge_database):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await open_challenge(
            PostgresChallenge(session),
            ids["workspace_id"],
            space.id,
            option.id,
            str(ids["owner_id"]),
            lang="en",
            queue=_FakeQueue(error=RuntimeError("redis is down")),
            trace_context={},
        )
        assert run.status == "FAILED"
        assert run.failure_reason == QUEUE_FAILED_REASON


async def test_the_critic_result_is_stored_as_proposals_and_completes_the_run(
    challenge_database,
):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, linked = await _scaffold(
            session, ids, contributions=[("Churn is flat", "confirmed", "for")]
        )
        run = await _open(session, ids, space, option)
        gateway = _FakeGateway(findings=[_finding(contribution_id=str(linked["Churn is flat"]))])

        result = await execute_run(PostgresChallenge(session), gateway, run.id, "en")

        assert result.status == "COMPLETED"
        assert result.model == "fake-critic"
        findings = await PostgresChallenge(session).findings(run.id)
        assert len(findings) == 1
        assert findings[0].origin == "critic"
        assert findings[0].status == "proposed"
        assert findings[0].kind == "unsupported_assumption"
        assert findings[0].contribution_id == linked["Churn is flat"]

        async with _client(session, url, str(ids["owner_id"])) as client:
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run.id))
            body = read.json()
            assert read.status_code == 200
            assert body["run"]["status"] == "COMPLETED"
            assert body["run"]["model"] == "fake-critic"
            assert body["run"]["failure_reason"] is None
            assert [row["status"] for row in body["findings"]] == ["proposed"]


async def test_the_brief_carries_the_question_the_option_and_only_confirmed_evidence(
    challenge_database,
):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, linked = await _scaffold(
            session,
            ids,
            contributions=[
                ("Churn is flat", "confirmed", "for"),
                ("Rumour says otherwise", "suggested", "against"),
            ],
        )
        run = await _open(session, ids, space, option)
        gateway = _FakeGateway(findings=[_finding()])

        await execute_run(PostgresChallenge(session), gateway, run.id, "fr")

        assert gateway.locales == ["fr"]
        brief = gateway.briefs[0]
        assert brief["question"] == "Which pricing should we pick?"
        assert brief["option"] == {
            "title": "Raise prices",
            "proposal": "Raise the entry price by 20%.",
        }
        evidence = brief["evidence"]
        assert isinstance(evidence, list)
        assert [item["title"] for item in evidence] == ["Churn is flat"]
        assert evidence[0]["contribution_id"] == str(linked["Churn is flat"])
        assert evidence[0]["side"] == "for"
        assert "Rumour says otherwise" not in str(brief)


async def test_an_error_ends_the_run_with_a_reason_and_stores_nothing(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        gateway = _FakeGateway(error=RuntimeError("the gateway timed out"))

        result = await execute_run(PostgresChallenge(session), gateway, run.id, "en")

        assert result.status == "FAILED"
        assert result.failure_reason == "The Critic could not answer: RuntimeError"
        assert await PostgresChallenge(session).findings(run.id) == []

        async with _client(session, url, str(ids["owner_id"])) as client:
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run.id))
            body = read.json()
            assert body["run"]["failure_reason"] == "The Critic could not answer: RuntimeError"


async def test_an_empty_result_fails_the_run(challenge_database):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)

        result = await execute_run(
            PostgresChallenge(session), _FakeGateway(findings=[]), run.id, "en"
        )

        assert result.status == "FAILED"
        assert result.failure_reason == EMPTY_RESULT_REASON
        assert await PostgresChallenge(session).findings(run.id) == []


async def test_an_unusable_result_stores_nothing(challenge_database):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        gateway = _FakeGateway(
            findings=[_finding(), _finding(kind="vibes", detail="This one is unusable.")]
        )

        result = await execute_run(PostgresChallenge(session), gateway, run.id, "en")

        assert result.status == "FAILED"
        assert await PostgresChallenge(session).findings(run.id) == []


async def test_a_citation_outside_the_brief_is_refused(challenge_database):
    engine, _ = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        gateway = _FakeGateway(findings=[_finding(contribution_id=str(uuid4()))])

        result = await execute_run(PostgresChallenge(session), gateway, run.id, "en")

        assert result.status == "FAILED"
        assert result.failure_reason == "A finding cites a contribution that was not in the brief"
        assert await PostgresChallenge(session).findings(run.id) == []


async def test_a_human_settles_a_critic_finding(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        await execute_run(
            PostgresChallenge(session), _FakeGateway(findings=[_finding()]), run.id, "en"
        )
        findings = await PostgresChallenge(session).findings(run.id)

        async with _client(session, url, str(ids["owner_id"])) as client:
            resolved = await client.post(
                f"{_base(ids['workspace_id'], space.id, option.id, run.id)}"
                f"/findings/{findings[0].id}/resolution",
                json={"resolution": "confirmed"},
            )
            assert resolved.status_code == 200
            assert resolved.json()["status"] == "confirmed"
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run.id))
            assert read.json()["run"]["status"] == "COMPLETED"


async def test_the_read_carries_no_verdict(challenge_database):
    engine, url = challenge_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space, option, _ = await _scaffold(session, ids)
        run = await _open(session, ids, space, option)
        await execute_run(
            PostgresChallenge(session), _FakeGateway(findings=[_finding()]), run.id, "en"
        )

        async with _client(session, url, str(ids["owner_id"])) as client:
            read = await client.get(_base(ids["workspace_id"], space.id, option.id, run.id))
            body = read.json()
            assert set(body) == {"run", "findings", "coverage"}
            for forbidden in ("verdict", "score", "ranking", "prediction"):
                assert forbidden not in str(body).lower()
