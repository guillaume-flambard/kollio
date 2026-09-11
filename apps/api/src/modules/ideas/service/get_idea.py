from uuid import UUID

from src.modules.ideas.adapters.postgres import Idea, PostgresIdeas
from src.modules.ideas.domain.permissions import can_read_idea


async def get_idea(repository: PostgresIdeas, idea_id: UUID, subject: str) -> Idea | None:
    idea = await repository.get(idea_id)
    if idea is None:
        return None
    memberships = await repository.memberships(subject)
    return idea if can_read_idea(idea.workspace_id, memberships) else None
