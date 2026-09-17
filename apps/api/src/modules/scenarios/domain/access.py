from uuid import UUID


def can_read_scenarios(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """Scenarios are readable to members of the space's workspace only."""
    return workspace_id in memberships


def can_write_scenarios(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Variables, runs and values follow the space write rule."""
    return actor_id == owner_id or actor_id in participant_ids
