from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from src.modules.company_context.adapters.postgres import (
    CompanyConstraint,
    CompanyMetric,
    CompanyObjective,
    CompanyPrinciple,
    CompanyProfile,
    PostgresCompanyContext,
)
from src.modules.company_context.domain.access import can_access_context


class ContextNotFoundError(LookupError):
    """Raised when the workspace is not visible to the requester."""


class ObjectiveNotFoundError(LookupError):
    """Raised when an objective does not exist inside the workspace."""


class ConstraintNotFoundError(LookupError):
    """Raised when a constraint does not exist inside the workspace."""


class PrincipleNotFoundError(LookupError):
    """Raised when a principle does not exist inside the workspace."""


class MetricNotFoundError(LookupError):
    """Raised when a metric does not exist inside the workspace."""


@dataclass(frozen=True)
class ContextSnapshot:
    profile: CompanyProfile | None
    objectives: list[CompanyObjective]
    constraints: list[CompanyConstraint]
    principles: list[CompanyPrinciple]
    metrics: list[CompanyMetric]


async def _authorize(repository: PostgresCompanyContext, workspace_id: UUID, subject: str) -> None:
    if not can_access_context(workspace_id, await repository.memberships(subject)):
        raise ContextNotFoundError


async def get_context(
    repository: PostgresCompanyContext, workspace_id: UUID, subject: str
) -> ContextSnapshot:
    await _authorize(repository, workspace_id, subject)
    return ContextSnapshot(
        profile=await repository.profile(workspace_id),
        objectives=await repository.objectives(workspace_id),
        constraints=await repository.constraints(workspace_id),
        principles=await repository.principles(workspace_id),
        metrics=await repository.metrics(workspace_id),
    )


async def save_profile(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    values: dict[str, Any],
    lang: str,
) -> CompanyProfile:
    await _authorize(repository, workspace_id, subject)
    return await repository.upsert_profile(workspace_id, values, lang)


async def create_objective(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    *,
    title: str,
    lang: str,
) -> CompanyObjective:
    await _authorize(repository, workspace_id, subject)
    return await repository.create_objective(workspace_id, title, lang)


async def update_objective(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    objective_id: UUID,
    changes: dict[str, Any],
    lang: str,
) -> CompanyObjective:
    await _authorize(repository, workspace_id, subject)
    objective = await repository.update_objective(workspace_id, objective_id, changes, lang)
    if objective is None:
        raise ObjectiveNotFoundError
    return objective


async def create_constraint(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    *,
    title: str,
    detail: str | None,
    lang: str,
) -> CompanyConstraint:
    await _authorize(repository, workspace_id, subject)
    return await repository.create_constraint(workspace_id, title, detail, lang)


async def update_constraint(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    constraint_id: UUID,
    changes: dict[str, Any],
    lang: str,
) -> CompanyConstraint:
    await _authorize(repository, workspace_id, subject)
    constraint = await repository.update_constraint(workspace_id, constraint_id, changes, lang)
    if constraint is None:
        raise ConstraintNotFoundError
    return constraint


async def create_principle(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    *,
    title: str,
    detail: str | None,
    lang: str,
) -> CompanyPrinciple:
    await _authorize(repository, workspace_id, subject)
    return await repository.create_principle(workspace_id, title, detail, lang)


async def update_principle(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    principle_id: UUID,
    changes: dict[str, Any],
    lang: str,
) -> CompanyPrinciple:
    await _authorize(repository, workspace_id, subject)
    principle = await repository.update_principle(workspace_id, principle_id, changes, lang)
    if principle is None:
        raise PrincipleNotFoundError
    return principle


async def create_metric(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    *,
    name: str,
    value: str | None,
    unit: str | None,
    observed_at: date | None,
    source: str | None,
    lang: str,
) -> CompanyMetric:
    await _authorize(repository, workspace_id, subject)
    return await repository.create_metric(
        workspace_id,
        name=name,
        value=value,
        unit=unit,
        observed_at=observed_at,
        source=source,
        lang=lang,
    )


async def update_metric(
    repository: PostgresCompanyContext,
    workspace_id: UUID,
    subject: str,
    metric_id: UUID,
    changes: dict[str, Any],
    lang: str,
) -> CompanyMetric:
    await _authorize(repository, workspace_id, subject)
    metric = await repository.update_metric(workspace_id, metric_id, changes, lang)
    if metric is None:
        raise MetricNotFoundError
    return metric
