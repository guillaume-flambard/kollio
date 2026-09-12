from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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


class IdeaSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    pitch: str
    stage: Literal["seed", "iterating", "team_formed"]
    lang: Literal["fr", "en"]
    created_at: datetime


class IdeaPageResponse(BaseModel):
    items: list[IdeaSummaryResponse]
    total: int
    limit: int
    offset: int
