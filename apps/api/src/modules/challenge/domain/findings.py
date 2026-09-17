from src.modules.challenge.domain.vocabularies import validate_origin


class FindingShapeError(ValueError):
    """Raised when a finding has no usable statement."""


def validate_detail(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise FindingShapeError("A finding states what could make us regret the decision")
    return cleaned


def arriving_status(origin: str) -> str:
    """A person stating an objection is canonical; a proposal waits for a human."""
    return "confirmed" if validate_origin(origin) == "human" else "proposed"
