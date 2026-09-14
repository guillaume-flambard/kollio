from uuid import UUID


def can_access_context(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """Company context is visible and editable to members of its workspace only."""
    return workspace_id in memberships
