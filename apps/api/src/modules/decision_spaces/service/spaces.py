from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
    DecisionSpaceStatusEvent,
    PostgresDecisionSpaces,
)
from src.modules.decision_spaces.domain.access import (
    can_manage_participants,
    can_read_space,
    can_remove_participant,
    can_transition_space,
)
from src.modules.decision_spaces.domain.lifecycle import (
    DecisionSpaceStatusError,
    can_transition,
    reopen_requires_reason,
    validate_status,
)


class SpaceNotFoundError(LookupError):
    """Raised when the workspace or the space is not visible to the requester."""


class SpaceValidationError(ValueError):
    """Raised when a request breaks a lifecycle or participation rule."""


class SpaceForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


@dataclass(frozen=True)
class SpaceSnapshot:
    space: DecisionSpace
    participants: list[DecisionSpaceParticipant]
    history: list[DecisionSpaceStatusEvent]


async def _authorize_read(
    repository: PostgresDecisionSpaces, workspace_id: UUID, subject: str
) -> None:
    if not can_read_space(workspace_id, await repository.memberships(subject)):
        raise SpaceNotFoundError


async def _actor(repository: PostgresDecisionSpaces, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise SpaceNotFoundError
    return user.id


async def _load(
    repository: PostgresDecisionSpaces, workspace_id: UUID, space_id: UUID
) -> DecisionSpace:
    space = await repository.space(workspace_id, space_id)
    if space is None:
        raise SpaceNotFoundError
    return space


async def list_spaces(
    repository: PostgresDecisionSpaces, workspace_id: UUID, subject: str
) -> list[DecisionSpace]:
    await _authorize_read(repository, workspace_id, subject)
    return await repository.list_for_workspace(workspace_id)


async def open_space(
    repository: PostgresDecisionSpaces,
    workspace_id: UUID,
    subject: str,
    *,
    question: str,
    description: str | None,
    deadline: date | None,
    lang: str,
) -> DecisionSpace:
    await _authorize_read(repository, workspace_id, subject)
    owner_id = await _actor(repository, subject)
    cleaned = question.strip()
    if not cleaned:
        raise SpaceValidationError("the question must not be blank")
    return await repository.create(
        workspace_id=workspace_id,
        question=cleaned,
        description=description,
        deadline=deadline,
        owner_id=owner_id,
        lang=lang,
    )


async def get_space(
    repository: PostgresDecisionSpaces, workspace_id: UUID, space_id: UUID, subject: str
) -> SpaceSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _load(repository, workspace_id, space_id)
    return SpaceSnapshot(
        space=space,
        participants=await repository.participants(space.id),
        history=await repository.history(space.id),
    )


async def transition_space(
    repository: PostgresDecisionSpaces,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    to_status: str,
    reason: str | None,
    lang: str,
) -> DecisionSpace:
    await _authorize_read(repository, workspace_id, subject)
    space = await _load(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)

    try:
        validate_status(to_status)
    except DecisionSpaceStatusError as error:
        raise SpaceValidationError(str(error)) from error

    if not can_transition(space.status, to_status):
        raise SpaceValidationError(f"Illegal transition {space.status} -> {to_status}")

    if reopen_requires_reason(space.status, to_status):
        if reason is None or not reason.strip():
            raise SpaceValidationError("reopening a decision space requires a reason")

    if not can_transition_space(
        space.owner_id, await repository.participant_ids(space.id), actor_id
    ):
        raise SpaceForbiddenError

    await repository.append_status_event(
        space,
        to_status=to_status,
        actor_id=actor_id,
        reason=reason.strip() if reason is not None else None,
        lang=lang,
    )
    return space


async def add_participant(
    repository: PostgresDecisionSpaces,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    user_id: UUID,
) -> list[DecisionSpaceParticipant]:
    await _authorize_read(repository, workspace_id, subject)
    space = await _load(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    if not can_manage_participants(space.owner_id, actor_id):
        raise SpaceForbiddenError
    if not await repository.is_workspace_member(workspace_id, user_id):
        raise SpaceValidationError("a participant must be a member of the workspace")
    await repository.add_participant(space.id, user_id)
    return await repository.participants(space.id)


async def remove_participant(
    repository: PostgresDecisionSpaces,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    user_id: UUID,
) -> list[DecisionSpaceParticipant]:
    await _authorize_read(repository, workspace_id, subject)
    space = await _load(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    if not can_manage_participants(space.owner_id, actor_id):
        raise SpaceForbiddenError
    if not can_remove_participant(space.owner_id, user_id):
        raise SpaceValidationError("the owner cannot be removed from their own space")
    await repository.remove_participant(space.id, user_id)
    return await repository.participants(space.id)
