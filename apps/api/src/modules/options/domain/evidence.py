from typing import Final

EVIDENCE_SIDES: Final[frozenset[str]] = frozenset({"for", "against"})


class EvidenceSideError(ValueError):
    """Raised when an evidence side is outside the closed set."""


def validate_side(value: str) -> str:
    if value not in EVIDENCE_SIDES:
        raise EvidenceSideError(f"Unknown evidence side: {value}")
    return value
