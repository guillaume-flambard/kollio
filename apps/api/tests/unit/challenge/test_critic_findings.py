from uuid import UUID, uuid4

import pytest

from src.modules.challenge.domain.critic import (
    CriticFindingError,
    validate_candidate,
    validate_candidates,
)

CITED = UUID("00000000-0000-0000-0000-0000000000e1")
OTHER = UUID("00000000-0000-0000-0000-0000000000e2")
ALLOWED = frozenset({CITED})


def _raw(**overrides):
    payload = {
        "kind": "unsupported_assumption",
        "severity": "medium",
        "detail": "Assumes churn stays flat while pricing doubles.",
        "contribution_id": None,
    }
    payload.update(overrides)
    return payload


def test_a_complete_finding_is_accepted():
    finding = validate_candidate(_raw(), allowed_contribution_ids=ALLOWED)
    assert finding.kind == "unsupported_assumption"
    assert finding.severity == "medium"
    assert finding.detail == "Assumes churn stays flat while pricing doubles."
    assert finding.contribution_id is None


def test_a_statement_is_trimmed():
    finding = validate_candidate(
        _raw(detail="  Spaces are not significant.  "), allowed_contribution_ids=ALLOWED
    )
    assert finding.detail == "Spaces are not significant."


@pytest.mark.parametrize(
    "kind",
    [
        "unsupported_assumption",
        "contradictory_evidence",
        "hidden_dependency",
        "failure_mode",
        "causal_claim",
        "missing_success_criteria",
    ],
)
def test_every_declared_check_is_accepted(kind: str):
    assert validate_candidate(_raw(kind=kind), allowed_contribution_ids=ALLOWED).kind == kind


@pytest.mark.parametrize("kind", ["", "risk", "UNSUPPORTED_ASSUMPTION", "hunch"])
def test_an_unknown_check_is_refused(kind: str):
    with pytest.raises(CriticFindingError):
        validate_candidate(_raw(kind=kind), allowed_contribution_ids=ALLOWED)


@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_every_declared_severity_is_accepted(severity: str):
    assert (
        validate_candidate(_raw(severity=severity), allowed_contribution_ids=ALLOWED).severity
        == severity
    )


@pytest.mark.parametrize("severity", ["", "critical", "HIGH", "urgent"])
def test_an_unknown_severity_is_refused(severity: str):
    with pytest.raises(CriticFindingError):
        validate_candidate(_raw(severity=severity), allowed_contribution_ids=ALLOWED)


@pytest.mark.parametrize("detail", ["", "   "])
def test_a_blank_statement_is_refused(detail: str):
    with pytest.raises(CriticFindingError):
        validate_candidate(_raw(detail=detail), allowed_contribution_ids=ALLOWED)


def test_a_missing_field_is_refused():
    for missing in ("kind", "severity", "detail"):
        payload = _raw()
        del payload[missing]
        with pytest.raises(CriticFindingError):
            validate_candidate(payload, allowed_contribution_ids=ALLOWED)


def test_a_citation_from_the_brief_is_kept():
    finding = validate_candidate(_raw(contribution_id=str(CITED)), allowed_contribution_ids=ALLOWED)
    assert finding.contribution_id == CITED


def test_a_citation_outside_the_brief_is_refused():
    with pytest.raises(CriticFindingError):
        validate_candidate(_raw(contribution_id=str(OTHER)), allowed_contribution_ids=ALLOWED)


def test_a_citation_that_is_not_an_identifier_is_refused():
    with pytest.raises(CriticFindingError):
        validate_candidate(_raw(contribution_id="the first one"), allowed_contribution_ids=ALLOWED)


def test_an_empty_citation_is_read_as_no_citation():
    for empty in (None, ""):
        assert (
            validate_candidate(
                _raw(contribution_id=empty), allowed_contribution_ids=ALLOWED
            ).contribution_id
            is None
        )


def test_a_set_of_findings_is_checked_as_a_whole():
    findings = validate_candidates(
        [_raw(), _raw(kind="causal_claim", severity="high")],
        allowed_contribution_ids=ALLOWED,
    )
    assert len(findings) == 2


def test_one_bad_finding_refuses_the_whole_set():
    with pytest.raises(CriticFindingError):
        validate_candidates([_raw(), _raw(kind="hunch")], allowed_contribution_ids=ALLOWED)


def test_no_findings_is_an_empty_set_not_an_error():
    assert validate_candidates([], allowed_contribution_ids=ALLOWED) == ()


def test_candidate_findings_compare_by_value():
    assert validate_candidate(_raw(), allowed_contribution_ids=ALLOWED) == validate_candidate(
        _raw(), allowed_contribution_ids=ALLOWED
    )
    assert validate_candidate(
        _raw(detail=f"Distinct {uuid4()}"), allowed_contribution_ids=ALLOWED
    ) != validate_candidate(_raw(), allowed_contribution_ids=ALLOWED)
