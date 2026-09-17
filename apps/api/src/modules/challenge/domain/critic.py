from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from uuid import UUID

from src.modules.challenge.domain.findings import FindingShapeError, validate_detail
from src.modules.challenge.domain.vocabularies import (
    ChallengeVocabularyError,
    validate_kind,
    validate_severity,
)


class CriticFindingError(ValueError):
    """Raised when a finding the Critic returned cannot enter the space as it stands."""


@dataclass(frozen=True)
class CandidateFinding:
    """One finding the Critic returned, once it has been checked.

    A caller that holds one of these holds something storable; a caller that
    gets an exception has a reason to fail the whole run rather than store part of it.
    """

    kind: str
    severity: str
    detail: str
    contribution_id: UUID | None


def _citation(value: object) -> UUID | None:
    if value is None or value == "":
        return None
    try:
        return UUID(str(value))
    except ValueError as error:
        raise CriticFindingError(f"A citation must be an identifier: {value!r}") from error


def validate_candidate(
    raw: Mapping[str, object], *, allowed_contribution_ids: frozenset[UUID]
) -> CandidateFinding:
    try:
        kind = validate_kind(str(raw.get("kind", "")))
        severity = validate_severity(str(raw.get("severity", "")))
        detail = validate_detail(str(raw.get("detail", "")))
    except (ChallengeVocabularyError, FindingShapeError) as error:
        raise CriticFindingError(str(error)) from error

    citation = _citation(raw.get("contribution_id"))
    if citation is not None and citation not in allowed_contribution_ids:
        raise CriticFindingError("A finding cites a contribution that was not in the brief")

    return CandidateFinding(kind=kind, severity=severity, detail=detail, contribution_id=citation)


def validate_candidates(
    raws: Iterable[Mapping[str, object]], *, allowed_contribution_ids: frozenset[UUID]
) -> tuple[CandidateFinding, ...]:
    """Check every returned finding before any of them is stored.

    A run whose result is partly unusable stores nothing: a half-written
    challenge would read as a complete one.
    """
    return tuple(
        validate_candidate(raw, allowed_contribution_ids=allowed_contribution_ids) for raw in raws
    )
