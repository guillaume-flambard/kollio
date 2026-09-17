from dataclasses import dataclass
from uuid import UUID

from src.modules.branches.adapters.postgres import Contribution
from src.modules.decision_spaces.adapters.postgres import DecisionSpace
from src.modules.options.adapters.postgres import (
    Option,
    OptionEvidence,
    PostgresOptions,
)
from src.modules.options.domain.access import can_read_options, can_write_options
from src.modules.options.domain.evidence import EvidenceSideError, validate_side
from src.modules.options.domain.fields import (
    OptionFieldError,
    validate_proposal,
    validate_title,
)

TEXT_FIELDS: tuple[str, ...] = (
    "mechanism",
    "upside",
    "cost",
    "risks",
    "critical_assumptions",
    "success_metrics",
)


class OptionNotFoundError(LookupError):
    """Raised when the workspace, space or option is not visible to the requester."""


class OptionValidationError(ValueError):
    """Raised when a request breaks an option or evidence rule."""


class OptionForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


@dataclass(frozen=True)
class OptionSnapshot:
    option: Option
    evidence: list[OptionEvidence]


async def _authorize_read(repository: PostgresOptions, workspace_id: UUID, subject: str) -> None:
    if not can_read_options(workspace_id, await repository.memberships(subject)):
        raise OptionNotFoundError


async def _actor(repository: PostgresOptions, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise OptionNotFoundError
    return user.id


async def _space(repository: PostgresOptions, workspace_id: UUID, space_id: UUID) -> DecisionSpace:
    space = await repository.space(space_id)
    if space is None or space.workspace_id != workspace_id:
        raise OptionNotFoundError
    return space


async def _writer(repository: PostgresOptions, space: DecisionSpace, subject: str) -> UUID:
    actor_id = await _actor(repository, subject)
    if not can_write_options(space.owner_id, await repository.participant_ids(space.id), actor_id):
        raise OptionForbiddenError
    return actor_id


async def _load(repository: PostgresOptions, space_id: UUID, option_id: UUID) -> Option:
    option = await repository.option(space_id, option_id)
    if option is None:
        raise OptionNotFoundError
    return option


async def list_options(
    repository: PostgresOptions, workspace_id: UUID, space_id: UUID, subject: str
) -> list[Option]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    return await repository.list_for_space(space_id)


async def get_option(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
) -> OptionSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    option = await _load(repository, space_id, option_id)
    return OptionSnapshot(option=option, evidence=await repository.evidence(option.id))


async def create_option(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    title: str,
    proposal: str,
    fields: dict[str, str | None],
    lang: str,
) -> OptionSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    actor_id = await _writer(repository, space, subject)
    try:
        cleaned_title = validate_title(title)
        cleaned_proposal = validate_proposal(proposal)
    except OptionFieldError as error:
        raise OptionValidationError(str(error)) from error
    option = await repository.create_option(
        space_id=space.id,
        title=cleaned_title,
        proposal=cleaned_proposal,
        mechanism=fields.get("mechanism"),
        upside=fields.get("upside"),
        cost=fields.get("cost"),
        risks=fields.get("risks"),
        critical_assumptions=fields.get("critical_assumptions"),
        success_metrics=fields.get("success_metrics"),
        created_by=actor_id,
        lang=lang,
    )
    return OptionSnapshot(option=option, evidence=[])


async def update_option(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
    *,
    values: dict[str, str],
    lang: str,
) -> OptionSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _writer(repository, space, subject)
    option = await _load(repository, space_id, option_id)
    try:
        if "title" in values:
            values["title"] = validate_title(values["title"])
        if "proposal" in values:
            values["proposal"] = validate_proposal(values["proposal"])
    except OptionFieldError as error:
        raise OptionValidationError(str(error)) from error
    updated = await repository.update_option(option, values, lang)
    return OptionSnapshot(option=updated, evidence=await repository.evidence(updated.id))


async def delete_option(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
) -> None:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _writer(repository, space, subject)
    option = await _load(repository, space_id, option_id)
    await repository.delete_option(option)


async def link_evidence(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
    *,
    contribution_id: UUID,
    side: str,
) -> OptionSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _writer(repository, space, subject)
    option = await _load(repository, space_id, option_id)
    try:
        validate_side(side)
    except EvidenceSideError as error:
        raise OptionValidationError(str(error)) from error
    contribution: Contribution | None = await repository.contribution(contribution_id)
    if contribution is None or contribution.space_id != space.id:
        raise OptionValidationError("the contribution belongs to another space")
    if contribution.status != "confirmed":
        raise OptionValidationError("only a confirmed contribution can be evidence")
    if await repository.evidence_for(option.id, contribution_id) is not None:
        raise OptionValidationError("that contribution is already linked")
    await repository.link_evidence(option.id, contribution_id, side)
    return OptionSnapshot(option=option, evidence=await repository.evidence(option.id))


async def unlink_evidence(
    repository: PostgresOptions,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    contribution_id: UUID,
    subject: str,
) -> OptionSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _writer(repository, space, subject)
    option = await _load(repository, space_id, option_id)
    link = await repository.evidence_for(option.id, contribution_id)
    if link is None:
        raise OptionValidationError("that contribution is not linked to this option")
    await repository.unlink_evidence(link)
    return OptionSnapshot(option=option, evidence=await repository.evidence(option.id))
