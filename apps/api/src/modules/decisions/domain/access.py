from uuid import UUID


def can_read_record(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """A decision record is readable to members of its workspace only."""
    return workspace_id in memberships


def can_commit_decision(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Committing follows the space write rule: owner plus participants."""
    return actor_id == owner_id or actor_id in participant_ids
