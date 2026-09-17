from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DecisionSpaceStatus = Literal[
    "OPEN",
    "EXPLORING",
    "CONVERGING",
    "READY_TO_DECIDE",
    "DECIDED",
    "TESTING",
    "LEARNED",
    "REOPENED",
]


class DecisionSpaceCreate(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    description: str | None = None
    deadline: date | None = None


class DecisionSpaceTransition(BaseModel):
    to_status: DecisionSpaceStatus
    reason: str | None = None


class ParticipantAdd(BaseModel):
    user_id: UUID


class DecisionSpaceParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    created_at: datetime


class DecisionSpaceStatusEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: DecisionSpaceStatus | None = None
    to_status: DecisionSpaceStatus
    actor_id: UUID
    reason: str | None = None
    created_at: datetime


class DecisionSpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    question: str
    description: str | None = None
    owner_id: UUID
    status: DecisionSpaceStatus
    deadline: date | None = None
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class DecisionSpaceDetailResponse(DecisionSpaceResponse):
    participants: list[DecisionSpaceParticipantResponse]
    history: list[DecisionSpaceStatusEventResponse]


class DecisionSpaceListResponse(BaseModel):
    items: list[DecisionSpaceResponse]
