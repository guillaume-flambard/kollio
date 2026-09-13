import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import create_app
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.platform.auth import Identity, current_identity
from src.platform.config import Settings

pytestmark = [pytest.mark.e2e, pytest.mark.integration]

API_DIR = Path(__file__).resolve().parents[2]
TASKIQ_BIN = str(Path(os.sys.executable).with_name("taskiq"))

FACTOR_NAMES = (
    "competition",
    "build_cost",
    "time_to_market",
    "defensibility",
    "acquisition",
)


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []
    paths: list[str] = []
    authorizations: list[str] = []

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        self.requests.append(payload)
        self.paths.append(self.path)
        self.authorizations.append(self.headers["Authorization"])
        system_prompt = payload["messages"][0]["content"]
        locale = "fr" if "locale fr" in system_prompt else "en"
        result = {
            "overall_score": 50,
            "verdict": "unknown",
            "summary": "More evidence is required.",
            "factors": [
                {
                    "name": name,
                    "score": 50,
                    "summary": "No evidence was supplied.",
                    "source_ids": [],
                }
                for name in FACTOR_NAMES
            ],
            "locale": locale,
        }
        content = "{}" if len(self.requests) == 1 else json.dumps(result)
        response = json.dumps({"choices": [{"message": {"content": content}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        return


async def wait_for_status(
    client: httpx.AsyncClient,
    path: str,
    expected: str,
    *,
    max_wait_seconds: float = 20,
) -> dict[str, object]:
    deadline = asyncio.get_running_loop().time() + max_wait_seconds
    last_response: dict[str, object] = {}
    while asyncio.get_running_loop().time() < deadline:
        response = await client.get(path)
        assert response.status_code == 200
        last_response = response.json()
        if last_response["status"] == expected:
            return last_response
        await asyncio.sleep(0.1)
    pytest.fail(f"Workflow did not reach {expected}; last response: {last_response}")


async def test_api_worker_graph_and_checkpoint_complete_one_reviewed_analysis() -> None:
    database_url = os.environ.get("TEST_DATABASE_URL")
    redis_url = os.environ.get("REDIS_URL")
    if not database_url or not redis_url:
        pytest.skip("TEST_DATABASE_URL and REDIS_URL are required for agentic E2E tests")
    if not database_url.rsplit("/", 1)[-1].startswith("kollio_test"):
        raise ValueError("E2E tests require a dedicated kollio_test database")

    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    FakeOpenAIHandler.requests = []
    FakeOpenAIHandler.paths = []
    FakeOpenAIHandler.authorizations = []
    model_url = f"http://127.0.0.1:{server.server_port}/v1"

    engine = create_async_engine(database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    workspace_id, owner_id, idea_id = (uuid4() for _ in range(3))
    async with sessions() as session:
        session.add_all(
            [
                Workspace(id=workspace_id, name="Agentic E2E workspace"),
                User(id=owner_id, auth_subject=str(owner_id), display_name="E2E owner"),
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
                Idea(
                    id=idea_id,
                    slug=f"agentic-e2e-{idea_id}",
                    title="A provider-free agent test",
                    pitch="Verify every local agent boundary.",
                    owner_id=owner_id,
                    workspace_id=workspace_id,
                    stage="seed",
                    lang="en",
                    visibility="workspace",
                ),
            ]
        )
        await session.commit()

    checkpoint_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    async with AsyncPostgresSaver.from_conn_string(checkpoint_url) as saver:
        await saver.setup()

    worker_environment = {
        **os.environ,
        "ENVIRONMENT": "test",
        "DATABASE_URL": database_url,
        "REDIS_URL": redis_url,
        "LLM_BASE_URL": model_url,
        "LLM_API_KEY": "provider-free-test-key",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT": "",
        "OTEL_EXPORTER_OTLP_HEADERS": "",
    }
    worker = await asyncio.create_subprocess_exec(
        TASKIQ_BIN,
        "worker",
        "src.platform.worker:broker",
        "--workers",
        "1",
        "--log-level",
        "WARNING",
        cwd=API_DIR,
        env=worker_environment,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

    settings = Settings(
        _env_file=None,
        environment="test",
        database_url=database_url,
        redis_url=redis_url,
        llm_base_url=model_url,
        llm_api_key="provider-free-test-key",
    )
    app = create_app(settings)
    app.dependency_overrides[current_identity] = lambda: Identity(str(owner_id))
    try:
        await asyncio.sleep(0.5)
        assert worker.returncode is None
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                launched = await client.post(
                    f"/ideas/{idea_id}/analyses",
                    json={"evidence": []},
                    headers={"Idempotency-Key": f"e2e-{uuid4()}", "Accept-Language": "en"},
                )
                assert launched.status_code == 202
                workflow_id = UUID(launched.json()["id"])
                path = f"/ideas/{idea_id}/analyses/{workflow_id}"

                awaiting_review = await wait_for_status(client, path, "awaiting_review")
                assert awaiting_review["draft_result"]["locale"] == "en"

                reviewed = await client.post(f"{path}/review", json={"approved": True})
                assert reviewed.status_code == 202
                completed = await wait_for_status(client, path, "completed")
                assert completed["draft_result"]["verdict"] == "unknown"

        assert len(FakeOpenAIHandler.requests) == 2
        request = FakeOpenAIHandler.requests[-1]
        assert request["model"] == "kollio-default"
        assert request["response_format"]["type"] == "json_schema"
        assert FakeOpenAIHandler.paths == ["/v1/chat/completions"] * 2
        assert FakeOpenAIHandler.authorizations == ["Bearer provider-free-test-key"] * 2
    finally:
        worker.terminate()
        try:
            async with asyncio.timeout(5):
                await worker.wait()
        except TimeoutError:
            worker.kill()
            await worker.wait()
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
        await engine.dispose()
