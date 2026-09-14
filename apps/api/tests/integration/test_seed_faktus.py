import os

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.modules.company_context.adapters.postgres import (
    CompanyMetric,
    CompanyObjective,
    CompanyPrinciple,
)
from src.modules.ideas.adapters.postgres import Idea, Workspace, WorkspaceMembership
from src.platform.seed_faktus import (
    FAKTUS_WORKSPACE_ID,
    IDEA_ID,
    reset_faktus,
    seed_faktus,
)

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def seed_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine
    await engine.dispose()


async def test_faktus_seed_is_deterministic_and_idempotent(seed_database):
    async with seed_database.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            first = await seed_faktus(session)
            second = await seed_faktus(session)

            assert first == second
            assert first["workspace"] == 1
            assert (
                first["objectives"]
                == first["constraints"]
                == first["principles"]
                == first["metrics"]
            )

            workspace = await session.get(Workspace, FAKTUS_WORKSPACE_ID)
            assert workspace is not None and workspace.name == "Faktus"
            idea = await session.get(Idea, IDEA_ID)
            assert idea is not None and idea.workspace_id == FAKTUS_WORKSPACE_ID

            objective_count = await session.scalar(
                select(func.count())
                .select_from(CompanyObjective)
                .where(CompanyObjective.workspace_id == FAKTUS_WORKSPACE_ID)
            )
            principle_count = await session.scalar(
                select(func.count())
                .select_from(CompanyPrinciple)
                .where(CompanyPrinciple.workspace_id == FAKTUS_WORKSPACE_ID)
            )
            metric_count = await session.scalar(
                select(func.count())
                .select_from(CompanyMetric)
                .where(CompanyMetric.workspace_id == FAKTUS_WORKSPACE_ID)
            )
            assert objective_count == first["objectives"]
            assert principle_count == first["principles"]
            assert metric_count == first["metrics"]

            await reset_faktus(session)
            remaining_members = await session.scalar(
                select(func.count())
                .select_from(WorkspaceMembership)
                .where(WorkspaceMembership.workspace_id == FAKTUS_WORKSPACE_ID)
            )
            assert remaining_members == 0
            assert await session.get(Idea, IDEA_ID) is None
        await transaction.rollback()
