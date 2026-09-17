from uuid import UUID

from src.modules.branches.adapters.postgres import (
    Branch,
    Contribution,
    PostgresBranches,
)
from src.modules.branches.domain.access import can_read_branch, can_write_branch
from src.modules.branches.domain.propose import (
    ContributionKindError,
    ContributionProposalError,
    initial_status,
    validate_kind,
    validate_proposal_title,
)
from src.modules.decision_spaces.adapters.postgres import DecisionSpace


class BranchNotFoundError(LookupError):
    """Raised when the workspace, space or branch is not visible to the requester."""


class BranchValidationError(ValueError):
    """Raised when a request breaks a branch or contribution rule."""


class BranchForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


class ContributionNotFoundError(LookupError):
    """Raised when a contribution is not visible to the requester."""


async def _authorize_read(repository: PostgresBranches, workspace_id: UUID, subject: str) -> None:
    if workspace_id not in await repository.memberships(subject):
        raise BranchNotFoundError


async def _actor(repository: PostgresBranches, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise BranchNotFoundError
    return user.id


async def _space(repository: PostgresBranches, workspace_id: UUID, space_id: UUID) -> DecisionSpace:
    space = await repository.space(space_id)
    if space is None or space.workspace_id != workspace_id:
        raise BranchNotFoundError
    return space


async def _writers(repository: PostgresBranches, space: DecisionSpace) -> frozenset[UUID]:
    return frozenset({space.owner_id}) | await repository.participant_ids(space.id)


async def list_branches(
    repository: PostgresBranches, workspace_id: UUID, space_id: UUID, subject: str
) -> list[Branch]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    memberships = await repository.memberships(subject)
    return [
        branch
        for branch in await repository.list_for_space(space_id)
        if can_read_branch(
            branch.visibility, workspace_id, memberships, branch.created_by, actor_id
        )
    ]


async def create_branch(
    repository: PostgresBranches,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    title: str,
    summary: str | None,
    visibility: str,
    lang: str,
) -> Branch:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    if not can_write_branch(space.owner_id, await repository.participant_ids(space.id), actor_id):
        raise BranchForbiddenError
    cleaned = title.strip()
    if not cleaned:
        raise BranchValidationError("a branch needs a title")
    if visibility not in ("private", "shared"):
        raise BranchValidationError(f"Unknown branch visibility: {visibility}")
    return await repository.create_branch(
        space_id=space.id,
        title=cleaned,
        summary=summary,
        visibility=visibility,
        created_by=actor_id,
        source_idea_id=None,
        lang=lang,
    )


async def get_branch(
    repository: PostgresBranches, workspace_id: UUID, space_id: UUID, branch_id: UUID, subject: str
) -> Branch:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    branch = await repository.branch(space_id, branch_id)
    if branch is None:
        raise BranchNotFoundError
    actor_id = await _actor(repository, subject)
    if not can_read_branch(
        branch.visibility,
        workspace_id,
        await repository.memberships(subject),
        branch.created_by,
        actor_id,
    ):
        raise BranchNotFoundError
    return branch


async def propose_contribution(
    repository: PostgresBranches,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    branch_id: UUID,
    kind: str,
    title: str,
    body: str | None,
    source: str | None,
    tool_model: str | None,
    transformation_history: dict | None,
    as_suggestion: bool,
    lang: str,
) -> Contribution:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    branch = await repository.branch(space_id, branch_id)
    if branch is None:
        raise BranchNotFoundError
    actor_id = await _actor(repository, subject)
    if not can_read_branch(
        branch.visibility,
        workspace_id,
        await repository.memberships(subject),
        branch.created_by,
        actor_id,
    ):
        raise BranchNotFoundError
    if not can_write_branch(space.owner_id, await repository.participant_ids(space.id), actor_id):
        raise BranchForbiddenError
    try:
        validate_kind(kind)
    except ContributionKindError as error:
        raise BranchValidationError(str(error)) from error
    try:
        cleaned_title = validate_proposal_title(title)
    except ContributionProposalError as error:
        raise BranchValidationError(str(error)) from error
    return await repository.create_contribution(
        space_id=space.id,
        branch_id=branch.id,
        kind=kind,
        title=cleaned_title,
        body=body,
        author_id=actor_id,
        source=source,
        tool_model=tool_model,
        transformation_history=transformation_history,
        status=initial_status(is_human=not as_suggestion),
        lang=lang,
    )


async def list_contributions(
    repository: PostgresBranches, workspace_id: UUID, space_id: UUID, subject: str
) -> list[Contribution]:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    return await repository.list_contributions_for_space(space_id)


async def confirm_contribution(
    repository: PostgresBranches,
    workspace_id: UUID,
    space_id: UUID,
    contribution_id: UUID,
    subject: str,
) -> Contribution:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    contribution = await repository.contribution(space_id, contribution_id)
    if contribution is None:
        raise ContributionNotFoundError
    actor_id = await _actor(repository, subject)
    if not can_write_branch(space.owner_id, await repository.participant_ids(space.id), actor_id):
        raise BranchForbiddenError
    return await repository.confirm_contribution(contribution, actor_id)
