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


ConstraintKey = Literal["concurrence", "cout", "temps", "defendabilite", "acquisition"]


class ConstraintScore(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    score: int | None = Field(default=None, ge=0, le=100)
    note: str = Field(min_length=1)


class ConstraintAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    realism_score: int | None = Field(default=None, ge=0, le=100)
    concurrence: ConstraintScore
    cout: ConstraintScore
    temps: ConstraintScore
    defendabilite: ConstraintScore
    acquisition: ConstraintScore
    locale: Literal["fr", "en"]
    source_ids: list[str]
    established_facts: list[str]

    @property
    def constraints(self) -> dict[str, ConstraintScore]:
        return {
            "concurrence": self.concurrence,
            "cout": self.cout,
            "temps": self.temps,
            "defendabilite": self.defendabilite,
            "acquisition": self.acquisition,
        }
