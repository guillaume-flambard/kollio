from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RelationType = Literal[
    "SUPPORTS",
    "CONTRADICTS",
    "DUPLICATES",
    "ALTERNATIVE_TO",
    "DERIVED_FROM",
    "SUPERSEDES",
    "EVIDENCE_FOR",
    "EVIDENCE_AGAINST",
]


class RelationCreate(BaseModel):
    from_contribution_id: UUID
    to_contribution_id: UUID
    relation_type: RelationType


class RelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    from_contribution_id: UUID
    to_contribution_id: UUID
    relation_type: RelationType
    created_by: UUID
    created_at: datetime


class ClusterCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class ClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    title: str
    created_by: UUID
    created_at: datetime
    member_ids: list[UUID] = Field(default_factory=list)


class ClusterMemberAdd(BaseModel):
    contribution_id: UUID


class MapContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    branch_id: UUID
    kind: str
    title: str
    status: str
    author_id: UUID
    cluster_id: UUID | None = None


class MapResponse(BaseModel):
    contributions: list[MapContributionResponse]
    relations: list[RelationResponse]
    clusters: list[ClusterResponse]
