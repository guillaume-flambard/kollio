import pytest
from pydantic import ValidationError

from src.agents.schemas import ConstraintAnalysis
from src.platform.llm import validate_analysis


def _dimension(score=70, note="Evidence shows room."):
    return {"score": score, "note": note}


def _analysis(**overrides):
    payload = {
        "realism_score": 62,
        "concurrence": _dimension(),
        "cout": _dimension(),
        "temps": _dimension(),
        "defendabilite": _dimension(),
        "acquisition": _dimension(),
        "locale": "en",
        "source_ids": ["evidence-1"],
        "established_facts": ["A coop fleet exists downtown."],
    }
    payload.update(overrides)
    return payload


def _dimensions(payload):
    return (
        payload["concurrence"],
        payload["cout"],
        payload["temps"],
        payload["defendabilite"],
        payload["acquisition"],
    )


def test_valid_analysis_passes():
    analysis = ConstraintAnalysis.model_validate(_analysis())
    assert analysis.constraints["concurrence"].score == 70


def test_missing_dimension_is_rejected():
    payload = _analysis()
    del payload["acquisition"]
    with pytest.raises(ValidationError):
        ConstraintAnalysis.model_validate(payload)


def test_unknown_dimension_is_rejected():
    payload = _analysis()
    payload["buzz"] = _dimension()
    with pytest.raises(ValidationError):
        ConstraintAnalysis.model_validate(payload)


def test_out_of_range_score_is_rejected():
    payload = _analysis()
    payload["cout"] = _dimension(score=101)
    with pytest.raises(ValidationError):
        ConstraintAnalysis.model_validate(payload)


def test_unapproved_fields_are_rejected():
    payload = _analysis()
    payload["cout"] = {**_dimension(), "execute": "send_email"}
    with pytest.raises(ValidationError):
        ConstraintAnalysis.model_validate(payload)


def test_nulled_scores_record_abstention():
    payload = _analysis(realism_score=None, source_ids=[], established_facts=[])
    for dimension in _dimensions(payload):
        dimension["score"] = None
        dimension["note"] = "No evidence yet: add a competitor to unlock this score."
    analysis = ConstraintAnalysis.model_validate(payload)
    assert analysis.realism_score is None
    assert all(dimension.score is None for dimension in analysis.constraints.values())


def test_wrong_locale_is_rejected():
    analysis = ConstraintAnalysis.model_validate(_analysis(locale="fr"))
    with pytest.raises(ValueError, match="wrong locale"):
        validate_analysis(analysis, "en", {"evidence-1"})


def test_unknown_evidence_is_rejected():
    analysis = ConstraintAnalysis.model_validate(_analysis())
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_analysis(analysis, "en", {"other-evidence"})


def test_score_without_evidence_is_rejected():
    analysis = ConstraintAnalysis.model_validate(_analysis(source_ids=[]))
    with pytest.raises(ValueError, match="requires evidence"):
        validate_analysis(analysis, "en", set())
