from uuid import UUID


def can_read_map(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """The map reads for members of its workspace only."""
    return workspace_id in memberships


def can_write_map(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """The map writes for the owner and the participants; nobody else."""
    return actor_id == owner_id or actor_id in participant_ids
