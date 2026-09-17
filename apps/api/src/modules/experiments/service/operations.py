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
from src.modules.experiments.domain.links import validate_link
from src.modules.experiments.service.reuse import embed_confirmed_learning
from src.platform.config import get_settings

__all__ = [
    "ExperimentNotFoundError",
    "ExperimentRuleError",
    "change_status",
    "create_experiment",
    "list_experiments",
    "list_learnings",
    "list_space_experiments",
    "list_space_learnings",
    "read_experiment",
    "record_outcome",
    "write_learning",
]


class ExperimentNotFoundError(LookupError):
    """The initiative or experiment is not visible to this subject."""


async def _validate_space_link(
    repo: PostgresExperiments,
    *,
    idea_workspace_id: UUID | None,
    decision_space_id: UUID | None,
    option_id: UUID | None,
) -> None:
    if decision_space_id is None and option_id is None:
        return
    space_workspace_id = None
    if decision_space_id is not None:
        space = await repo.space(decision_space_id)
        space_workspace_id = space.workspace_id if space is not None else None
    option_space_id = None
    if option_id is not None and decision_space_id is not None:
        option = await repo.option_in_space(decision_space_id, option_id)
        option_space_id = option.space_id if option is not None else None
    validate_link(
        idea_workspace_id=idea_workspace_id,
        space_id=decision_space_id,
        space_workspace_id=space_workspace_id,
        option_id=option_id,
        option_space_id=option_space_id,
    )


async def _authorize_space(
    repo: PostgresExperiments, *, workspace_id: UUID, space_id: UUID, subject: str
) -> None:
    space = await repo.space(space_id)
    if space is None or space.workspace_id != workspace_id:
        raise ExperimentNotFoundError("This decision space is not visible to you")
    if not await repo.is_workspace_member(workspace_id, subject):
        raise ExperimentNotFoundError("This decision space is not visible to you")


async def list_space_experiments(
    repo: PostgresExperiments, *, workspace_id: UUID, space_id: UUID, subject: str
) -> list[Experiment]:
    await _authorize_space(repo, workspace_id=workspace_id, space_id=space_id, subject=subject)
    return await repo.experiments_for_space(space_id)


async def list_space_learnings(
    repo: PostgresExperiments, *, workspace_id: UUID, space_id: UUID, subject: str
) -> list[Learning]:
    await _authorize_space(repo, workspace_id=workspace_id, space_id=space_id, subject=subject)
    return await repo.learnings_for_space(space_id)


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
    decision_space_id: UUID | None = None,
    option_id: UUID | None = None,
) -> Experiment:
    actor = await repo.accessible_idea(idea_id, subject)
    if actor is None:
        raise ExperimentNotFoundError("This initiative is not visible to you")
    idea, user = actor
    await _validate_space_link(
        repo,
        idea_workspace_id=idea.workspace_id,
        decision_space_id=decision_space_id,
        option_id=option_id,
    )
    return await repo.create_experiment(
        idea_id=idea_id,
        created_by_id=user.id,
        title=title,
        hypothesis=hypothesis,
        success_metric=success_metric,
        baseline=baseline,
        target=target,
        decision_space_id=decision_space_id,
        option_id=option_id,
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
    experiment, idea, user = actor
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
    learning = await repo.save_learning(
        experiment=experiment,
        text=body,
        status=status,
        confirmed_by_id=user.id if status == "confirmed" else None,
    )
    if status == "confirmed":
        await embed_confirmed_learning(
            repo.session,
            learning_id=learning.id,
            text=learning.text,
            language=idea.lang,
            workspace_id=idea.workspace_id,
            idea_id=learning.idea_id,
            experiment_id=experiment.id,
            settings=get_settings(),
        )
    return learning


async def list_learnings(
    repo: PostgresExperiments, *, idea_id: UUID, subject: str
) -> list[Learning]:
    if await repo.accessible_idea(idea_id, subject) is None:
        raise ExperimentNotFoundError("This initiative is not visible to you")
    return await repo.learnings_for_idea(idea_id)
