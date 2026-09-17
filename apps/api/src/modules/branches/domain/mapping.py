from uuid import UUID


def is_mappable(*, workspace_id: UUID | None, source_idea_id: UUID | None) -> bool:
    """A workspace Idea without a Branch yet can be mapped.

    Public Ideas have no parent Space, and an already-mapped Idea is skipped.
    """
    return workspace_id is not None and source_idea_id is None
