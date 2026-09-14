"""Orchestration of the adversarial pipeline behind one analysis.

The graph still runs a single analyze step and the member still sees one
ConstraintAnalysisResult. What changes is what happens inside that step: five
ordered calls, the last of which reads the challenger and the evidence critic.
The order is fixed, cheap and premium tiers come from the task-class routing,
and every step is returned so the run can be persisted and replayed.
"""

from __future__ import annotations

from typing import Any

from src.modules.constraint_analysis.domain.models import (
    AnalystReport,
    ChallengerReport,
    CompanyFitReport,
    EvidenceReport,
)
from src.modules.constraint_analysis.domain.pipeline import (
    STEP_TASK_CLASS,
    AnalysisRun,
    PipelineStep,
    StepName,
    ordered_steps,
    require_synthesis_inputs,
)
from src.modules.constraint_analysis.service.ports import ConstraintReasoningGateway
from src.platform.locale import language_name
from src.platform.task_class import intelligence_tier

# A compact decision brief, never the whole history: only the fields the
# reasoning actually needs, with evidence capped.
EVIDENCE_CAP = 8


def build_decision_brief(
    *,
    title: str,
    pitch: str,
    locale: str,
    evidence: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    active = [key for key in ("objectives", "constraints")]
    brief: dict[str, Any] = {
        "title": title,
        "pitch": pitch,
        "locale": locale,
        "profile": context.get("profile") or {},
        "evidence": evidence[:EVIDENCE_CAP],
    }
    for key in active:
        items = context.get(key)
        if isinstance(items, list):
            brief[key] = [
                item
                for item in items
                if not isinstance(item, dict) or item.get("state") != "archived"
            ]
    return brief


def _model_for(gateway: ConstraintReasoningGateway, step: StepName) -> str:
    tier = intelligence_tier(STEP_TASK_CLASS[step])
    return gateway.model_visible if tier == "visible" else gateway.model_commodity


async def run_constraint_pipeline(
    gateway: ConstraintReasoningGateway,
    *,
    title: str,
    pitch: str,
    locale: str,
    evidence: list[dict[str, Any]],
    context: dict[str, Any],
) -> AnalysisRun:
    # Reject an unsupported locale before spending a single model call.
    language_name(locale)
    brief = build_decision_brief(
        title=title, pitch=pitch, locale=locale, evidence=evidence, context=context
    )
    steps: list[PipelineStep] = []

    def record(step: StepName, output: dict[str, Any]) -> None:
        steps.append(
            PipelineStep(
                name=step,
                tier=intelligence_tier(STEP_TASK_CLASS[step]),
                model=_model_for(gateway, step),
                output=output,
            )
        )

    analyst: AnalystReport = await gateway.analyst(brief=brief, locale=locale)
    record("analyst", analyst.model_dump(mode="json"))

    challenger: ChallengerReport = await gateway.challenger(brief=brief, locale=locale)
    record("challenger", challenger.model_dump(mode="json"))

    evidence_critic: EvidenceReport = await gateway.evidence_critic(brief=brief, locale=locale)
    record("evidence_critic", evidence_critic.model_dump(mode="json"))

    company_fit: CompanyFitReport = await gateway.company_fit(brief=brief, locale=locale)
    record("company_fit", company_fit.model_dump(mode="json"))

    # A conclusion cannot skip the adversarial and evidentiary work.
    require_synthesis_inputs(steps)

    result = await gateway.synthesize(
        brief=brief,
        analyst=analyst,
        challenger=challenger,
        evidence_critic=evidence_critic,
        company_fit=company_fit,
        locale=locale,
    )
    record("synthesizer", result.model_dump(mode="json"))

    return AnalysisRun(result=result, steps=ordered_steps(steps))
