from typing import Final

INITIATIVE_TYPES: Final[frozenset[str]] = frozenset(
    {
        "idea",
        "hypothesis",
        "campaign",
        "opportunity",
        "decision",
        "experiment",
        "pricing",
        "market",
        "partnership",
        "internal_improvement",
    }
)


class InitiativeTypeError(ValueError):
    """Raised when an initiative type is outside the closed list."""


def validate_initiative_type(value: str) -> str:
    if value not in INITIATIVE_TYPES:
        raise InitiativeTypeError(f"Unknown initiative type: {value}")
    return value
