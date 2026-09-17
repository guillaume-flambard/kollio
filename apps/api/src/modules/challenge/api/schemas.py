from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ChallengeKind = Literal[
    "unsupported_assumption",
    "contradictory_evidence",
    "hidden_dependency",
    "failure_mode",
    "causal_claim",
    "missing_success_criteria",
]

FindingSeverity = Literal["low", "medium", "high"]
FindingOrigin = Literal["human", "critic"]
FindingStatus = Literal["proposed", "confirmed", "dismissed"]
RunStatus = Literal["OPEN", "RUNNING", "COMPLETED", "FAILED"]
FindingResolution = Literal["confirmed", "dismissed"]


class ChallengeRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    option_id: UUID
    status: RunStatus
    opened_by: UUID
    model: str | None = None
    failure_reason: str | None = None
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class ChallengeFindingCreate(BaseModel):
    kind: ChallengeKind
    severity: FindingSeverity
    detail: str = Field(min_length=1)
    contribution_id: UUID | None = None


class FindingResolutionRequest(BaseModel):
    resolution: FindingResolution


class ChallengeFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    kind: ChallengeKind
    severity: FindingSeverity
    detail: str
    origin: FindingOrigin
    status: FindingStatus
    contribution_id: UUID | None = None
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class ChallengeCoverageResponse(BaseModel):
    covered: list[ChallengeKind]
    uncovered: list[ChallengeKind]


class ChallengeRunDetailResponse(BaseModel):
    run: ChallengeRunResponse
    findings: list[ChallengeFindingResponse]
    coverage: ChallengeCoverageResponse


class ChallengeListResponse(BaseModel):
    runs: list[ChallengeRunResponse]
    findings: list[ChallengeFindingResponse]
    coverage: ChallengeCoverageResponse
