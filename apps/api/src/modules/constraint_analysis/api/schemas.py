from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.constraint_analysis.domain.models import (
    AnalysisEvidence,
    ConstraintAnalysisResult,
)


class LaunchAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    evidence: list[AnalysisEvidence] = Field(default_factory=list, max_length=50)


class ReviewAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    approved: bool


class AnalysisWorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    source_iteration_id: UUID | None
    locale: Literal["fr", "en"]
    status: Literal[
        "queued",
        "running",
        "awaiting_review",
        "review_queued",
        "completed",
        "rejected",
        "failed",
    ]
    current_step: str
    draft_result: ConstraintAnalysisResult | None
    error_code: str | None
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None
