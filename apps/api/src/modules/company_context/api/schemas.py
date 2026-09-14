from typing import ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

ContextState = Literal["active", "archived"]


class CompanyProfileFields(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    business_model: str | None = None
    products_services: str | None = None
    customer_segments: str | None = None
    markets: str | None = None
    structure: str | None = None


class CompanyProfileWrite(CompanyProfileFields):
    """Write payload for the company profile (all fields optional, replaced wholesale)."""


class CompanyProfileResponse(CompanyProfileFields):
    model_config = ConfigDict(from_attributes=True)

    lang: Literal["fr", "en"] | None = None


class ObjectiveCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class _RejectsExplicitNulls(BaseModel):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> _RejectsExplicitNulls:
        for field in self.non_nullable_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ObjectiveUpdate(_RejectsExplicitNulls):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ("title", "state", "priority")

    title: str | None = Field(default=None, min_length=1, max_length=300)
    state: ContextState | None = None
    priority: bool | None = None


class ObjectiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    state: ContextState
    priority: bool
    lang: Literal["fr", "en"]


class CompanyConstraintCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    detail: str | None = None


class CompanyConstraintUpdate(_RejectsExplicitNulls):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ("title", "state")

    title: str | None = Field(default=None, min_length=1, max_length=300)
    detail: str | None = None
    state: ContextState | None = None


class CompanyConstraintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    detail: str | None = None
    state: ContextState
    lang: Literal["fr", "en"]


class CompanyContextResponse(BaseModel):
    profile: CompanyProfileResponse
    objectives: list[ObjectiveResponse]
    constraints: list[CompanyConstraintResponse]
