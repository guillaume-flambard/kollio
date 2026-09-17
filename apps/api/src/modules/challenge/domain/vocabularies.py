from typing import Final

CHALLENGE_KINDS: Final[frozenset[str]] = frozenset(
    {
        "unsupported_assumption",
        "contradictory_evidence",
        "hidden_dependency",
        "failure_mode",
        "causal_claim",
        "missing_success_criteria",
    }
)

FINDING_SEVERITIES: Final[frozenset[str]] = frozenset({"low", "medium", "high"})

FINDING_ORIGINS: Final[frozenset[str]] = frozenset({"human", "critic"})

FINDING_STATUSES: Final[frozenset[str]] = frozenset({"proposed", "confirmed", "dismissed"})

RUN_STATUSES: Final[frozenset[str]] = frozenset({"OPEN", "RUNNING", "COMPLETED", "FAILED"})


class ChallengeVocabularyError(ValueError):
    """Raised when a value is outside one of the closed challenge vocabularies."""


def _validate(value: str, allowed: frozenset[str], label: str) -> str:
    if value not in allowed:
        raise ChallengeVocabularyError(f"Unknown {label}: {value}")
    return value


def validate_kind(value: str) -> str:
    return _validate(value, CHALLENGE_KINDS, "challenge kind")


def validate_severity(value: str) -> str:
    return _validate(value, FINDING_SEVERITIES, "severity")


def validate_origin(value: str) -> str:
    return _validate(value, FINDING_ORIGINS, "origin")


def validate_finding_status(value: str) -> str:
    return _validate(value, FINDING_STATUSES, "finding status")


def validate_run_status(value: str) -> str:
    return _validate(value, RUN_STATUSES, "run status")
