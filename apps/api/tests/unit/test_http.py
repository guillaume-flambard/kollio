import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.platform.config import Settings


@pytest.mark.parametrize(
    "path",
    [
        "/ideas/00000000-0000-0000-0000-000000000001",
        "/workspaces",
        "/workspaces/00000000-0000-0000-0000-000000000001/ideas",
    ],
)
def test_unauthenticated_idea_request_is_localized(path):
    with TestClient(create_app(Settings(_env_file=None, database_url=""))) as client:
        response = client.get(
            path,
            headers={"Accept-Language": "en-GB,en;q=0.9,fr;q=0.1"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Sign in required"
        assert response.headers["Content-Language"] == "en"


def test_liveness_does_not_require_database():
    with TestClient(create_app(Settings(_env_file=None, database_url=""))) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 503
