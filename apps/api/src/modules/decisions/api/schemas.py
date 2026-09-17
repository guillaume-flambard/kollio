from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ArgumentSide = Literal["for", "against"]
TriggerDirection = Literal["above", "below"]


class RevisitTrigger(BaseModel):
    metric: str = Field(min_length=1, max_length=200)
    direction: TriggerDirection | None = None
    threshold: str | None = Field(default=None, max_length=200)
    note: str | None = None


class DecisionArgumentWrite(BaseModel):
    contribution_id: UUID
    side: ArgumentSide


class DecisionCommit(BaseModel):
    selected_option_id: UUID
    rationale: str = Field(min_length=1)
    critical_assumptions: str | None = None
    uncertainty: str | None = None
    success_criteria: str | None = None
    revisit_triggers: list[RevisitTrigger] | None = None
    rejected_option_ids: list[UUID] = Field(default_factory=list)
    arguments: list[DecisionArgumentWrite] = Field(default_factory=list)


class DecisionArgumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contribution_id: UUID
    side: ArgumentSide


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    version: int
    selected_option_id: UUID
    rationale: str
    critical_assumptions: str | None = None
    uncertainty: str | None = None
    success_criteria: str | None = None
    revisit_triggers: list[RevisitTrigger] | None = None
    reviewer_ids: list[UUID]
    decided_by: UUID
    lang: Literal["fr", "en"]
    created_at: datetime
    rejected_option_ids: list[UUID]
    arguments: list[DecisionArgumentResponse]


class DecisionListResponse(BaseModel):
    items: list[DecisionResponse]
