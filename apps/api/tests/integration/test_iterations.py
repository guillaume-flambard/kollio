import os
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings
from src.platform.db import get_session

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def iteration_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for Postgres integration tests")
    if not url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("Integration tests require a dedicated kollio_test database")
    engine = create_async_engine(url)
    yield engine, url
    await engine.dispose()


async def test_iteration_lifecycle_is_versioned_and_workspace_isolated(iteration_database):
    engine, url = iteration_database
    workspace_id, owner_id, member_id, outsider_id, idea_id = (uuid4() for _ in range(5))
    subject = {"value": str(owner_id)}

    async with engine.connect() as connection:
        transaction = await connection.begin()
        local = async_sessionmaker(connection, expire_on_commit=False)
        async with local() as session:
            session.add_all(
                [
                    Workspace(id=workspace_id, name="Iteration workspace"),
                    User(id=owner_id, auth_subject=str(owner_id), display_name="Idea owner"),
                    User(id=member_id, auth_subject=str(member_id), display_name="Idea member"),
                    User(id=outsider_id, auth_subject=str(outsider_id), display_name="Outsider"),
                ]
            )
            await session.flush()
            session.add_all(
                [
                    WorkspaceMembership(
                        workspace_id=workspace_id,
                        user_id=owner_id,
                        role="admin",
                    ),
                    WorkspaceMembership(
                        workspace_id=workspace_id,
                        user_id=member_id,
                        role="member",
                    ),
                    Idea(
                        id=idea_id,
                        slug="versioned-idea",
                        title="Initial title",
                        pitch="Initial pitch",
                        owner_id=owner_id,
                        workspace_id=workspace_id,
                        stage="seed",
                        lang="en",
                        visibility="workspace",
                    ),
                ]
            )
            await session.flush()

            app = create_app(Settings(_env_file=None, database_url=url))
            app.dependency_overrides[current_identity] = lambda: Identity(subject["value"])

            async def override_session():
                yield session

            app.dependency_overrides[get_session] = override_session
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                initial = await client.post(
                    f"/ideas/{idea_id}/iterations",
                    json={
                        "message": "Create initial product snapshot",
                        "lang": "en",
                        "snapshot": {
                            "title": "Initial title",
                            "pitch": "Initial pitch",
                            "stage": "seed",
                        },
                    },
                )
                assert initial.status_code == 201
                initial_id = initial.json()["id"]

                subject["value"] = str(member_id)
                denied_main = await client.post(
                    f"/ideas/{idea_id}/iterations",
                    json={
                        "message": "Overwrite main",
                        "lang": "en",
                        "expected_parent_id": initial_id,
                        "snapshot": {
                            "title": "Denied",
                            "pitch": "Denied",
                            "stage": "iterating",
                        },
                    },
                )
                assert denied_main.status_code == 403

                proposal = await client.post(
                    f"/ideas/{idea_id}/iterations",
                    json={
                        "message": "Clarify the customer problem",
                        "lang": "en",
                        "branch": "proposal/customer-problem",
                        "expected_parent_id": initial_id,
                        "snapshot": {
                            "title": "Focused title",
                            "pitch": "Focused pitch",
                            "stage": "iterating",
                        },
                    },
                )
                assert proposal.status_code == 201
                assert proposal.json()["proposal_status"] == "pending"
                proposal_id = proposal.json()["id"]
                assert (await session.get(Idea, idea_id)).title == "Initial title"

                refined_proposal = await client.post(
                    f"/ideas/{idea_id}/iterations",
                    json={
                        "message": "Refine the customer problem",
                        "lang": "en",
                        "branch": "proposal/customer-problem",
                        "expected_parent_id": proposal_id,
                        "snapshot": {
                            "title": "Focused title",
                            "pitch": "Focused pitch with evidence",
                            "stage": "iterating",
                        },
                    },
                )
                assert refined_proposal.status_code == 201
                refined_proposal_id = refined_proposal.json()["id"]

                denied_accept = await client.post(
                    f"/ideas/{idea_id}/iterations/{refined_proposal_id}/accept",
                    json={"expected_main_parent_id": initial_id},
                )
                assert denied_accept.status_code == 403

                subject["value"] = str(owner_id)
                stale_branch_accept = await client.post(
                    f"/ideas/{idea_id}/iterations/{proposal_id}/accept",
                    json={"expected_main_parent_id": initial_id},
                )
                assert stale_branch_accept.status_code == 409

                stale_accept = await client.post(
                    f"/ideas/{idea_id}/iterations/{refined_proposal_id}/accept",
                    json={"expected_main_parent_id": None},
                )
                assert stale_accept.status_code == 409

                accepted = await client.post(
                    f"/ideas/{idea_id}/iterations/{refined_proposal_id}/accept",
                    json={"expected_main_parent_id": initial_id},
                )
                assert accepted.status_code == 201
                accepted_id = accepted.json()["id"]
                assert accepted.json()["parent_id"] == initial_id
                assert (await session.get(Idea, idea_id)).pitch == "Focused pitch with evidence"
                stored_proposal = await session.get(Iteration, proposal_id)
                assert stored_proposal.proposal_status == "accepted"

                restored = await client.post(
                    f"/ideas/{idea_id}/iterations/{initial_id}/rollback",
                    json={
                        "expected_main_parent_id": accepted_id,
                        "message": "Restore the initial scope",
                        "lang": "en",
                    },
                )
                assert restored.status_code == 201
                assert restored.json()["parent_id"] == accepted_id
                assert (await session.get(Idea, idea_id)).title == "Initial title"
                restored_id = restored.json()["id"]

                subject["value"] = str(member_id)
                rejected_proposal = await client.post(
                    f"/ideas/{idea_id}/iterations",
                    json={
                        "message": "Explore another audience",
                        "lang": "en",
                        "branch": "proposal/another-audience",
                        "expected_parent_id": restored_id,
                        "snapshot": {
                            "title": "Alternative audience",
                            "pitch": "Alternative pitch",
                            "stage": "iterating",
                        },
                    },
                )
                assert rejected_proposal.status_code == 201
                rejected_proposal_id = rejected_proposal.json()["id"]

                subject["value"] = str(owner_id)
                rejected = await client.post(
                    f"/ideas/{idea_id}/iterations/{rejected_proposal_id}/reject",
                    json={"rationale": "Offline-first belongs on the main line instead."},
                )
                assert rejected.status_code == 200
                assert rejected.json()["proposal_status"] == "rejected"
                assert (
                    rejected.json()["rationale"]
                    == "Offline-first belongs on the main line instead."
                )
                assert (await session.get(Idea, idea_id)).title == "Initial title"

                subject["value"] = str(member_id)
                history = await client.get(f"/ideas/{idea_id}/iterations")
                assert history.status_code == 200
                assert len(history.json()) == 6

                subject["value"] = str(outsider_id)
                hidden = await client.get(f"/ideas/{idea_id}/iterations")
                assert hidden.status_code == 404
                assert "Focused pitch" not in hidden.text

            stored = list(
                (
                    await session.scalars(
                        select(Iteration)
                        .where(Iteration.idea_id == idea_id)
                        .order_by(Iteration.revision)
                    )
                ).all()
            )
            assert len(stored) == 6
            assert [item.revision for item in stored] == [1, 2, 3, 4, 5, 6]
            assert [item.branch for item in stored].count("main") == 3
        await transaction.rollback()
