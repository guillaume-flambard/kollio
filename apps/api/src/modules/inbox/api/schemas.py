from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.decision_spaces.api.schemas import DecisionSpaceStatus

InboxKind = Literal[
    "space_needs_convergence",
    "contribution_awaits_confirmation",
    "finding_awaits_resolution",
    "decision_awaits_commitment",
    "experiment_awaits_outcome",
    "learning_awaits_confirmation",
]


class InboxEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: InboxKind
    workspace_id: UUID
    space_id: UUID
    space_question: str
    space_status: DecisionSpaceStatus
    subject_id: UUID | None = None
    detail: str | None = None
    created_at: datetime


class InboxSectionResponse(BaseModel):
    entries: list[InboxEntryResponse]
    total: int


class DecisionInboxResponse(BaseModel):
    """What needs the reader's attention: four of the five section 4 questions.

    Relevant prior memory is absent because the capability that surfaces prior
    confirmed Learnings with their provenance is not built. An empty section
    would assert that no relevant memory exists, which nothing supports today.
    """

    needs_convergence: InboxSectionResponse
    needs_my_input: InboxSectionResponse
    ready_to_decide: InboxSectionResponse
    needs_learning: InboxSectionResponse
