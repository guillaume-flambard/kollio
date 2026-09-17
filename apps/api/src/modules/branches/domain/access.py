from uuid import UUID


def can_read_branch(
    visibility: str,
    workspace_id: UUID,
    memberships: frozenset[UUID],
    creator_id: UUID,
    actor_id: UUID,
) -> bool:
    """A private Branch reads only for its creator; a shared one for Space readers."""
    if workspace_id not in memberships:
        return False
    if visibility == "private":
        return actor_id == creator_id
    return True


def can_write_branch(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Proposing and confirming follow the Space write rule: owner plus participants."""
    return actor_id == owner_id or actor_id in participant_ids
