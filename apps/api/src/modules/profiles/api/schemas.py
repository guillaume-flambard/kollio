from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OwnedIdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    title: str
    stage: Literal["seed", "iterating", "team_formed"]
    lang: Literal["fr", "en"]
    created_at: datetime


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idea_id: UUID
    idea_title: str
    role: str


class ContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idea_id: UUID
    idea_title: str
    message: str
    lang: Literal["fr", "en"]
    short_hash: str
    created_at: datetime


class ProfileResponse(BaseModel):
    id: UUID
    display_name: str
    handle: str | None = None
    roles: list[str]
    bio: str | None = None
    avatar_key: str | None = None
    owned_ideas: list[OwnedIdeaResponse]
    memberships: list[MembershipResponse]
    contributions: list[ContributionResponse]
