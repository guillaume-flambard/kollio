from typing import Final
from uuid import UUID

RECORD_SIDES: Final[frozenset[str]] = frozenset({"for", "against"})


class RecordFieldError(ValueError):
    """Raised when a record field is missing or contradicts another."""


class RecordSideError(ValueError):
    """Raised when an argument side is outside the closed set."""


def validate_rationale(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise RecordFieldError("a decision record needs a rationale")
    return cleaned


def validate_side(value: str) -> str:
    if value not in RECORD_SIDES:
        raise RecordSideError(f"Unknown argument side: {value}")
    return value


def validate_alternatives(option_ids: list[UUID], selected_option_id: UUID) -> list[UUID]:
    """A rejected alternative is what was not chosen, so the chosen one cannot appear."""
    if selected_option_id in option_ids:
        raise RecordFieldError("the selected option cannot also be a rejected alternative")
    return list(option_ids)
