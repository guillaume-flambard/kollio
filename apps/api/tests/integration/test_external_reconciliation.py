import os
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.ideas.adapters.postgres import User, Workspace, WorkspaceMembership
from src.modules.reconciliation.adapters.postgres import PostgresReconciliation

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def reconciliation_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine
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


async def _seed_space(session, workspace_name: str):
    workspace_id, owner_id = uuid4(), uuid4()
    session.add_all(
        [
            Workspace(id=workspace_id, name=workspace_name),
            User(id=owner_id, auth_subject=str(owner_id), display_name="Owner"),
            WorkspaceMembership(workspace_id=workspace_id, user_id=owner_id, role="member"),
        ]
    )
    await session.flush()
    space = await PostgresDecisionSpaces(session).create(
        workspace_id=workspace_id,
        question="Which direction should we take?",
        description=None,
        deadline=None,
        owner_id=owner_id,
        lang="en",
    )
    return space, owner_id


async def test_source_revisions_are_retained_and_isolated_by_decision_space(
    reconciliation_database,
):
    async with _tx(reconciliation_database) as session:
        first_space, owner_id = await _seed_space(session, "First workspace")
        second_space, _ = await _seed_space(session, "Second workspace")
        sources = PostgresReconciliation(session)

        material = await sources.create_material(
            space_id=first_space.id,
            title="Friday synthesis",
            stated_author="Jean-Pierre",
            origin_label="ChatGPT",
            visibility="shared",
            created_by=owner_id,
            lang="fr",
        )
        first = await sources.append_revision(
            material_id=material.id,
            body="Prioritize a self-service launch.",
            created_by=owner_id,
            lang="en",
        )
        await sources.append_revision(
            material_id=material.id,
            body="Prioritize a self-service launch with onboarding support.",
            created_by=owner_id,
            lang="en",
        )

        revisions = await sources.list_revisions(first_space.id, material.id)
        assert [(revision.sequence, revision.body) for revision in revisions] == [
            (1, "Prioritize a self-service launch."),
            (2, "Prioritize a self-service launch with onboarding support."),
        ]
        assert first.body == "Prioritize a self-service launch."
        assert await sources.list_revisions(second_space.id, material.id) == []


async def test_reconciliation_resolutions_append_without_changing_source_excerpts(
    reconciliation_database,
):
    async with _tx(reconciliation_database) as session:
        space, owner_id = await _seed_space(session, "Decision workspace")
        sources = PostgresReconciliation(session)
        material = await sources.create_material(
            space_id=space.id,
            title="Two proposals",
            stated_author="Corinne",
            origin_label="Manual import",
            visibility="shared",
            created_by=owner_id,
            lang="fr",
        )
        revision = await sources.append_revision(
            material_id=material.id,
            body="Keep the concierge path. Keep the self-service path.",
            created_by=owner_id,
            lang="en",
        )
        left = await sources.create_excerpt(
            revision_id=revision.id,
            body="Keep the concierge path.",
            start_offset=0,
            end_offset=24,
            created_by=owner_id,
        )
        right = await sources.create_excerpt(
            revision_id=revision.id,
            body="Keep the self-service path.",
            start_offset=25,
            end_offset=52,
            created_by=owner_id,
        )

        resolution = await sources.append_resolution(
            space_id=space.id,
            left_excerpt_id=left.id,
            right_excerpt_id=right.id,
            outcome="combine",
            rationale="Use a concierge path for launch, then guide users to self-service.",
            created_by=owner_id,
        )

        assert resolution.outcome == "combine"
        assert (await sources.excerpt(space.id, left.id)).body == "Keep the concierge path."
        assert (await sources.excerpt(space.id, right.id)).body == "Keep the self-service path."
        assert [item.id for item in await sources.list_resolutions(space.id)] == [resolution.id]


async def test_resolution_cannot_link_an_excerpt_from_another_decision_space(
    reconciliation_database,
):
    async with _tx(reconciliation_database) as session:
        first_space, owner_id = await _seed_space(session, "First workspace")
        second_space, second_owner_id = await _seed_space(session, "Second workspace")
        sources = PostgresReconciliation(session)
        first_material = await sources.create_material(
            space_id=first_space.id,
            title="First source",
            stated_author="Jean-Pierre",
            origin_label="ChatGPT",
            visibility="shared",
            created_by=owner_id,
            lang="fr",
        )
        second_material = await sources.create_material(
            space_id=second_space.id,
            title="Second source",
            stated_author="Corinne",
            origin_label="ChatGPT",
            visibility="shared",
            created_by=second_owner_id,
            lang="fr",
        )
        first_revision = await sources.append_revision(
            material_id=first_material.id, body="First claim.", created_by=owner_id, lang="en"
        )
        second_revision = await sources.append_revision(
            material_id=second_material.id,
            body="Second claim.",
            created_by=second_owner_id,
            lang="en",
        )
        first_excerpt = await sources.create_excerpt(
            revision_id=first_revision.id,
            body="First claim.",
            start_offset=0,
            end_offset=12,
            created_by=owner_id,
        )
        second_excerpt = await sources.create_excerpt(
            revision_id=second_revision.id,
            body="Second claim.",
            start_offset=0,
            end_offset=13,
            created_by=second_owner_id,
        )

        with pytest.raises(ValueError, match="belong to the decision space"):
            await sources.append_resolution(
                space_id=first_space.id,
                left_excerpt_id=first_excerpt.id,
                right_excerpt_id=second_excerpt.id,
                outcome="cannot_combine",
                rationale="The second source belongs to a different decision space.",
                created_by=owner_id,
            )
