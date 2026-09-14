from typing import Literal
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
    pass


class CompanyProfileResponse(CompanyProfileFields):
    model_config = ConfigDict(from_attributes=True)


class ObjectiveCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class ObjectiveUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    state: ContextState | None = None
    priority: bool | None = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> ObjectiveUpdate:
        for field in ("title", "state", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ObjectiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    state: ContextState
    priority: bool


class ConstraintCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    detail: str | None = None


class ConstraintUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    detail: str | None = None
    state: ContextState | None = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> ConstraintUpdate:
        for field in ("title", "state"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ConstraintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    detail: str | None = None
    state: ContextState


class CompanyContextResponse(BaseModel):
    profile: CompanyProfileResponse
    objectives: list[ObjectiveResponse]
    constraints: list[ConstraintResponse]
