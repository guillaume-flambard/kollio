"""Experiment, outcome and learning operations.

Ticket #47 fixed the rules: any member who can read the initiative may
record an outcome or move the lifecycle, and completing an experiment
drafts a learning that a member confirms or edits. The draft composed
here is deterministic (hypothesis, metric, observed outcomes); a model
drafted suggestion is a later refinement of the analysis engine.
"""

from datetime import date
from uuid import UUID

from src.modules.experiments.adapters.postgres import (
    Experiment,
    ExperimentOutcome,
    Learning,
    PostgresExperiments,
)
from src.modules.experiments.domain.lifecycle import (
    ExperimentRuleError,
    compose_learning_draft,
    decide_learning_status,
    decide_transition,
)

__all__ = [
    "ExperimentNotFoundError",
    "ExperimentRuleError",
    "change_status",
    "create_experiment",
    "list_experiments",
    "list_learnings",
    "read_experiment",
    "record_outcome",
    "write_learning",
]


class ExperimentNotFoundError(LookupError):
    """The initiative or experiment is not visible to this subject."""


async def create_experiment(
    repo: PostgresExperiments,
    *,
    idea_id: UUID,
    subject: str,
    title: str,
    hypothesis: str,
    success_metric: str,
    baseline: str | None,
    target: str | None,
) -> Experiment:
    actor = await repo.accessible_idea(idea_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This initiative is not visible to you")
    _idea, user = actor
    return await repo.create_experiment(
        idea_id=idea_id,
        created_by_id=user.id,
        title=title,
        hypothesis=hypothesis,
        success_metric=success_metric,
        baseline=baseline,
        target=target,
    )


async def list_experiments(
    repo: PostgresExperiments, *, idea_id: UUID, subject: str
) -> list[Experiment]:
    if await repo.accessible_idea(idea_id, subject) is None:
        raise ExperimentNotFoundError("This initiative is not visible to you")
    return await repo.experiments_for_idea(idea_id)


async def read_experiment(
    repo: PostgresExperiments, *, experiment_id: UUID, subject: str
) -> tuple[Experiment, list[ExperimentOutcome], Learning | None]:
    actor = await repo.experiment_actor(experiment_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This experiment is not visible to you")
    experiment, _idea, _user = actor
    outcomes = await repo.outcomes(experiment.id)
    learning = await repo.learning(experiment.id)
    return experiment, outcomes, learning


async def _experiment_for(
    repo: PostgresExperiments, experiment_id: UUID, subject: str
) -> Experiment:
    actor = await repo.experiment_actor(experiment_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This experiment is not visible to you")
    return actor[0]


async def change_status(
    repo: PostgresExperiments, *, experiment_id: UUID, subject: str, target: str
) -> Experiment:
    experiment = await _experiment_for(repo, experiment_id, subject)
    status = decide_transition(current=experiment.status, target=target)
    experiment = await repo.apply_status(experiment, status, repo.now())
    if status == "completed":
        outcomes = await repo.outcomes(experiment.id)
        await repo.save_learning(
            experiment=experiment,
            text=compose_learning_draft(
                hypothesis=experiment.hypothesis,
                success_metric=experiment.success_metric,
                target=experiment.target,
                outcomes=[
                    {
                        "metric": outcome.metric,
                        "value": outcome.value,
                        "unit": outcome.unit,
                        "comment": outcome.comment,
                    }
                    for outcome in outcomes
                ],
            ),
            status="draft",
            confirmed_by_id=None,
        )
    return experiment


async def record_outcome(
    repo: PostgresExperiments,
    *,
    experiment_id: UUID,
    subject: str,
    metric: str,
    value: str,
    unit: str | None,
    observed_at: date | None,
    comment: str | None,
    qualitative: str | None,
) -> ExperimentOutcome:
    actor = await repo.experiment_actor(experiment_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This experiment is not visible to you")
    _experiment, _idea, user = actor
    return await repo.record_outcome(
        experiment_id=experiment_id,
        recorded_by_id=user.id,
        metric=metric,
        value=value,
        unit=unit,
        observed_at=observed_at,
        comment=comment,
        qualitative=qualitative,
    )


async def write_learning(
    repo: PostgresExperiments,
    *,
    experiment_id: UUID,
    subject: str,
    text: str | None,
    confirm: bool,
) -> Learning:
    actor = await repo.experiment_actor(experiment_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This experiment is not visible to you")
    experiment, _idea, user = actor
    existing = await repo.learning(experiment.id)
    outcomes = await repo.outcomes(experiment.id)
    body = text
    if body is None:
        body = (
            existing.text
            if existing is not None
            else compose_learning_draft(
                hypothesis=experiment.hypothesis,
                success_metric=experiment.success_metric,
                target=experiment.target,
                outcomes=[
                    {
                        "metric": outcome.metric,
                        "value": outcome.value,
                        "unit": outcome.unit,
                        "comment": outcome.comment,
                    }
                    for outcome in outcomes
                ],
            )
        )
    status = decide_learning_status(
        current=existing.status if existing is not None else "draft",
        target="confirmed" if confirm else "draft",
    )
    return await repo.save_learning(
        experiment=experiment,
        text=body,
        status=status,
        confirmed_by_id=user.id if status == "confirmed" else None,
    )


async def list_learnings(
    repo: PostgresExperiments, *, idea_id: UUID, subject: str
) -> list[Learning]:
    if await repo.accessible_idea(idea_id, subject) is None:
        raise ExperimentNotFoundError("This initiative is not visible to you")
    return await repo.learnings_for_idea(idea_id)
