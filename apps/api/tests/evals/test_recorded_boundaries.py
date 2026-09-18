"""Replay every reviewed recording through the boundary it is meant to represent.

The recorded corpus is the only net that runs without provider credentials, so each
recording has to survive the same validation the runtime applies to a live answer. These
tests replay the stored outputs through the production boundary instead of re-implementing
its rules, and they fail when a recording is never replayed anywhere.
"""

from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path

import pytest

from src.agents.schemas import GateFinding
from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult
from src.platform.llm import validate_finding

FIXTURES = Path(__file__).parent / "fixtures"
SOURCE_ROOTS = (Path(__file__).parent, Path(__file__).parent.parent / "unit")

GATE_RECORDINGS = sorted(FIXTURES.glob("competition.*.json")) + sorted(
    FIXTURES.glob("no_evidence.*.json")
)
ANALYSIS_RECORDINGS = sorted(FIXTURES.glob("constraint_analysis.*.json"))

DECLARED_GLOB = re.compile(r"""["']([A-Za-z0-9_.-]*\.\*\.json)["']""")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def supplied_identifiers(fixture: dict) -> set[str]:
    return {item["id"] for item in fixture["input"]["evidence"]}


def decided_recording() -> tuple[dict, GateFinding]:
    for path in GATE_RECORDINGS:
        fixture = load(path)
        finding = GateFinding.model_validate(fixture["output"])
        if finding.verdict != "unknown" and finding.source_ids:
            return fixture, finding
    raise AssertionError("The corpus holds no decided recording to mutate")


@pytest.mark.parametrize("path", GATE_RECORDINGS, ids=lambda path: path.stem)
def test_recorded_gate_finding_crosses_the_production_boundary(path: Path) -> None:
    fixture = load(path)
    finding = GateFinding.model_validate(fixture["output"])
    validated = validate_finding(finding, fixture["input"]["locale"], supplied_identifiers(fixture))
    assert validated == finding


@pytest.mark.parametrize("path", ANALYSIS_RECORDINGS, ids=lambda path: path.stem)
def test_recorded_constraint_analysis_crosses_the_domain_boundary(path: Path) -> None:
    fixture = load(path)
    result = ConstraintAnalysisResult.model_validate(fixture["output"])
    assert result.locale == fixture["input"]["locale"]


def test_a_recording_with_the_wrong_locale_is_refused() -> None:
    fixture = load(GATE_RECORDINGS[0])
    finding = GateFinding.model_validate(fixture["output"])
    other_locale = "fr" if fixture["input"]["locale"] == "en" else "en"
    with pytest.raises(ValueError, match="wrong locale"):
        validate_finding(finding, other_locale, supplied_identifiers(fixture))


def test_a_recording_citing_an_identifier_never_supplied_is_refused() -> None:
    fixture = load(GATE_RECORDINGS[0])
    finding = GateFinding.model_validate(fixture["output"])
    mutated = finding.model_copy(update={"source_ids": ["never-supplied"]})
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_finding(mutated, fixture["input"]["locale"], supplied_identifiers(fixture))


def test_a_decided_recording_without_citations_is_refused() -> None:
    fixture, finding = decided_recording()
    mutated = finding.model_copy(update={"source_ids": []})
    with pytest.raises(ValueError, match="A decision requires evidence"):
        validate_finding(mutated, fixture["input"]["locale"], supplied_identifiers(fixture))


def test_every_recording_is_replayed_by_a_test() -> None:
    sources = "".join(
        path.read_text(encoding="utf-8") for root in SOURCE_ROOTS for path in root.rglob("*.py")
    )
    families = set(DECLARED_GLOB.findall(sources))
    orphans = [
        path.name
        for path in sorted(FIXTURES.glob("*.json"))
        if path.name not in sources
        and not any(fnmatch.fnmatch(path.name, family) for family in families)
    ]
    assert orphans == []
