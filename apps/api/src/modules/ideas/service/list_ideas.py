from uuid import UUID

from src.modules.ideas.adapters.postgres import Idea, PostgresIdeas
from src.modules.ideas.domain.permissions import can_read_idea


async def list_workspace_ideas(
    repository: PostgresIdeas,
    workspace_id: UUID,
    subject: str,
    limit: int,
    offset: int,
    query_text: str | None = None,
    stage: str | None = None,
    domain: str | None = None,
) -> tuple[list[Idea], int] | None:
    memberships = await repository.memberships(subject)
    if not can_read_idea(workspace_id, memberships):
        return None
    return await repository.list_for_workspace(
        workspace_id,
        limit,
        offset,
        query_text=query_text,
        stage=stage,
        domain=domain,
    )
