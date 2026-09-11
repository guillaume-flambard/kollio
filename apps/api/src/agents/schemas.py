from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    url: str
    text: str


class GateFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    verdict: Literal["pass", "kill", "unknown"]
    reason: str = Field(min_length=1)
    source_ids: list[str]
    established_facts: list[str]
    locale: Literal["fr", "en"]
