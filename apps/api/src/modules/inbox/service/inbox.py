from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.inbox.adapters.postgres import InboxRow, PostgresInbox
from src.modules.inbox.domain.sections import inbox_order_key

DEFAULT_LIMIT = 20
MAX_LIMIT = 50


class InboxNotFoundError(LookupError):
    """Raised when the authenticated subject has no account."""


class InboxValidationError(ValueError):
    """Raised when the requested limit is out of range."""


@dataclass(frozen=True)
class InboxSection:
    entries: list[InboxRow]
    total: int


@dataclass(frozen=True)
class InboxSnapshot:
    needs_convergence: InboxSection
    needs_my_input: InboxSection
    ready_to_decide: InboxSection
    needs_learning: InboxSection


def _order_key(row: InboxRow) -> tuple[datetime, UUID]:
    return inbox_order_key((row.created_at, row.subject_id or row.space_id))


def _section(rows: list[InboxRow], limit: int) -> InboxSection:
    ordered = sorted(rows, key=_order_key)
    return InboxSection(entries=ordered[:limit], total=len(ordered))


async def read_inbox(
    repository: PostgresInbox, subject: str, *, limit: int | None = None
) -> InboxSnapshot:
    """Assemble what waits on the reader, longest wait first, bounded per section."""
    resolved = DEFAULT_LIMIT if limit is None else limit
    if resolved < 1 or resolved > MAX_LIMIT:
        raise InboxValidationError(f"The limit must be between 1 and {MAX_LIMIT}")

    user = await repository.user_for_subject(subject)
    if user is None:
        raise InboxNotFoundError

    workspace_ids = await repository.memberships(subject)
    answered_by_me = await repository.spaces_answered_by(subject)

    my_input = [
        *await repository.suggested_contributions(answered_by_me),
        *await repository.proposed_findings(answered_by_me),
    ]
    learning = [
        *await repository.completed_experiments_without_outcome(workspace_ids),
        *await repository.draft_learnings(workspace_ids),
    ]

    return InboxSnapshot(
        needs_convergence=_section(await repository.converging_spaces(workspace_ids), resolved),
        needs_my_input=_section(my_input, resolved),
        ready_to_decide=_section(await repository.ready_spaces(workspace_ids), resolved),
        needs_learning=_section(learning, resolved),
    )
