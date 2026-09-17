from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.modules.decision_spaces.adapters.postgres import DecisionSpace
from src.modules.scenarios.adapters.postgres import (
    PostgresScenarios,
    ScenarioRun,
    ScenarioVariable,
)
from src.modules.scenarios.domain.access import can_read_scenarios, can_write_scenarios
from src.modules.scenarios.domain.runs import (
    RunRuleError,
    assert_single_base,
    validate_assumptions,
    validate_level,
    validate_values,
)
from src.modules.scenarios.domain.sensitivity import (
    Direction,
    RunPoints,
    SensitivityReport,
    compute_sensitivity,
)
from src.modules.scenarios.domain.variables import (
    VariableRuleError,
    validate_name,
    validate_range,
)


class ScenarioNotFoundError(LookupError):
    """Raised when the workspace, space, option, variable or run is not visible."""


class ScenarioValidationError(ValueError):
    """Raised when a request breaks a variable or run rule."""


class ScenarioForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


@dataclass(frozen=True)
class RunSnapshot:
    run: ScenarioRun
    values: dict[UUID, Decimal]


@dataclass(frozen=True)
class SensitivityResult:
    report: SensitivityReport
    evidence_for: int
    evidence_against: int


async def _authorize_read(repository: PostgresScenarios, workspace_id: UUID, subject: str) -> None:
    if not can_read_scenarios(workspace_id, await repository.memberships(subject)):
        raise ScenarioNotFoundError


async def _space(
    repository: PostgresScenarios, workspace_id: UUID, space_id: UUID
) -> DecisionSpace:
    space = await repository.space(workspace_id, space_id)
    if space is None:
        raise ScenarioNotFoundError
    return space


async def _actor(repository: PostgresScenarios, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise ScenarioNotFoundError
    return user.id


async def _authorize_write(
    repository: PostgresScenarios, space: DecisionSpace, subject: str
) -> UUID:
    actor_id = await _actor(repository, subject)
    if not can_write_scenarios(
        space.owner_id, await repository.participant_ids(space.id), actor_id
    ):
        raise ScenarioForbiddenError
    return actor_id


def _validate_definition(
    *, name: str, low: Decimal, base: Decimal, high: Decimal
) -> tuple[str, Decimal, Decimal, Decimal]:
    try:
        cleaned = validate_name(name)
        ordered = validate_range(low=low, base=base, high=high)
    except VariableRuleError as error:
        raise ScenarioValidationError(str(error)) from error
    return (cleaned, *ordered)


async def list_variables(
    repository: PostgresScenarios, workspace_id: UUID, space_id: UUID, subject: str
) -> list[ScenarioVariable]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    return await repository.variables(space_id)


async def create_variable(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    name: str,
    unit: str | None,
    low: Decimal,
    base: Decimal,
    high: Decimal,
    lang: str,
) -> ScenarioVariable:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _authorize_write(repository, space, subject)
    cleaned, ordered_low, ordered_base, ordered_high = _validate_definition(
        name=name, low=low, base=base, high=high
    )
    if await repository.variable_name_taken(space_id, cleaned):
        raise ScenarioValidationError(f"A variable named {cleaned} already exists")
    return await repository.create_variable(
        space_id=space.id,
        name=cleaned,
        unit=unit,
        low=ordered_low,
        base=ordered_base,
        high=ordered_high,
        lang=lang,
    )


async def update_variable(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    variable_id: UUID,
    subject: str,
    *,
    name: str,
    unit: str | None,
    low: Decimal,
    base: Decimal,
    high: Decimal,
) -> ScenarioVariable:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _authorize_write(repository, space, subject)
    variable = await repository.variable(space_id, variable_id)
    if variable is None:
        raise ScenarioNotFoundError
    cleaned, ordered_low, ordered_base, ordered_high = _validate_definition(
        name=name, low=low, base=base, high=high
    )
    if await repository.variable_name_taken(space_id, cleaned, excluding=variable.id):
        raise ScenarioValidationError(f"A variable named {cleaned} already exists")
    return await repository.update_variable(
        variable,
        name=cleaned,
        unit=unit,
        low=ordered_low,
        base=ordered_base,
        high=ordered_high,
    )


async def delete_variable(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    variable_id: UUID,
    subject: str,
) -> None:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _authorize_write(repository, space, subject)
    variable = await repository.variable(space_id, variable_id)
    if variable is None:
        raise ScenarioNotFoundError
    await repository.delete_variable(variable)


async def _option(repository: PostgresScenarios, space_id: UUID, option_id: UUID):
    option = await repository.option(space_id, option_id)
    if option is None:
        raise ScenarioNotFoundError
    return option


async def _validate_values(
    repository: PostgresScenarios,
    space_id: UUID,
    values: list[tuple[UUID, Decimal]],
) -> list[tuple[UUID, Decimal]]:
    try:
        ordered = list(validate_values(values))
    except RunRuleError as error:
        raise ScenarioValidationError(str(error)) from error
    for variable_id, _ in ordered:
        if await repository.variable(space_id, variable_id) is None:
            raise ScenarioValidationError("A run only declares variables of its space")
    return ordered


async def list_runs(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
) -> list[RunSnapshot]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    return [
        RunSnapshot(run=run, values=await repository.values(run.id))
        for run in await repository.runs(option_id)
    ]


async def create_run(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
    *,
    level: str,
    assumptions: str,
    values: list[tuple[UUID, Decimal]],
    lang: str,
) -> RunSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    actor_id = await _authorize_write(repository, space, subject)
    try:
        checked_level = validate_level(level)
        checked_assumptions = validate_assumptions(assumptions)
        assert_single_base(checked_level, await repository.run_levels(option_id))
    except RunRuleError as error:
        raise ScenarioValidationError(str(error)) from error
    ordered = await _validate_values(repository, space_id, values)
    run = await repository.create_run(
        option_id=option_id,
        space_id=space_id,
        level=checked_level,
        assumptions=checked_assumptions,
        created_by=actor_id,
        lang=lang,
        values=ordered,
    )
    return RunSnapshot(run=run, values=await repository.values(run.id))


async def update_run(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    subject: str,
    *,
    level: str,
    assumptions: str,
    values: list[tuple[UUID, Decimal]],
) -> RunSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    await _authorize_write(repository, space, subject)
    run = await repository.run(option_id, run_id)
    if run is None:
        raise ScenarioNotFoundError
    try:
        checked_level = validate_level(level)
        checked_assumptions = validate_assumptions(assumptions)
    except RunRuleError as error:
        raise ScenarioValidationError(str(error)) from error
    if checked_level == "base" and run.level != "base":
        existing = await repository.run_levels(option_id)
        try:
            assert_single_base(checked_level, existing)
        except RunRuleError as error:
            raise ScenarioValidationError(str(error)) from error
    ordered = await _validate_values(repository, space_id, values)
    updated = await repository.update_run(
        run,
        space_id=space_id,
        level=checked_level,
        assumptions=checked_assumptions,
        values=ordered,
    )
    return RunSnapshot(run=updated, values=await repository.values(updated.id))


async def delete_run(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    subject: str,
) -> None:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    await _authorize_write(repository, space, subject)
    run = await repository.run(option_id, run_id)
    if run is None:
        raise ScenarioNotFoundError
    await repository.delete_run(run)


async def read_sensitivity(
    repository: PostgresScenarios,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
    *,
    metric_variable_id: UUID,
    direction: Direction,
    threshold: Decimal,
) -> SensitivityResult:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    metric = await repository.variable(space_id, metric_variable_id)
    if metric is None:
        raise ScenarioNotFoundError

    runs = await repository.runs_with_values(option_id)
    report = compute_sensitivity(
        metric_variable_id=metric_variable_id,
        direction=direction,
        threshold=threshold,
        runs=[RunPoints(run_id=run_id, values=values) for run_id, values in runs],
        variable_ids=[variable.id for variable in await repository.variables(space_id)],
    )
    evidence_for, evidence_against = await repository.evidence_counts(option_id)
    return SensitivityResult(
        report=report,
        evidence_for=evidence_for,
        evidence_against=evidence_against,
    )
