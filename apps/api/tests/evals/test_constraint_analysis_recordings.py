import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from src.modules.constraint_analysis.domain.models import (
    ConstraintAnalysisResult,
    context_reference_ids,
)

FIXTURES = sorted(
    (Path(__file__).parent / "fixtures").glob("constraint_analysis.no_evidence.*.json")
)

CONTRADICTION_FIXTURES = sorted(
    (Path(__file__).parent / "fixtures").glob("constraint_analysis.contradiction.*.json")
)


class ConstraintAbstentionMetric(BaseMetric):
    threshold = 1.0
    async_mode = False
    strict_mode = True

    def measure(self, test_case, *args, **kwargs):
        result = ConstraintAnalysisResult.model_validate_json(test_case.actual_output)
        expected = json.loads(test_case.expected_output)
        self.success = (
            result.verdict == "unknown"
            and result.locale == expected["locale"]
            and len(result.factors) == 5
            and result.overall_score is None
            and all(
                factor.basis == "unknown"
                and factor.score is None
                and bool(factor.gap)
                and not factor.source_ids
                for factor in result.factors
            )
        )
        self.score = float(self.success)
        self.reason = (
            "Evidence-free analysis must abstain, score nothing, name each gap and cite nothing."
        )
        return self.score

    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)

    @property
    def __name__(self):
        return "Constraint analysis abstention"


@pytest.mark.parametrize("path", FIXTURES, ids=lambda path: path.stem)
def test_recorded_constraint_analysis_abstains_without_evidence(path: Path) -> None:
    fixture = json.loads(path.read_text())
    assert_test(
        LLMTestCase(
            input=json.dumps(fixture["input"]),
            actual_output=json.dumps(fixture["output"]),
            expected_output=json.dumps({"locale": fixture["input"]["locale"]}),
        ),
        [ConstraintAbstentionMetric()],
        run_async=False,
    )


class ContradictionMetric(BaseMetric):
    threshold = 1.0
    async_mode = False
    strict_mode = True

    def measure(self, test_case, *args, **kwargs):
        result = ConstraintAnalysisResult.model_validate_json(test_case.actual_output)
        expected = json.loads(test_case.expected_output)
        supplied = context_reference_ids(expected["company_context"])
        referenced = {item.ref_id for item in result.contradictions}
        self.success = (
            bool(result.contradictions)
            and referenced.issubset(supplied)
            and any(factor.basis == "unknown" and factor.score is None for factor in result.factors)
        )
        self.score = float(self.success)
        self.reason = (
            "A contradicting analysis names supplied objective or constraint ids and keeps its "
            "unknown factors unscored."
        )
        return self.score

    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)

    @property
    def __name__(self):
        return "Constraint analysis contradiction"


@pytest.mark.parametrize("path", CONTRADICTION_FIXTURES, ids=lambda path: path.stem)
def test_recorded_constraint_analysis_contradicts_supplied_context(path: Path) -> None:
    fixture = json.loads(path.read_text())
    assert_test(
        LLMTestCase(
            input=json.dumps(fixture["input"]),
            actual_output=json.dumps(fixture["output"]),
            expected_output=json.dumps(fixture["input"]),
        ),
        [ContradictionMetric()],
        run_async=False,
    )
