from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
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
    embedding_model: str = "kollio-embedding"
    embedding_source_model: str = "text-embedding-3-large"
    embedding_dimensions: Literal[1536] = 1536
    otel_exporter_otlp_traces_endpoint: str = ""
    otel_exporter_otlp_headers: SecretStr = SecretStr("")

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if value and not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        return value

    @property
    def checkpoint_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
