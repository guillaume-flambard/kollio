from collections.abc import Iterable
from dataclasses import dataclass

from src.modules.challenge.domain.vocabularies import CHALLENGE_KINDS


@dataclass(frozen=True)
class Coverage:
    covered: frozenset[str]
    uncovered: frozenset[str]


def compute_coverage(findings: Iterable[tuple[str, str]]) -> Coverage:
    """Which of the six checks carry a finding that has not been dismissed.

    Takes (kind, status) pairs so the rule stays independent of persistence.
    """
    covered = {kind for kind, status in findings if status != "dismissed"}
    return Coverage(covered=frozenset(covered), uncovered=CHALLENGE_KINDS - covered)
