from uuid import UUID


def can_read_space(workspace_id: UUID, memberships: frozenset[UUID]) -> bool:
    """A decision space is readable to members of its workspace only."""
    return workspace_id in memberships


def can_transition_space(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """The owner and the participants drive the lifecycle; nobody else writes."""
    return actor_id == owner_id or actor_id in participant_ids


def can_manage_participants(owner_id: UUID, actor_id: UUID) -> bool:
    """Only the owner shapes participation."""
    return actor_id == owner_id


def can_remove_participant(owner_id: UUID, target_id: UUID) -> bool:
    """The owner is a participant by construction and cannot be removed."""
    return target_id != owner_id
