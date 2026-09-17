from typing import Final

RELATION_TYPES: Final[frozenset[str]] = frozenset(
    {
        "SUPPORTS",
        "CONTRADICTS",
        "DUPLICATES",
        "ALTERNATIVE_TO",
        "DERIVED_FROM",
        "SUPERSEDES",
        "EVIDENCE_FOR",
        "EVIDENCE_AGAINST",
    }
)


class RelationTypeError(ValueError):
    """Raised when a relation type is outside the closed set."""


class RelationLinkError(ValueError):
    """Raised when a relation's ends cannot link (self-relation)."""


def validate_relation_type(value: str) -> str:
    if value not in RELATION_TYPES:
        raise RelationTypeError(f"Unknown relation type: {value}")
    return value


def validate_relation_ends(from_id: str, to_id: str) -> tuple[str, str]:
    if from_id == to_id:
        raise RelationLinkError("A contribution cannot relate to itself")
    return from_id, to_id
