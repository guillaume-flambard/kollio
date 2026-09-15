from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")
    environment: Literal["development", "test", "production"] = "development"
    database_url: str = ""
    redis_url: str = "redis://localhost:63799/0"
    logto_issuer: str = ""
    logto_jwks_url: str = ""
    logto_audience: str = "https://kollio.memolabs.dev/api"
    llm_base_url: str = "http://localhost:4000/v1"
    llm_api_key: SecretStr = SecretStr("")
    llm_model: str = "kollio-default"
    llm_model_visible: str = ""
    llm_request_timeout_seconds: float = 600.0
    embedding_model: str = "kollio-embedding-local"
    embedding_source_model: str = "intfloat/multilingual-e5-small"
    embedding_dimensions: Literal[1536, 384] = 384
    embedding_query_prefix: str = "query: "
    embedding_passage_prefix: str = "passage: "
    otel_exporter_otlp_traces_endpoint: str = ""
    otel_exporter_otlp_headers: SecretStr = SecretStr("")

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if value and not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        return value

    @field_validator("embedding_dimensions", mode="before")
    @classmethod
    def dimensions_arrive_as_text(cls, value: object) -> object:
        # Environment variables are always text and a Literal of integers matches
        # types exactly, so EMBEDDING_DIMENSIONS=1536 used to be rejected before
        # any check could run, which took the whole API down at import. Coerce the
        # text form and let the Literal rule decide membership.
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value
        return value

    @field_validator("llm_request_timeout_seconds")
    @classmethod
    def timeout_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("llm_request_timeout_seconds must be positive")
        return value

    @model_validator(mode="after")
    def require_production_integrations(self) -> Settings:
        if self.environment != "production":
            return self
        missing: list[str] = []
        if not self.database_url:
            missing.append("database_url")
        if not self.redis_url or "localhost" in self.redis_url:
            missing.append("redis_url")
        if not self.logto_issuer:
            missing.append("logto_issuer")
        if not self.logto_jwks_url:
            missing.append("logto_jwks_url")
        if not self.llm_base_url or "localhost" in self.llm_base_url:
            missing.append("llm_base_url")
        if not self.llm_api_key.get_secret_value():
            missing.append("llm_api_key")
        if not self.otel_exporter_otlp_traces_endpoint:
            missing.append("otel_exporter_otlp_traces_endpoint")
        if not self.otel_exporter_otlp_headers.get_secret_value():
            missing.append("otel_exporter_otlp_headers")
        if missing:
            raise ValueError(f"Missing production configuration: {', '.join(missing)}")
        return self

    @property
    def checkpoint_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
