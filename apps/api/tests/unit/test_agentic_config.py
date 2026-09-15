import pytest
from pydantic import ValidationError

from src.platform.config import Settings


def test_production_agentic_runtime_fails_closed_without_required_configuration() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(
            _env_file=None,
            environment="production",
            database_url="",
            redis_url="",
            logto_issuer="",
            logto_jwks_url="",
            llm_base_url="",
            llm_api_key="",
            otel_exporter_otlp_traces_endpoint="",
            otel_exporter_otlp_headers="",
        )

    message = str(error.value)
    for field in (
        "logto_issuer",
        "logto_jwks_url",
        "database_url",
        "redis_url",
        "llm_base_url",
        "llm_api_key",
        "otel_exporter_otlp_traces_endpoint",
        "otel_exporter_otlp_headers",
    ):
        assert field in message


def test_development_runtime_allows_provider_free_deterministic_tests() -> None:
    settings = Settings(_env_file=None, environment="development", database_url="")

    assert settings.llm_model == "kollio-default"
    assert settings.embedding_model == "kollio-embedding-local"
    assert settings.embedding_source_model == "intfloat/multilingual-e5-small"
    assert settings.embedding_dimensions == 384


def test_openai_embedding_space_stays_explicitly_configurable() -> None:
    settings = Settings(
        _env_file=None,
        environment="development",
        database_url="",
        embedding_model="kollio-embedding",
        embedding_source_model="text-embedding-3-large",
        embedding_dimensions=1536,
        embedding_query_prefix="",
        embedding_passage_prefix="",
    )

    assert settings.embedding_model == "kollio-embedding"
    assert settings.embedding_dimensions == 1536


def test_complete_production_agentic_runtime_configuration_is_accepted() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        database_url="postgresql+asyncpg://kollio:secret@postgres:5432/kollio",
        redis_url="redis://redis:6379/0",
        logto_issuer="https://auth.example.test/oidc",
        logto_jwks_url="https://auth.example.test/oidc/jwks",
        llm_base_url="http://litellm:4000/v1",
        llm_api_key="gateway-key",
        otel_exporter_otlp_traces_endpoint="https://traces.example.test/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
    )

    assert settings.environment == "production"
