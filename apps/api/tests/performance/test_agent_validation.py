from time import perf_counter

import pytest

from src.modules.constraint_analysis.domain.models import (
    ConstraintAnalysisResult,
    validate_analysis_result,
)

pytestmark = pytest.mark.performance


def test_ten_thousand_agent_results_validate_within_cpu_budget() -> None:
    raw_result = {
        "overall_score": 50,
        "verdict": "unknown",
        "summary": "More evidence is required.",
        "factors": [
            {
                "name": name,
                "score": 50,
                "summary": "No evidence was supplied.",
                "source_ids": [],
            }
            for name in (
                "competition",
                "build_cost",
                "time_to_market",
                "defensibility",
                "acquisition",
            )
        ],
        "locale": "en",
    }

    started = perf_counter()
    for _ in range(10_000):
        result = ConstraintAnalysisResult.model_validate(raw_result)
        validate_analysis_result(
            result,
            requested_locale="en",
            evidence_ids=frozenset(),
        )

    assert perf_counter() - started < 0.5
