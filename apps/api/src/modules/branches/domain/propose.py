from typing import Final

CONTRIBUTION_KINDS: Final[frozenset[str]] = frozenset(
    {"idea", "claim", "evidence", "objection", "constraint"}
)

CONTRIBUTION_STATUSES: Final[frozenset[str]] = frozenset({"suggested", "confirmed"})


class ContributionKindError(ValueError):
    """Raised when a contribution kind is outside the closed set."""


class ContributionProposalError(ValueError):
    """Raised when a contribution proposal has no usable title."""


def validate_kind(value: str) -> str:
    if value not in CONTRIBUTION_KINDS:
        raise ContributionKindError(f"Unknown contribution kind: {value}")
    return value


def validate_proposal_title(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ContributionProposalError("A contribution proposal needs a title")
    return cleaned


def initial_status(*, is_human: bool) -> str:
    """A human proposal is canonical at once; an AI suggestion waits for confirmation."""
    return "confirmed" if is_human else "suggested"
