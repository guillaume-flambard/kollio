from datetime import datetime
from typing import ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

EvidenceSide = Literal["for", "against"]


class OptionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    proposal: str = Field(min_length=1)
    mechanism: str | None = None
    upside: str | None = None
    cost: str | None = None
    risks: str | None = None
    critical_assumptions: str | None = None
    success_metrics: str | None = None


class _RejectsExplicitNulls(BaseModel):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> _RejectsExplicitNulls:
        for field in self.non_nullable_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class OptionUpdate(_RejectsExplicitNulls):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ("title", "proposal")

    title: str | None = Field(default=None, min_length=1, max_length=300)
    proposal: str | None = Field(default=None, min_length=1)
    mechanism: str | None = None
    upside: str | None = None
    cost: str | None = None
    risks: str | None = None
    critical_assumptions: str | None = None
    success_metrics: str | None = None


class EvidenceLink(BaseModel):
    contribution_id: UUID
    side: EvidenceSide


class OptionEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contribution_id: UUID
    side: EvidenceSide
    created_at: datetime


class OptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    title: str
    proposal: str
    mechanism: str | None = None
    upside: str | None = None
    cost: str | None = None
    risks: str | None = None
    critical_assumptions: str | None = None
    success_metrics: str | None = None
    created_by: UUID
    lang: Literal["fr", "en"]
    created_at: datetime
    updated_at: datetime


class OptionDetailResponse(OptionResponse):
    evidence: list[OptionEvidenceResponse]


class OptionListResponse(BaseModel):
    items: list[OptionResponse]
