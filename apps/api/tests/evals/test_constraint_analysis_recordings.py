import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult

FIXTURES = sorted(
    (Path(__file__).parent / "fixtures").glob("constraint_analysis.no_evidence.*.json")
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
            and all(not factor.source_ids for factor in result.factors)
        )
        self.score = float(self.success)
        self.reason = "Evidence-free analysis must abstain without invented citations."
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
