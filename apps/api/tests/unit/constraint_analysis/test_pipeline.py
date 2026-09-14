"""The adversarial pipeline: fixed order, cheap-then-premium tiers, one result,
and a conclusion that cannot drop the challenger or the evidence critic."""

import pytest

from src.modules.constraint_analysis.agent.pipeline import run_constraint_pipeline
from src.modules.constraint_analysis.domain.models import (
    AnalystReport,
    ChallengerReport,
    CompanyFitReport,
    ConstraintAnalysisResult,
    EvidenceReport,
)
from src.modules.constraint_analysis.domain.pipeline import (
    PipelineIncompleteError,
    PipelineStep,
    require_synthesis_inputs,
)

FACTOR_NAMES = ("competition", "build_cost", "time_to_market", "defensibility", "acquisition")


def _result(locale: str) -> ConstraintAnalysisResult:
    return ConstraintAnalysisResult.model_validate(
        {
            "overall_score": None,
            "verdict": "unknown",
            "summary": "Needs evidence.",
            "contradictions": [],
            "factors": [
                {
                    "name": name,
                    "basis": "unknown",
                    "score": None,
                    "gap": "No evidence supplied",
                    "summary": "Unknown.",
                    "source_ids": [],
                }
                for name in FACTOR_NAMES
            ],
            "locale": locale,
        }
    )


class _ScriptedGateway:
    model_commodity = "cheap-model"
    model_visible = "premium-model"

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def analyst(self, *, brief, locale):
        self.calls.append("analyst")
        return AnalystReport(arguments=["Pilot demand is real"])

    async def challenger(self, *, brief, locale):
        self.calls.append("challenger")
        return ChallengerReport(risks=["Cannot staff onboarding"])

    async def evidence_critic(self, *, brief, locale):
        self.calls.append("evidence_critic")
        return EvidenceReport(speculation=["Assumes willingness to pay"])

    async def company_fit(self, *, brief, locale):
        self.calls.append("company_fit")
        return CompanyFitReport(conflicts=["Collides with the no-hiring constraint"])

    async def synthesize(self, *, brief, analyst, challenger, evidence_critic, company_fit, locale):
        self.calls.append("synthesize")
        # The synthesizer genuinely sees the adversarial and evidentiary work.
        assert challenger.risks
        assert evidence_critic.speculation
        return _result(locale)


async def test_pipeline_runs_the_steps_in_order_and_returns_one_result() -> None:
    gateway = _ScriptedGateway()
    run = await run_constraint_pipeline(
        gateway,
        title="Offline field app",
        pitch="Works without signal",
        locale="fr",
        evidence=[{"id": "ev-1", "url": "https://e", "text": "note"}],
        context={"objectives": [{"id": "objective:1", "title": "Pilots", "state": "active"}]},
    )

    assert gateway.calls == [
        "analyst",
        "challenger",
        "evidence_critic",
        "company_fit",
        "synthesize",
    ]
    assert [step.name for step in run.steps] == [
        "analyst",
        "challenger",
        "evidence_critic",
        "company_fit",
        "synthesizer",
    ]
    assert [step.tier for step in run.steps] == [
        "commodity",
        "visible",
        "visible",
        "visible",
        "visible",
    ]
    assert run.steps[0].model == "cheap-model"
    assert run.steps[-1].model == "premium-model"
    assert run.result.verdict == "unknown"


def _step(name: str, output: dict) -> PipelineStep:
    return PipelineStep(name=name, tier="visible", model="m", output=output)


def test_a_conclusion_cannot_drop_the_challenger_or_the_evidence_critic() -> None:
    incomplete = [_step("analyst", {"arguments": ["x"]}), _step("company_fit", {"supports": []})]
    with pytest.raises(PipelineIncompleteError, match="challenger"):
        require_synthesis_inputs(incomplete)

    complete = [
        _step("challenger", {"risks": ["x"]}),
        _step("evidence_critic", {"facts": []}),
        _step("synthesizer", {"verdict": "unknown"}),
    ]
    require_synthesis_inputs(complete)  # does not raise
