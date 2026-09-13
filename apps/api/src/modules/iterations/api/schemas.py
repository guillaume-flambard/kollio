from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.ideas.api.schemas import AnalysisResponse


class IdeaSnapshot(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    pitch: str = Field(min_length=1, max_length=12_000)
    stage: Literal["seed", "iterating", "team_formed"]


class CreateIterationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    lang: Literal["fr", "en"]
    snapshot: IdeaSnapshot
    branch: str = Field(
        default="main",
        pattern=r"^(main|proposal/[a-z0-9][a-z0-9._-]{0,47})$",
    )
    expected_parent_id: UUID | None = None


class ResolveProposalRequest(BaseModel):
    expected_main_parent_id: UUID | None = None


class RejectProposalRequest(BaseModel):
    rationale: str = Field(min_length=1, max_length=500)


class RollbackRequest(BaseModel):
    expected_main_parent_id: UUID | None = None
    message: str = Field(min_length=1, max_length=500)
    lang: Literal["fr", "en"]


class IterationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    parent_id: UUID | None
    author_id: UUID
    message: str
    lang: Literal["fr", "en"]
    payload: IdeaSnapshot
    branch: str
    proposal_status: Literal["pending", "accepted", "rejected"] | None
    rationale: str | None = None
    short_hash: str
    revision: int
    created_at: datetime
    analysis: AnalysisResponse | None = None
