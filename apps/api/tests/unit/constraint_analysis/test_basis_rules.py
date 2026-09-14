import pytest
from pydantic import ValidationError

from src.modules.constraint_analysis.domain.models import (
    ConstraintAnalysisResult,
    context_reference_ids,
    validate_analysis_result,
)


def factor(name, basis, score, gap, source_ids):
    return {
        "name": name,
        "basis": basis,
        "score": score,
        "gap": gap,
        "summary": f"{name} summary",
        "source_ids": source_ids,
    }


def result(**overrides):
    payload = {
        "overall_score": 60,
        "verdict": "conditional",
        "summary": "Conditional",
        "factors": [
            factor("competition", "known", 60, None, ["e1"]),
            factor("build_cost", "assumed", 55, None, []),
            factor("time_to_market", "assumed", 50, None, []),
            factor("defensibility", "assumed", 45, None, []),
            factor("acquisition", "assumed", 40, None, []),
        ],
        "contradictions": [],
        "locale": "en",
    }
    payload.update(overrides)
    return payload


def test_an_unknown_factor_carries_no_score_and_names_the_gap():
    payload = result()
    payload["factors"][0] = factor("competition", "unknown", None, "No market study supplied", [])
    parsed = ConstraintAnalysisResult.model_validate(payload)
    assert parsed.factors[0].score is None
    assert parsed.factors[0].gap == "No market study supplied"


def test_an_unknown_factor_with_a_score_is_refused():
    payload = result()
    payload["factors"][0] = factor("competition", "unknown", 50, "gap", [])
    with pytest.raises(ValidationError):
        ConstraintAnalysisResult.model_validate(payload)


def test_an_unknown_factor_without_a_gap_is_refused():
    payload = result()
    payload["factors"][0] = factor("competition", "unknown", None, "  ", [])
    with pytest.raises(ValidationError):
        ConstraintAnalysisResult.model_validate(payload)


def test_a_known_factor_without_cited_evidence_is_refused():
    payload = result()
    payload["factors"][0] = factor("competition", "known", 60, None, [])
    with pytest.raises(ValidationError):
        ConstraintAnalysisResult.model_validate(payload)


def test_an_abstention_carries_no_overall_score_and_no_scored_factor():
    payload = result(
        overall_score=None,
        verdict="unknown",
        factors=[
            factor(name, "unknown", None, "missing", [])
            for name in (
                "competition",
                "build_cost",
                "time_to_market",
                "defensibility",
                "acquisition",
            )
        ],
        contradictions=[],
    )
    parsed = ConstraintAnalysisResult.model_validate(payload)
    assert parsed.overall_score is None


def test_a_scored_verdict_requires_an_overall_score():
    with pytest.raises(ValidationError):
        ConstraintAnalysisResult.model_validate(result(overall_score=None))


def test_a_contradiction_must_reference_a_supplied_context_item():
    payload = result(
        contradictions=[{"target": "constraint", "ref_id": "constraint:9", "detail": "too costly"}]
    )
    parsed = ConstraintAnalysisResult.model_validate(payload)
    with pytest.raises(ValueError):
        validate_analysis_result(
            parsed, requested_locale="en", evidence_ids=frozenset({"e1"}), context_ids=frozenset()
        )
    validate_analysis_result(
        parsed,
        requested_locale="en",
        evidence_ids=frozenset({"e1"}),
        context_ids=frozenset({"constraint:9"}),
    )


def test_context_reference_ids_reads_the_active_objectives_and_constraints():
    ids = context_reference_ids(
        {
            "objectives": [{"id": "objective:1", "title": "Reach 5 pilots"}],
            "constraints": [{"id": "constraint:2", "title": "Bootstrapped"}],
            "profile": {"name": "Faktus"},
        }
    )
    assert ids == frozenset({"objective:1", "constraint:2"})
    assert context_reference_ids(None) == frozenset()
