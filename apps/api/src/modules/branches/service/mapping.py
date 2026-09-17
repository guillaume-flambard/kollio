from uuid import UUID

from src.modules.branches.adapters.postgres import Branch, PostgresBranches
from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces


class MappingNotFoundError(LookupError):
    """Raised when the workspace or idea is not visible to the requester.

    Public ideas have no workspace, so from any workspace they do not exist;
    mapping one therefore creates nothing and leaves it untouched.
    """


async def map_idea(
    branches: PostgresBranches,
    spaces: PostgresDecisionSpaces,
    workspace_id: UUID,
    idea_id: UUID,
    subject: str,
) -> tuple[Branch, bool]:
    """Map a workspace Idea to a Branch under a new parent Space.

    Returns the Branch and whether it was created (False when the Idea
    already had one — the mapping is idempotent).
    """
    if workspace_id not in await branches.memberships(subject):
        raise MappingNotFoundError
    idea = await branches.idea(idea_id)
    if idea is None or idea.workspace_id != workspace_id:
        raise MappingNotFoundError
    existing = await branches.branch_for_idea(idea_id)
    if existing is not None:
        return existing, False
    space = await spaces.create(
        workspace_id=workspace_id,
        question=idea.title,
        description=idea.pitch,
        deadline=None,
        owner_id=idea.owner_id,
        lang=idea.lang,
    )
    branch = await branches.create_branch(
        space_id=space.id,
        title=idea.title,
        summary=idea.pitch,
        visibility="shared",
        created_by=idea.owner_id,
        source_idea_id=idea.id,
        lang=idea.lang,
    )
    return branch, True
