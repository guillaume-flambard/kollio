from uuid import UUID


def can_read_challenge(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """A challenge is readable to members of the workspace that owns the Space."""
    return workspace_id in memberships


def can_write_challenge(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Challenging follows the Space write rule: the owner plus the participants."""
    return actor_id == owner_id or actor_id in participant_ids
