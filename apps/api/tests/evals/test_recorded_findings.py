"""Evaluate recorded provider responses against the mandatory abstention contract.

These cases do not estimate overall competition-analysis quality.
"""

import json
import os
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from src.agents.schemas import GateFinding
from src.platform.config import get_settings
from src.platform.evaluation import LiveEvaluationGuard
from src.platform.llm import Gateway

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("no_evidence.*.json"))
COMPETITION_FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("competition.*.json"))
LIVE_GUARD = LiveEvaluationGuard.from_environment()


class AbstentionMetric(BaseMetric):
    threshold = 1.0
    async_mode = False
    strict_mode = True

    def measure(self, test_case, *args, **kwargs):
        finding = GateFinding.model_validate_json(test_case.actual_output)
        expected = json.loads(test_case.expected_output)
        self.success = (
            finding.verdict == expected["verdict"]
            and finding.locale == expected["locale"]
            and finding.source_ids == []
        )
        self.score = float(self.success)
        self.reason = "No evidence must produce an uncited unknown verdict in the requested locale."
        return self.score

    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)

    @property
    def __name__(self):
        return "Evidence-free abstention"


def evaluate_finding(fixture, output):
    assert_test(
        LLMTestCase(
            input=json.dumps(fixture["input"]),
            actual_output=json.dumps(output),
            expected_output=json.dumps(
                {
                    "verdict": fixture["expected_verdict"],
                    "locale": fixture["input"]["locale"],
                }
            ),
        ),
        [AbstentionMetric()],
        run_async=False,
    )


def assert_competition_contract(fixture, output):
    finding = GateFinding.model_validate(output)
    expected = fixture["expected"]
    assert finding.verdict == expected["verdict"]
    assert finding.locale == expected["locale"]
    assert finding.source_ids == expected["source_ids"]
    assert set(finding.source_ids).issubset({item["id"] for item in fixture["input"]["evidence"]})


@pytest.mark.parametrize("path", FIXTURES, ids=lambda path: path.stem)
def test_recorded_abstention(path):
    fixture = json.loads(path.read_text())
    evaluate_finding(fixture, fixture["output"])


@pytest.mark.parametrize("path", COMPETITION_FIXTURES, ids=lambda path: path.stem)
def test_recorded_competition_contract(path):
    fixture = json.loads(path.read_text())
    assert fixture["provenance"]["source_system"] == "prospecteur"
    assert fixture["provenance"]["source_case_id"]
    assert fixture["provenance"]["reviewed_on"]
    assert fixture["provenance"]["semantic_note"]
    assert_competition_contract(fixture, fixture["output"])


def test_recorded_suite_detects_known_failed_research_regression():
    path = next(path for path in COMPETITION_FIXTURES if "failed_research" in path.name)
    fixture = json.loads(path.read_text())
    broken_output = {**fixture["output"], "verdict": "pass"}
    with pytest.raises(AssertionError):
        assert_competition_contract(fixture, broken_output)


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("KOLLIO_RUN_LIVE_EVALS") != "1", reason="Live provider calls are opt-in"
)
@pytest.mark.parametrize("path", FIXTURES, ids=lambda path: path.stem)
async def test_live_abstention(path):
    fixture = json.loads(path.read_text())
    await LIVE_GUARD.authorize(incomplete_cases=len(FIXTURES) - LIVE_GUARD.attempted_cases)
    finding = await Gateway(get_settings()).assess(**fixture["input"])
    evaluate_finding(fixture, finding.model_dump())
