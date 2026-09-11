from uuid import UUID


def can_read_idea(workspace_id: UUID | None, memberships: frozenset[UUID]) -> bool:
    return workspace_id is None or workspace_id in memberships
