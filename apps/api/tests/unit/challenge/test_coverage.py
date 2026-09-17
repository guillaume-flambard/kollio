from src.modules.challenge.domain.coverage import compute_coverage
from src.modules.challenge.domain.vocabularies import CHALLENGE_KINDS


def test_a_confirmed_finding_covers_its_kind():
    result = compute_coverage([("failure_mode", "confirmed")])
    assert result.covered == frozenset({"failure_mode"})
    assert result.uncovered == CHALLENGE_KINDS - {"failure_mode"}


def test_a_proposed_finding_also_covers_its_kind():
    result = compute_coverage([("causal_claim", "proposed")])
    assert "causal_claim" in result.covered


def test_a_dismissed_finding_does_not_cover():
    result = compute_coverage([("hidden_dependency", "dismissed")])
    assert result.covered == frozenset()
    assert result.uncovered == CHALLENGE_KINDS


def test_a_dismissed_finding_does_not_hide_a_confirmed_one_of_the_same_kind():
    result = compute_coverage(
        [("hidden_dependency", "dismissed"), ("hidden_dependency", "confirmed")]
    )
    assert result.covered == frozenset({"hidden_dependency"})


def test_coverage_always_names_every_kind():
    result = compute_coverage([])
    assert result.covered == frozenset()
    assert result.uncovered == CHALLENGE_KINDS
    assert result.covered | result.uncovered == CHALLENGE_KINDS


def test_several_kinds_are_reported_together():
    result = compute_coverage(
        [
            ("unsupported_assumption", "confirmed"),
            ("missing_success_criteria", "proposed"),
            ("failure_mode", "dismissed"),
        ]
    )
    assert result.covered == frozenset({"unsupported_assumption", "missing_success_criteria"})
    assert "failure_mode" in result.uncovered
