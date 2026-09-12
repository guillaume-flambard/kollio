import pytest

from src.modules.constraint_analysis.domain.lifecycle import (
    AnalysisStatus,
    InvalidAnalysisTransition,
    failure_status,
    queue_review,
    start_execution,
)
from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult


def test_only_active_work_can_start() -> None:
    assert start_execution(AnalysisStatus.QUEUED) is AnalysisStatus.RUNNING
    assert start_execution(AnalysisStatus.RUNNING) is AnalysisStatus.RUNNING

    with pytest.raises(InvalidAnalysisTransition):
        start_execution(AnalysisStatus.COMPLETED)


def test_review_can_only_be_queued_once() -> None:
    assert queue_review(AnalysisStatus.AWAITING_REVIEW) is AnalysisStatus.REVIEW_QUEUED

    with pytest.raises(InvalidAnalysisTransition):
        queue_review(AnalysisStatus.REVIEW_QUEUED)


def test_failure_returns_to_the_correct_queue_until_retries_are_exhausted() -> None:
    assert failure_status(retrying=True, review=False) is AnalysisStatus.QUEUED
    assert failure_status(retrying=True, review=True) is AnalysisStatus.REVIEW_QUEUED
    assert failure_status(retrying=False, review=True) is AnalysisStatus.FAILED


def test_constraint_result_requires_each_factor_once() -> None:
    factors = [
        {
            "name": name,
            "score": 70,
            "summary": "Supported by the supplied evidence.",
            "source_ids": ["source-1"],
        }
        for name in (
            "competition",
            "build_cost",
            "time_to_market",
            "defensibility",
            "acquisition",
        )
    ]
    result = ConstraintAnalysisResult.model_validate(
        {
            "overall_score": 70,
            "verdict": "conditional",
            "summary": "The idea is viable if the acquisition risk is addressed.",
            "factors": factors,
            "locale": "en",
        }
    )
    assert len(result.factors) == 5

    factors[-1]["name"] = "competition"
    with pytest.raises(ValueError, match="exactly once"):
        ConstraintAnalysisResult.model_validate(
            {
                "overall_score": 70,
                "verdict": "conditional",
                "summary": "Invalid duplicate factors.",
                "factors": factors,
                "locale": "en",
            }
        )
