from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LegacyIdeaContext(BaseModel):
    source: str
    source_id: str
    domain: str | None = None
    verdict: str | None = None
    fatal_constraint: str | None = None
    channel: str | None = None
    why_now: str | None = None


class CollaboratorResponse(BaseModel):
    id: UUID
    handle: str | None = None
    display_name: str
    role: str
    roles: list[str]
    bio: str | None = None
    avatar_key: str | None = None


class AnalysisResponse(BaseModel):
    state: Literal["resolved", "abstained", "running", "unavailable"]
    iteration_id: UUID | None = None
    realism_score: int | None = None
    constraints: dict[str, dict] = Field(default_factory=dict)
    locale: Literal["fr", "en"] | None = None
    model: str | None = None
    created_at: datetime | None = None


InitiativeType = Literal[
    "idea",
    "hypothesis",
    "campaign",
    "opportunity",
    "decision",
    "experiment",
    "pricing",
    "market",
    "partnership",
    "internal_improvement",
]


class DepositIdeaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    pitch: str = Field(min_length=1, max_length=5000)
    lang: Literal["fr", "en"] | None = None
    initiative_type: InitiativeType = "idea"


class UpdateIdeaInitiativeTypeRequest(BaseModel):
    initiative_type: InitiativeType


class IdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    title: str
    pitch: str
    owner_id: UUID
    workspace_id: UUID | None
    stage: Literal["seed", "iterating", "team_formed"]
    initiative_type: InitiativeType
    lang: Literal["fr", "en"]
    visibility: Literal["public", "workspace"]
    created_at: datetime
    analysis: AnalysisResponse | None = None
    sought_roles: list[str] = Field(default_factory=list)
    join_requests: list[JoinRequestResponse] = Field(default_factory=list)
    legacy_context: LegacyIdeaContext | None = None
    collaborators: list[CollaboratorResponse] = Field(default_factory=list)


class IdeaSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    pitch: str
    stage: Literal["seed", "iterating", "team_formed"]
    initiative_type: InitiativeType
    lang: Literal["fr", "en"]
    created_at: datetime
    sought_roles: list[str] = Field(default_factory=list)
    realism_score: int | None = None
    last_activity_at: datetime | None = None
    collaborators: list[CollaboratorResponse] = Field(default_factory=list)


class IdeaPageResponse(BaseModel):
    items: list[IdeaSummaryResponse]
    total: int
    limit: int
    offset: int


class ApplyJoinBody(BaseModel):
    role: str = Field(min_length=1, max_length=20)
    note: str = Field(min_length=1, max_length=500)


class RejectJoinBody(BaseModel):
    rationale: str = Field(min_length=1, max_length=500)


class JoinRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    idea_id: UUID
    requester_id: UUID
    role: str
    note: str
    status: Literal["pending", "accepted", "rejected"]
    rationale: str | None = None
    created_at: datetime
