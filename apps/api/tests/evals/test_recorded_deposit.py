"""Evaluate recorded constraint-analysis fixtures against the deposit contract.

These cases do not estimate overall deposit-analysis quality: they pin the
mandatory contract (five named dimensions, score-with-evidence coupling,
per-note locale parity, honest abstention) on recorded provider responses.
"""

import json
from pathlib import Path

import pytest

from src.agents.schemas import ConstraintAnalysis
from src.platform.llm import validate_analysis

FIXTURE_ROOT = Path(__file__).parent / "fixtures"
DEPOSIT_FIXTURES = sorted(FIXTURE_ROOT.glob("deposit.*.json"))
NO_EVIDENCE = [p for p in DEPOSIT_FIXTURES if "no_evidence" in p.name]
ITERATIONS = [p for p in DEPOSIT_FIXTURES if "iteration" in p.name]
DIMENSIONS = ("concurrence", "cout", "temps", "defendabilite", "acquisition")


def load_fixture(path: Path) -> dict:
    fixture = json.loads(path.read_text())
    assert fixture["provenance"]["source_system"] == "prospecteur"
    assert fixture["provenance"]["source_case_id"]
    assert fixture["provenance"]["reviewed_on"]
    assert fixture["provenance"]["semantic_note"]
    return fixture


@pytest.mark.parametrize("path", DEPOSIT_FIXTURES, ids=lambda path: path.stem)
def test_recorded_deposit_contract(path):
    fixture = load_fixture(path)
    analysis = ConstraintAnalysis.model_validate(fixture["output"])
    validated = validate_analysis(
        analysis, fixture["input"]["locale"], {item["id"] for item in fixture["input"]["evidence"]}
    )
    assert validated.locale == fixture["input"]["locale"]
    for dimension in validated.constraints.values():
        assert (dimension.score is None) == (validated.realism_score is None)
        assert dimension.note


@pytest.mark.parametrize("path", NO_EVIDENCE, ids=lambda path: path.stem)
def test_recorded_deposit_abstention_is_honest(path):
    fixture = load_fixture(path)
    analysis = ConstraintAnalysis.model_validate(fixture["output"])
    assert analysis.realism_score is None
    assert analysis.source_ids == []
    for key in DIMENSIONS:
        dimension = analysis.constraints[key]
        assert dimension.score is None
        assert dimension.note


def test_recorded_iterations_recompute():
    first = ConstraintAnalysis.model_validate(
        load_fixture(next(p for p in ITERATIONS if p.name.endswith("iteration_1.en.json")))[
            "output"
        ]
    )
    second = ConstraintAnalysis.model_validate(
        load_fixture(next(p for p in ITERATIONS if p.name.endswith("iteration_2.en.json")))[
            "output"
        ]
    )
    assert second.realism_score != first.realism_score
    assert second.source_ids != first.source_ids


def test_recorded_iteration_staleness_negative():
    """An analysis bound to an old iteration must never serve the new one."""

    first = load_fixture(next(p for p in ITERATIONS if p.name.endswith("iteration_1.en.json")))
    second = load_fixture(next(p for p in ITERATIONS if p.name.endswith("iteration_2.en.json")))
    assert first["iteration"] < second["iteration"]
    assert first["output"]["realism_score"] != second["output"]["realism_score"]


def test_recorded_score_without_evidence_is_rejected():
    fixture = load_fixture(next(p for p in ITERATIONS if p.name.endswith("iteration_1.en.json")))
    broken = {**fixture["output"], "source_ids": []}
    analysis = ConstraintAnalysis.model_validate(broken)
    with pytest.raises(ValueError, match="requires evidence"):
        validate_analysis(analysis, "en", set())
