from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FactorName = Literal[
    "competition",
    "build_cost",
    "time_to_market",
    "defensibility",
    "acquisition",
]

EXPECTED_FACTORS: frozenset[str] = frozenset(
    {"competition", "build_cost", "time_to_market", "defensibility", "acquisition"}
)


class AnalysisEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(min_length=1)
    url: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ConstraintFactor(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: FactorName
    score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    source_ids: list[str]


class ConstraintAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    overall_score: int = Field(ge=0, le=100)
    verdict: Literal["viable", "conditional", "not_viable", "unknown"]
    summary: str = Field(min_length=1)
    factors: list[ConstraintFactor] = Field(min_length=5, max_length=5)
    locale: Literal["fr", "en"]

    @model_validator(mode="after")
    def require_all_factors(self) -> ConstraintAnalysisResult:
        names = [factor.name for factor in self.factors]
        if len(set(names)) != len(names) or set(names) != EXPECTED_FACTORS:
            raise ValueError("Each required constraint factor must appear exactly once")
        return self


def validate_analysis_result(
    result: ConstraintAnalysisResult,
    *,
    requested_locale: str,
    evidence_ids: frozenset[str],
) -> ConstraintAnalysisResult:
    if result.locale != requested_locale:
        raise ValueError("The model returned the wrong locale")
    cited_ids = {source_id for factor in result.factors for source_id in factor.source_ids}
    if not cited_ids.issubset(evidence_ids):
        raise ValueError("The model cited unknown evidence")
    if result.verdict != "unknown" and not cited_ids:
        raise ValueError("A non-unknown verdict requires evidence")
    return result
