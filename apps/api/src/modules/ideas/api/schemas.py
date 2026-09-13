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


class DepositIdeaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    pitch: str = Field(min_length=1, max_length=5000)
    lang: Literal["fr", "en"] | None = None


class IdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    title: str
    pitch: str
    owner_id: UUID
    workspace_id: UUID | None
    stage: Literal["seed", "iterating", "team_formed"]
    lang: Literal["fr", "en"]
    visibility: Literal["public", "workspace"]
    created_at: datetime
    legacy_context: LegacyIdeaContext | None = None
    collaborators: list[CollaboratorResponse] = Field(default_factory=list)


class IdeaSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    pitch: str
    stage: Literal["seed", "iterating", "team_formed"]
    lang: Literal["fr", "en"]
    created_at: datetime
    domain: str | None = None
    collaborators: list[CollaboratorResponse] = Field(default_factory=list)


class IdeaPageResponse(BaseModel):
    items: list[IdeaSummaryResponse]
    total: int
    limit: int
    offset: int
