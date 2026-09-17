from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

BranchVisibility = Literal["private", "shared"]
ContributionKind = Literal["idea", "claim", "evidence", "objection", "constraint"]
ContributionStatus = Literal["suggested", "confirmed"]


class BranchCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str | None = None
    visibility: BranchVisibility


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    title: str
    summary: str | None = None
    source_idea_id: UUID | None = None
    visibility: BranchVisibility
    created_by: UUID
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class BranchListResponse(BaseModel):
    items: list[BranchResponse]


class ContributionPropose(BaseModel):
    branch_id: UUID
    kind: ContributionKind
    title: str = Field(min_length=1, max_length=300)
    body: str | None = None
    source: str | None = None
    tool_model: str | None = Field(default=None, max_length=200)
    transformation_history: dict | None = None


class ContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    branch_id: UUID
    kind: ContributionKind
    title: str
    body: str | None = None
    author_id: UUID
    source: str | None = None
    tool_model: str | None = None
    transformation_history: dict | None = None
    status: ContributionStatus
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class ContributionListResponse(BaseModel):
    items: list[ContributionResponse]
