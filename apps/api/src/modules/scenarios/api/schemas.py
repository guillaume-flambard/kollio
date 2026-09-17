from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer


def _plain(value: Decimal) -> Decimal:
    """Drop the stored column scale's trailing zeros without exponent notation."""
    normalized = value.normalize()
    if normalized == normalized.to_integral_value():
        return normalized.quantize(Decimal(1))
    return normalized


PlainDecimal = Annotated[Decimal, PlainSerializer(_plain, return_type=Decimal)]

ScenarioRunLevel = Literal["optimistic", "base", "pessimistic", "failure"]
CriterionDirection = Literal["above", "below"]
SensitivityStatus = Literal["found", "beyond_declared_range", "insufficient_points"]
Travel = Literal["up", "down", "flat"]


class ScenarioVariableWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    unit: str | None = Field(default=None, max_length=40)
    low: Decimal
    base: Decimal
    high: Decimal


class ScenarioVariableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    name: str
    unit: str | None = None
    low: PlainDecimal
    base: PlainDecimal
    high: PlainDecimal
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class ScenarioVariableListResponse(BaseModel):
    items: list[ScenarioVariableResponse]


class RunValueWrite(BaseModel):
    variable_id: UUID
    value: Decimal


class RunValueResponse(BaseModel):
    variable_id: UUID
    value: PlainDecimal


class ScenarioRunWrite(BaseModel):
    level: ScenarioRunLevel
    assumptions: str = Field(min_length=1)
    values: list[RunValueWrite] = Field(default_factory=list)


class ScenarioRunResponse(BaseModel):
    id: UUID
    option_id: UUID
    level: ScenarioRunLevel
    assumptions: str
    created_by: UUID
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime
    values: list[RunValueResponse]


class ScenarioRunListResponse(BaseModel):
    items: list[ScenarioRunResponse]


class SensitivityVariableResponse(BaseModel):
    variable_id: UUID
    status: SensitivityStatus
    interval: tuple[PlainDecimal, PlainDecimal] | None = None
    crossing: PlainDecimal | None = None
    crossings: int
    slope_min: PlainDecimal | None = None
    slope_max: PlainDecimal | None = None
    travel: Travel | None = None


class SensitivityCriterionResponse(BaseModel):
    metric_variable_id: UUID
    direction: CriterionDirection
    threshold: PlainDecimal


class SensitivityEvidenceResponse(BaseModel):
    for_count: int
    against_count: int


class SensitivityResponse(BaseModel):
    """What would change the preference. Never a predicted value."""

    criterion: SensitivityCriterionResponse
    ranked: list[SensitivityVariableResponse]
    incomplete_run_ids: list[UUID]
    evidence: SensitivityEvidenceResponse
