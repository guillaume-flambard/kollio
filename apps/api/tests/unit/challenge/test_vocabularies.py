import pytest

from src.modules.challenge.domain.vocabularies import (
    CHALLENGE_KINDS,
    FINDING_ORIGINS,
    FINDING_SEVERITIES,
    FINDING_STATUSES,
    RUN_STATUSES,
    ChallengeVocabularyError,
    validate_finding_status,
    validate_kind,
    validate_origin,
    validate_run_status,
    validate_severity,
)


def test_the_six_checks_are_the_closed_set():
    assert CHALLENGE_KINDS == frozenset(
        {
            "unsupported_assumption",
            "contradictory_evidence",
            "hidden_dependency",
            "failure_mode",
            "causal_claim",
            "missing_success_criteria",
        }
    )


def test_severities_are_three_values():
    assert FINDING_SEVERITIES == frozenset({"low", "medium", "high"})


def test_origins_separate_human_from_machine():
    assert FINDING_ORIGINS == frozenset({"human", "critic"})


def test_finding_statuses_include_dismissal():
    assert FINDING_STATUSES == frozenset({"proposed", "confirmed", "dismissed"})


def test_run_statuses_are_the_four_declared_ones():
    assert RUN_STATUSES == frozenset({"OPEN", "RUNNING", "COMPLETED", "FAILED"})


@pytest.mark.parametrize("kind", sorted(CHALLENGE_KINDS))
def test_validate_kind_accepts_the_closed_set(kind: str):
    assert validate_kind(kind) == kind


@pytest.mark.parametrize("severity", sorted(FINDING_SEVERITIES))
def test_validate_severity_accepts_the_closed_set(severity: str):
    assert validate_severity(severity) == severity


@pytest.mark.parametrize("origin", sorted(FINDING_ORIGINS))
def test_validate_origin_accepts_the_closed_set(origin: str):
    assert validate_origin(origin) == origin


@pytest.mark.parametrize("status", sorted(RUN_STATUSES))
def test_validate_run_status_accepts_the_closed_set(status: str):
    assert validate_run_status(status) == status


@pytest.mark.parametrize("status", sorted(FINDING_STATUSES))
def test_validate_finding_status_accepts_the_closed_set(status: str):
    assert validate_finding_status(status) == status


@pytest.mark.parametrize("value", ["", "unsupported", "FAILURE_MODE", "weakness", "assumption"])
def test_validate_kind_refuses_anything_outside_the_six(value: str):
    with pytest.raises(ChallengeVocabularyError):
        validate_kind(value)


@pytest.mark.parametrize("value", ["", "critical", "HIGH", "blocker"])
def test_validate_severity_refuses_anything_outside_the_three(value: str):
    with pytest.raises(ChallengeVocabularyError):
        validate_severity(value)


@pytest.mark.parametrize("value", ["", "ai", "HUMAN", "system"])
def test_validate_origin_refuses_anything_outside_the_two(value: str):
    with pytest.raises(ChallengeVocabularyError):
        validate_origin(value)


@pytest.mark.parametrize("value", ["", "open", "DONE", "CANCELLED"])
def test_validate_run_status_refuses_anything_outside_the_four(value: str):
    with pytest.raises(ChallengeVocabularyError):
        validate_run_status(value)


@pytest.mark.parametrize("value", ["", "accepted", "rejected", "open"])
def test_validate_finding_status_refuses_anything_outside_the_three(value: str):
    with pytest.raises(ChallengeVocabularyError):
        validate_finding_status(value)
