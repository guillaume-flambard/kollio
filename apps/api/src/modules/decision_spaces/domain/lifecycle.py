from typing import Final

DECISION_SPACE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "OPEN",
        "EXPLORING",
        "CONVERGING",
        "READY_TO_DECIDE",
        "DECIDED",
        "TESTING",
        "LEARNED",
        "REOPENED",
    }
)

DECLARED_TRANSITIONS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("OPEN", "EXPLORING"),
        ("EXPLORING", "CONVERGING"),
        ("CONVERGING", "READY_TO_DECIDE"),
        ("READY_TO_DECIDE", "DECIDED"),
        ("DECIDED", "TESTING"),
        ("TESTING", "LEARNED"),
        ("DECIDED", "REOPENED"),
        ("TESTING", "REOPENED"),
        ("LEARNED", "REOPENED"),
        ("REOPENED", "EXPLORING"),
    }
)

REOPENING_TRANSITIONS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("DECIDED", "REOPENED"),
        ("TESTING", "REOPENED"),
        ("LEARNED", "REOPENED"),
    }
)


class DecisionSpaceStatusError(ValueError):
    """Raised when a decision space status is outside the closed set."""


class DecisionSpaceTransitionError(ValueError):
    """Raised when a status transition is not in the declared set."""


def validate_status(value: str) -> str:
    if value not in DECISION_SPACE_STATUSES:
        raise DecisionSpaceStatusError(f"Unknown decision space status: {value}")
    return value


def can_transition(from_status: str, to_status: str) -> bool:
    return (from_status, to_status) in DECLARED_TRANSITIONS


def reopen_requires_reason(from_status: str, to_status: str) -> bool:
    return (from_status, to_status) in REOPENING_TRANSITIONS
