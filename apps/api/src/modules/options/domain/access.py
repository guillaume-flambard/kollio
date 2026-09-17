from uuid import UUID


def can_read_options(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """Options are readable to members of the owning workspace only."""
    return workspace_id in memberships


def can_write_options(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Building options follows the Space write rule: owner plus participants."""
    return actor_id == owner_id or actor_id in participant_ids
