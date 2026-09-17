from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExperimentCreateBody(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    hypothesis: str = Field(min_length=1)
    success_metric: str = Field(min_length=1, max_length=300)
    baseline: str | None = Field(default=None, max_length=200)
    target: str | None = Field(default=None, max_length=200)
    decision_space_id: UUID | None = None
    option_id: UUID | None = None


class ExperimentStatusBody(BaseModel):
    status: str


class OutcomeCreateBody(BaseModel):
    metric: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1, max_length=200)
    unit: str | None = Field(default=None, max_length=50)
    observed_at: date | None = None
    comment: str | None = None
    qualitative: str | None = None


class LearningWriteBody(BaseModel):
    text: str | None = None
    confirm: bool = False


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    decision_space_id: UUID | None = None
    option_id: UUID | None = None
    title: str
    hypothesis: str
    success_metric: str
    baseline: str | None
    target: str | None
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime


class OutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    experiment_id: UUID
    metric: str
    value: str
    unit: str | None
    observed_at: date | None
    comment: str | None
    qualitative: str | None
    created_at: datetime


class LearningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    experiment_id: UUID
    idea_id: UUID
    status: str
    text: str
    outcome_ids: list[str]
    confirmed_by_id: UUID | None
    created_at: datetime
    updated_at: datetime


class ExperimentDetailResponse(BaseModel):
    experiment: ExperimentResponse
    outcomes: list[OutcomeResponse]
    learning: LearningResponse | None
