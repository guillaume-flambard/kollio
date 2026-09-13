from uuid import UUID


def can_read_profile(
    person_workspace_ids: frozenset[UUID], viewer_workspace_ids: frozenset[UUID]
) -> bool:
    """A member sees a profile only when they share at least one workspace."""
    return bool(person_workspace_ids & viewer_workspace_ids)
