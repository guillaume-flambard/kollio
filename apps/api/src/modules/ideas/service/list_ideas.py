from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.ideas.adapters.postgres import Idea, PostgresIdeas
from src.modules.ideas.domain.permissions import can_read_idea


@dataclass(frozen=True)
class IdeaSlice:
    items: list[Idea]
    total: int
    realism_scores: dict[UUID, int | None]
    last_activity: dict[UUID, datetime | None]


async def list_workspace_ideas(
    repository: PostgresIdeas,
    workspace_id: UUID,
    subject: str,
    limit: int,
    offset: int,
    query_text: str | None = None,
    stage: str | None = None,
    sought_role: str | None = None,
    realism_min: int | None = None,
) -> IdeaSlice | None:
    memberships = await repository.memberships(subject)
    if not can_read_idea(workspace_id, memberships):
        return None
    items, total, realism_scores, last_activity = await repository.list_for_workspace(
        workspace_id,
        limit,
        offset,
        query_text=query_text,
        stage=stage,
        sought_role=sought_role,
        realism_min=realism_min,
    )
    return IdeaSlice(
        items=items,
        total=total,
        realism_scores=realism_scores,
        last_activity=last_activity,
    )
