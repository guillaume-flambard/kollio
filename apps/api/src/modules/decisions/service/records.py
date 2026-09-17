from dataclasses import dataclass
from uuid import UUID

from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    PostgresDecisionSpaces,
)
from src.modules.decision_spaces.domain.lifecycle import can_transition
from src.modules.decisions.adapters.postgres import (
    Decision,
    DecisionArgument,
    PostgresDecisions,
)
from src.modules.decisions.domain.access import can_commit_decision, can_read_record
from src.modules.decisions.domain.record import (
    RecordFieldError,
    RecordSideError,
    validate_alternatives,
    validate_rationale,
    validate_side,
)
from src.modules.decisions.domain.triggers import TriggerShapeError, validate_triggers


class DecisionSpaceNotFoundError(LookupError):
    """Raised when the workspace or the space is not visible to the requester."""


class DecisionNotFoundError(LookupError):
    """Raised when a visible space holds no decision record yet."""


class DecisionValidationError(ValueError):
    """Raised when a commit breaks a record field or lifecycle rule."""


class DecisionForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


@dataclass(frozen=True)
class RecordSnapshot:
    decision: Decision
    alternatives: list[UUID]
    arguments: list[DecisionArgument]


async def _authorize_read(repository: PostgresDecisions, workspace_id: UUID, subject: str) -> None:
    if not can_read_record(workspace_id, await repository.memberships(subject)):
        raise DecisionSpaceNotFoundError


async def _space(
    repository: PostgresDecisions, workspace_id: UUID, space_id: UUID
) -> DecisionSpace:
    space = await repository.space(workspace_id, space_id)
    if space is None:
        raise DecisionSpaceNotFoundError
    return space


async def _actor(repository: PostgresDecisions, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise DecisionSpaceNotFoundError
    return user.id


async def _snapshot(repository: PostgresDecisions, decision: Decision) -> RecordSnapshot:
    return RecordSnapshot(
        decision=decision,
        alternatives=await repository.alternatives(decision.id),
        arguments=await repository.arguments(decision.id),
    )


async def read_current_record(
    repository: PostgresDecisions, workspace_id: UUID, space_id: UUID, subject: str
) -> RecordSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    decision = await repository.latest(space_id)
    if decision is None:
        raise DecisionNotFoundError
    return await _snapshot(repository, decision)


async def list_versions(
    repository: PostgresDecisions, workspace_id: UUID, space_id: UUID, subject: str
) -> list[RecordSnapshot]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    versions = await repository.all_versions(space_id)
    return [await _snapshot(repository, decision) for decision in versions]


async def _validate_option(repository: PostgresDecisions, space_id: UUID, option_id: UUID) -> None:
    if await repository.option(space_id, option_id) is None:
        raise DecisionValidationError(f"Unknown option for this space: {option_id}")


async def _validate_arguments(
    repository: PostgresDecisions,
    space_id: UUID,
    arguments: list[tuple[UUID, str]],
) -> list[tuple[UUID, str]]:
    seen: set[UUID] = set()
    validated: list[tuple[UUID, str]] = []
    for contribution_id, side in arguments:
        try:
            validated_side = validate_side(side)
        except RecordSideError as error:
            raise DecisionValidationError(str(error)) from error
        if contribution_id in seen:
            raise DecisionValidationError(
                "a contribution cannot argue both ways on the same decision"
            )
        contribution = await repository.contribution(contribution_id)
        if (
            contribution is None
            or contribution.space_id != space_id
            or contribution.status != "confirmed"
        ):
            raise DecisionValidationError(
                f"Only confirmed contributions of this space can be cited: {contribution_id}"
            )
        seen.add(contribution_id)
        validated.append((contribution_id, validated_side))
    return validated


async def commit_decision(
    spaces: PostgresDecisionSpaces,
    repository: PostgresDecisions,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    selected_option_id: UUID,
    rationale: str,
    critical_assumptions: str | None,
    uncertainty: str | None,
    success_criteria: str | None,
    revisit_triggers: list[object] | None,
    rejected_option_ids: list[UUID],
    arguments: list[tuple[UUID, str]],
    lang: str,
) -> RecordSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)

    if not can_commit_decision(
        space.owner_id, await repository.participant_ids(space.id), actor_id
    ):
        raise DecisionForbiddenError
    if not can_transition(space.status, "DECIDED"):
        raise DecisionValidationError(
            f"A decision can only be committed from READY_TO_DECIDE, not {space.status}"
        )

    try:
        cleaned_rationale = validate_rationale(rationale)
    except RecordFieldError as error:
        raise DecisionValidationError(str(error)) from error

    await _validate_option(repository, space.id, selected_option_id)
    for option_id in rejected_option_ids:
        await _validate_option(repository, space.id, option_id)
    try:
        alternatives = validate_alternatives(rejected_option_ids, selected_option_id)
    except RecordFieldError as error:
        raise DecisionValidationError(str(error)) from error

    validated_arguments = await _validate_arguments(repository, space.id, arguments)

    try:
        triggers = validate_triggers(revisit_triggers)
    except TriggerShapeError as error:
        raise DecisionValidationError(str(error)) from error

    reviewers = sorted(str(user_id) for user_id in await repository.participant_ids(space.id))
    decision = await repository.create(
        space_id=space.id,
        version=await repository.next_version(space.id),
        selected_option_id=selected_option_id,
        rationale=cleaned_rationale,
        critical_assumptions=critical_assumptions,
        uncertainty=uncertainty,
        success_criteria=success_criteria,
        revisit_triggers=triggers or None,
        reviewer_ids=reviewers,
        decided_by=actor_id,
        lang=lang,
        alternative_ids=list(alternatives),
        arguments=validated_arguments,
    )
    await spaces.append_status_event(
        space, to_status="DECIDED", actor_id=actor_id, reason=None, lang=lang
    )
    return await _snapshot(repository, decision)
