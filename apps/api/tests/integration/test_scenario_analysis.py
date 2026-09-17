import os
from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.modules.options.adapters.postgres import PostgresOptions
from src.modules.scenarios.adapters.postgres import PostgresScenarios
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def scenario_database():
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
            Workspace(id=workspace_id, name="Scenario workspace"),
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


async def _space(session, workspace_id, owner_id):
    return await PostgresDecisionSpaces(session).create(
        workspace_id=workspace_id,
        question="Which campaign?",
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )


async def _option(session, space_id, owner_id):
    return await PostgresOptions(session).create_option(
        space_id=space_id,
        title="Campaign A",
        proposal="Spend on A",
        mechanism=None,
        upside=None,
        cost=None,
        risks=None,
        critical_assumptions=None,
        success_metrics=None,
        created_by=owner_id,
        lang="en",
    )


async def _variable(session, space_id, name, *, low, base, high, unit=None):
    return await PostgresScenarios(session).create_variable(
        space_id=space_id,
        name=name,
        unit=unit,
        low=Decimal(low),
        base=Decimal(base),
        high=Decimal(high),
        lang="en",
    )


def _paths(workspace_id, space_id):
    base = f"/workspaces/{workspace_id}/decision-spaces/{space_id}"
    return base, f"{base}/scenario-variables"


async def test_variable_round_trip(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        base, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                variables_path,
                json={"name": "CTR", "unit": "%", "low": "1", "base": "2", "high": "3"},
                headers={"Accept-Language": "fr"},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["name"] == "CTR"
            assert body["unit"] == "%"
            assert body["low"] == "1"
            assert body["base"] == "2"
            assert body["high"] == "3"
            assert body["lang"] == "fr"
            assert body["space_id"] == str(space.id)

            listed = await client.get(variables_path)
            assert listed.status_code == 200
            assert [item["id"] for item in listed.json()["items"]] == [body["id"]]


@pytest.mark.parametrize("name", ["", "   "])
async def test_blank_variable_name_refused(scenario_database, name):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                variables_path,
                json={"name": name, "low": "1", "base": "2", "high": "3"},
            )
            # a whitespace name reaches the domain rule and is refused the same way
            assert refused.status_code == 422
            listed = await client.get(variables_path)
            assert listed.json()["items"] == []


async def test_unordered_range_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                variables_path,
                json={"name": "CPM", "low": "5", "base": "2", "high": "9"},
            )
            assert refused.status_code == 422
            listed = await client.get(variables_path)
            assert listed.json()["items"] == []


async def test_duplicate_variable_name_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                variables_path,
                json={"name": "CTR", "low": "4", "base": "5", "high": "6"},
            )
            assert refused.status_code == 422
            listed = await client.get(variables_path)
            assert len(listed.json()["items"]) == 1


async def test_variable_update_and_delete(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        variable = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            updated = await client.patch(
                f"{variables_path}/{variable.id}",
                json={"name": "CTR", "unit": "%", "low": "1", "base": "4", "high": "5"},
            )
            assert updated.status_code == 200
            assert updated.json()["base"] == "4"
            assert updated.json()["unit"] == "%"

            removed = await client.delete(f"{variables_path}/{variable.id}")
            assert removed.status_code == 204
            listed = await client.get(variables_path)
            assert listed.json()["items"] == []


async def test_run_round_trip(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                runs_path,
                json={
                    "level": "base",
                    "assumptions": "CTR stays at its current level",
                    "values": [{"variable_id": str(ctr.id), "value": "2"}],
                },
            )
            assert created.status_code == 201
            body = created.json()
            assert body["level"] == "base"
            assert body["option_id"] == str(option.id)
            assert body["values"] == [{"variable_id": str(ctr.id), "value": "2"}]

            listed = await client.get(runs_path)
            assert [item["id"] for item in listed.json()["items"]] == [body["id"]]


async def test_second_base_run_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            first = await client.post(
                runs_path, json={"level": "base", "assumptions": "Steady state"}
            )
            assert first.status_code == 201
            second = await client.post(
                runs_path, json={"level": "base", "assumptions": "Another steady state"}
            )
            assert second.status_code == 422

            other = await client.post(
                runs_path, json={"level": "optimistic", "assumptions": "Best case"}
            )
            assert other.status_code == 201


async def test_blank_assumptions_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(runs_path, json={"level": "base", "assumptions": "   "})
            assert refused.status_code == 422
            listed = await client.get(runs_path)
            assert listed.json()["items"] == []


async def test_unknown_run_level_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                runs_path, json={"level": "likely", "assumptions": "Not a level"}
            )
            assert refused.status_code == 422


async def test_run_with_foreign_variable_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        other_space = await PostgresDecisionSpaces(session).create(
            workspace_id=ids["other_workspace_id"],
            question="Elsewhere?",
            description=None,
            deadline=None,
            owner_id=ids["outsider_id"],
            lang="en",
        )
        foreign = await _variable(session, other_space.id, "Foreign", low="1", base="2", high="3")
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                runs_path,
                json={
                    "level": "base",
                    "assumptions": "Steady",
                    "values": [{"variable_id": str(foreign.id), "value": "2"}],
                },
            )
            assert refused.status_code == 422
            listed = await client.get(runs_path)
            assert listed.json()["items"] == []


async def test_duplicate_variable_in_one_run_refused(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            refused = await client.post(
                runs_path,
                json={
                    "level": "base",
                    "assumptions": "Steady",
                    "values": [
                        {"variable_id": str(ctr.id), "value": "2"},
                        {"variable_id": str(ctr.id), "value": "3"},
                    ],
                },
            )
            assert refused.status_code == 422


async def test_run_update_and_delete(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        base, _ = _paths(ids["workspace_id"], space.id)
        runs_path = f"{base}/options/{option.id}/scenario-runs"
        async with _client(session, url, str(ids["owner_id"])) as client:
            created = await client.post(
                runs_path,
                json={
                    "level": "base",
                    "assumptions": "Steady",
                    "values": [{"variable_id": str(ctr.id), "value": "2"}],
                },
            )
            run_id = created.json()["id"]

            updated = await client.patch(
                f"{runs_path}/{run_id}",
                json={
                    "level": "pessimistic",
                    "assumptions": "Worst case",
                    "values": [{"variable_id": str(ctr.id), "value": "1"}],
                },
            )
            assert updated.status_code == 200
            assert updated.json()["level"] == "pessimistic"
            assert updated.json()["values"] == [{"variable_id": str(ctr.id), "value": "1"}]

            removed = await client.delete(f"{runs_path}/{run_id}")
            assert removed.status_code == 204
            listed = await client.get(runs_path)
            assert listed.json()["items"] == []


async def test_sensitivity_reports_the_flip_and_the_ranking(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        revenue = await _variable(session, space.id, "Revenue", low="50", base="100", high="150")
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        budget = await _variable(session, space.id, "Budget", low="1", base="2", high="3")

        runs = PostgresScenarios(session)
        await runs.create_run(
            option_id=option.id,
            space_id=space.id,
            level="base",
            assumptions="Steady",
            created_by=ids["owner_id"],
            lang="en",
            values=[
                (revenue.id, Decimal("50")),
                (ctr.id, Decimal("1")),
                (budget.id, Decimal("1")),
            ],
        )
        await runs.create_run(
            option_id=option.id,
            space_id=space.id,
            level="optimistic",
            assumptions="Best case",
            created_by=ids["owner_id"],
            lang="en",
            values=[
                (revenue.id, Decimal("150")),
                (ctr.id, Decimal("3")),
                (budget.id, Decimal("9")),
            ],
        )

        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(
                f"{base}/options/{option.id}/sensitivity",
                params={
                    "metric_variable_id": str(revenue.id),
                    "direction": "above",
                    "threshold": "100",
                },
            )
            assert response.status_code == 200
            payload = response.json()

            assert set(payload) == {"criterion", "ranked", "incomplete_run_ids", "evidence"}
            assert payload["criterion"]["threshold"] == "100"
            assert payload["incomplete_run_ids"] == []

            ranked = {item["variable_id"]: item for item in payload["ranked"]}
            ctr_entry = ranked[str(ctr.id)]
            assert ctr_entry["status"] == "found"
            assert ctr_entry["interval"] == ["1", "3"]
            assert ctr_entry["crossing"] == "2"
            assert ctr_entry["crossings"] == 1
            assert Decimal(ctr_entry["slope_min"]) == Decimal("50")
            assert ranked[str(budget.id)]["status"] == "found"
            assert Decimal(ranked[str(budget.id)]["slope_min"]) == Decimal("12.5")

            order = [item["variable_id"] for item in payload["ranked"]]
            assert order == [str(ctr.id), str(budget.id)]

            # no field, anywhere, carries a predicted value
            flat = response.text.lower()
            for forbidden in ("predic", "forecast"):
                assert forbidden not in flat


async def test_sensitivity_reports_incomplete_runs(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        revenue = await _variable(session, space.id, "Revenue", low="50", base="100", high="150")
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        runs = PostgresScenarios(session)
        await runs.create_run(
            option_id=option.id,
            space_id=space.id,
            level="base",
            assumptions="Steady",
            created_by=ids["owner_id"],
            lang="en",
            values=[(revenue.id, Decimal("50")), (ctr.id, Decimal("1"))],
        )
        incomplete = await runs.create_run(
            option_id=option.id,
            space_id=space.id,
            level="optimistic",
            assumptions="Best case",
            created_by=ids["owner_id"],
            lang="en",
            values=[(ctr.id, Decimal("3"))],
        )
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(
                f"{base}/options/{option.id}/sensitivity",
                params={
                    "metric_variable_id": str(revenue.id),
                    "direction": "above",
                    "threshold": "100",
                },
            )
            payload = response.json()
            assert payload["incomplete_run_ids"] == [str(incomplete.id)]
            entry = payload["ranked"][0]
            assert entry["variable_id"] == str(ctr.id)
            assert entry["status"] == "insufficient_points"


async def test_sensitivity_reports_beyond_the_declared_range(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        revenue = await _variable(session, space.id, "Revenue", low="50", base="100", high="150")
        ctr = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        runs = PostgresScenarios(session)
        for level, revenue_value, ctr_value in (
            ("base", "150", "1"),
            ("optimistic", "200", "3"),
        ):
            await runs.create_run(
                option_id=option.id,
                space_id=space.id,
                level=level,
                assumptions=f"{level} assumptions",
                created_by=ids["owner_id"],
                lang="en",
                values=[
                    (revenue.id, Decimal(revenue_value)),
                    (ctr.id, Decimal(ctr_value)),
                ],
            )
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(
                f"{base}/options/{option.id}/sensitivity",
                params={
                    "metric_variable_id": str(revenue.id),
                    "direction": "above",
                    "threshold": "100",
                },
            )
            entry = response.json()["ranked"][0]
            assert entry["variable_id"] == str(ctr.id)
            assert entry["status"] == "beyond_declared_range"
            assert entry["travel"] == "up"
            assert entry["crossing"] is None


async def test_sensitivity_unknown_metric_is_not_found(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(
                f"{base}/options/{option.id}/sensitivity",
                params={
                    "metric_variable_id": str(uuid4()),
                    "direction": "above",
                    "threshold": "100",
                },
            )
            assert response.status_code == 404


async def test_sensitivity_requires_a_criterion(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(f"{base}/options/{option.id}/sensitivity")
            assert response.status_code == 422


async def test_evidence_counts_are_reported(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        revenue = await _variable(session, space.id, "Revenue", low="50", base="100", high="150")
        branch = await PostgresBranches(session).create_branch(
            space_id=space.id,
            title="Explore",
            summary=None,
            visibility="shared",
            created_by=ids["owner_id"],
            source_idea_id=None,
            lang="en",
        )
        contributions = PostgresBranches(session)
        for side in ("for", "against"):
            suggestion = await contributions.create_contribution(
                space_id=space.id,
                branch_id=branch.id,
                kind="evidence",
                title=f"Evidence {side}",
                body=None,
                author_id=ids["owner_id"],
                source=None,
                tool_model=None,
                transformation_history=None,
                status="confirmed",
                lang="en",
            )
            await PostgresOptions(session).link_evidence(option.id, suggestion.id, side)
        runs = PostgresScenarios(session)
        await runs.create_run(
            option_id=option.id,
            space_id=space.id,
            level="base",
            assumptions="Steady",
            created_by=ids["owner_id"],
            lang="en",
            values=[(revenue.id, Decimal("50"))],
        )
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["owner_id"])) as client:
            response = await client.get(
                f"{base}/options/{option.id}/sensitivity",
                params={
                    "metric_variable_id": str(revenue.id),
                    "direction": "above",
                    "threshold": "100",
                },
            )
            assert response.json()["evidence"] == {"for_count": 1, "against_count": 1}


async def test_non_member_is_refused_everywhere(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        variable = await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        base, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["outsider_id"])) as client:
            assert (await client.get(variables_path)).status_code == 404
            assert (
                await client.post(
                    variables_path,
                    json={"name": "Nope", "low": "1", "base": "2", "high": "3"},
                )
            ).status_code == 404
            assert (
                await client.patch(
                    f"{variables_path}/{variable.id}",
                    json={"name": "Nope", "low": "1", "base": "2", "high": "3"},
                )
            ).status_code == 404
            assert (await client.delete(f"{variables_path}/{variable.id}")).status_code == 404
            assert (
                await client.get(f"{base}/options/{option.id}/scenario-runs")
            ).status_code == 404
            assert (
                await client.get(
                    f"{base}/options/{option.id}/sensitivity",
                    params={
                        "metric_variable_id": str(variable.id),
                        "direction": "above",
                        "threshold": "1",
                    },
                )
            ).status_code == 404


async def test_uninvolved_member_cannot_write(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        option = await _option(session, space.id, ids["owner_id"])
        _, variables_path = _paths(ids["workspace_id"], space.id)
        base, _ = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["uninvolved_id"])) as client:
            refused = await client.post(
                variables_path,
                json={"name": "CTR", "low": "1", "base": "2", "high": "3"},
            )
            assert refused.status_code == 403
            runs_refused = await client.post(
                f"{base}/options/{option.id}/scenario-runs",
                json={"level": "base", "assumptions": "Steady"},
            )
            assert runs_refused.status_code == 403
            # reading stays available to every member of the workspace
            assert (await client.get(variables_path)).status_code == 200


async def test_scenarios_stay_inside_their_space(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await _variable(session, space.id, "CTR", low="1", base="2", high="3")
        async with _client(session, url, str(ids["outsider_id"])) as client:
            response = await client.get(
                f"/workspaces/{ids['other_workspace_id']}/decision-spaces/{space.id}"
                f"/scenario-variables"
            )
            assert response.status_code == 404


async def test_participant_can_write(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        await PostgresDecisionSpaces(session).add_participant(space.id, ids["participant_id"])
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, str(ids["participant_id"])) as client:
            created = await client.post(
                variables_path,
                json={"name": "CPC", "low": "1", "base": "2", "high": "3"},
            )
            assert created.status_code == 201


async def test_unauthenticated_request_is_unauthorized(scenario_database):
    engine, url = scenario_database
    async with _tx(engine) as session:
        ids = await _seed(session)
        space = await _space(session, ids["workspace_id"], ids["owner_id"])
        _, variables_path = _paths(ids["workspace_id"], space.id)
        async with _client(session, url, None) as client:
            assert (await client.get(variables_path)).status_code == 401
