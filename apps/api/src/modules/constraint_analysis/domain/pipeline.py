"""The adversarial reasoning pipeline behind one analysis.

The member sees a single, robust constraint analysis, never five agents. Ticket
#76 fixes the internal shape: an analyst makes the case, a challenger attacks it
specifically at this company, an evidence critic separates fact from speculation,
a company-fit step compares against the active objectives and constraints, and a
decision synthesizer writes the conclusion the member reads. Cheap models
prepare; the premium model challenges, judges evidence and synthesises. The
synthesizer consumes the challenger and the evidence critic, and a run cannot
silently skip either: if they are missing the analysis fails rather than
softening into a flattering one-shot answer.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult
from src.platform.task_class import TaskClass

StepName = Literal["analyst", "challenger", "evidence_critic", "company_fit", "synthesizer"]

STEP_ORDER: tuple[StepName, ...] = (
    "analyst",
    "challenger",
    "evidence_critic",
    "company_fit",
    "synthesizer",
)

# Cheap models prepare the case; the premium model attacks it, judges the
# evidence and writes the conclusion the member reads. Tiers come from the same
# TaskClass routing as the gateway (#75), so a step never guesses its model.
STEP_TASK_CLASS: dict[StepName, TaskClass] = {
    "analyst": TaskClass.SUMMARISATION,
    "challenger": TaskClass.CHALLENGE,
    "evidence_critic": TaskClass.REASONING,
    "company_fit": TaskClass.COMPARISON,
    "synthesizer": TaskClass.REASONING,
}

# The synthesizer reads these two intermediate steps directly; dropping either
# would let a conclusion skip the adversarial and evidentiary work.
REQUIRED_SYNTHESIS_INPUTS: frozenset[StepName] = frozenset({"challenger", "evidence_critic"})


class PipelineStep(BaseModel):
    """One persisted intermediate step: what it was asked, which model tier ran
    it, and what it produced. Persisted per run so a conclusion can be replayed
    and audited."""

    model_config = ConfigDict(extra="forbid")

    name: StepName
    tier: Literal["commodity", "visible"]
    model: str
    output: dict[str, Any]


class AnalysisRun(BaseModel):
    """The single result the member sees plus the ordered steps that produced it."""

    model_config = ConfigDict(extra="forbid")

    result: ConstraintAnalysisResult
    steps: list[PipelineStep]


class PipelineIncompleteError(RuntimeError):
    """Raised when an ordered step is missing so a conclusion cannot be softened."""


def ordered_steps(steps: list[PipelineStep]) -> list[PipelineStep]:
    rank = {name: index for index, name in enumerate(STEP_ORDER)}
    return sorted(steps, key=lambda step: rank[step.name])


def require_synthesis_inputs(steps: list[PipelineStep]) -> None:
    """Guarantee the synthesizer had the adversarial and evidentiary steps to read."""
    produced = {step.name for step in steps if step.output}
    missing = REQUIRED_SYNTHESIS_INPUTS - produced
    if missing:
        names = ", ".join(sorted(missing))
        raise PipelineIncompleteError(
            f"The conclusion is missing required reasoning steps: {names}. Nothing was published."
        )
