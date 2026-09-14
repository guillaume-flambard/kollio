from uuid import UUID, uuid4

from src.modules.ideas.adapters.postgres import Idea
from src.modules.iterations.adapters.postgres import Iteration, PostgresIterations
from src.modules.iterations.api.schemas import IdeaSnapshot
from src.modules.iterations.domain.rules import (
    ConflictError,
    InvalidTransitionError,
    decide_acceptance,
    decide_creation,
    decide_rejection,
    decide_rollback,
)


class IterationNotFoundError(LookupError):
    """Raised when an idea or iteration is inaccessible."""


def _short_hash(identifier: UUID) -> str:
    return identifier.hex[:12]


async def create_initial_iteration(
    repository: PostgresIterations,
    idea: Idea,
    author_id: UUID,
    *,
    message: str,
    lang: str,
) -> Iteration:
    identifier = uuid4()
    revision = await repository.next_revision(idea.id)
    iteration = Iteration(
        id=identifier,
        idea_id=idea.id,
        parent_id=None,
        author_id=author_id,
        message=message,
        lang=lang,
        payload={"title": idea.title, "pitch": idea.pitch, "stage": idea.stage},
        branch="main",
        proposal_status=None,
        short_hash=_short_hash(identifier),
        revision=revision,
    )
    return await repository.append(iteration, idea, project=True)


async def list_iterations(
    repository: PostgresIterations,
    idea_id: UUID,
    subject: str,
) -> list[Iteration]:
    if await repository.accessible_idea(idea_id, subject) is None:
        raise IterationNotFoundError
    return await repository.history(idea_id)


async def create_iteration(
    repository: PostgresIterations,
    idea_id: UUID,
    subject: str,
    *,
    message: str,
    lang: str,
    snapshot: IdeaSnapshot,
    branch: str,
    expected_parent_id: UUID | None,
) -> Iteration:
    context = await repository.accessible_idea(idea_id, subject, lock=True)
    if context is None:
        raise IterationNotFoundError
    idea, actor = context
    branch_head = await repository.head(idea_id, branch)
    if branch != "main" and branch_head is None:
        branch_head = await repository.head(idea_id, "main")
    decision = decide_creation(
        is_owner=idea.owner_id == actor.id,
        branch=branch,
        expected_parent_id=expected_parent_id,
        current_branch_head_id=branch_head.id if branch_head else None,
    )
    identifier = uuid4()
    revision = await repository.next_revision(idea.id)
    iteration = Iteration(
        id=identifier,
        idea_id=idea.id,
        parent_id=decision.parent_id,
        author_id=actor.id,
        message=message,
        lang=lang,
        payload=snapshot.model_dump(mode="json"),
        branch=branch,
        proposal_status=decision.proposal_status,
        short_hash=_short_hash(identifier),
        revision=revision,
    )
    return await repository.append(iteration, idea, project=branch == "main")


async def accept_proposal(
    repository: PostgresIterations,
    idea_id: UUID,
    proposal_id: UUID,
    subject: str,
    *,
    expected_main_parent_id: UUID | None,
) -> Iteration:
    context = await repository.accessible_idea(idea_id, subject, lock=True)
    if context is None:
        raise IterationNotFoundError
    idea, actor = context
    proposal = await repository.get(idea_id, proposal_id)
    if proposal is None:
        raise IterationNotFoundError
    branch_head = await repository.head(idea_id, proposal.branch)
    if branch_head is None or branch_head.id != proposal.id:
        raise ConflictError("A newer proposal iteration exists on this branch")
    main_head = await repository.head(idea_id, "main")
    decision = decide_acceptance(
        is_owner=idea.owner_id == actor.id,
        branch=proposal.branch,
        proposal_status=proposal.proposal_status,
        expected_main_parent_id=expected_main_parent_id,
        current_main_head_id=main_head.id if main_head else None,
    )
    identifier = uuid4()
    revision = await repository.next_revision(idea.id)
    merge = Iteration(
        id=identifier,
        idea_id=idea.id,
        parent_id=decision.parent_id,
        author_id=actor.id,
        message=proposal.message,
        lang=proposal.lang,
        payload=proposal.payload,
        branch="main",
        proposal_status=None,
        short_hash=_short_hash(identifier),
        revision=revision,
    )
    await repository.resolve_branch(idea.id, proposal.branch, decision.proposal_status)
    return await repository.append(merge, idea, project=True)


async def reject_proposal(
    repository: PostgresIterations,
    idea_id: UUID,
    proposal_id: UUID,
    subject: str,
    *,
    rationale: str,
) -> Iteration:
    context = await repository.accessible_idea(idea_id, subject, lock=True)
    if context is None:
        raise IterationNotFoundError
    idea, actor = context
    proposal = await repository.get(idea_id, proposal_id)
    if proposal is None:
        raise IterationNotFoundError
    branch_head = await repository.head(idea_id, proposal.branch)
    if branch_head is None or branch_head.id != proposal.id:
        raise ConflictError("A newer proposal iteration exists on this branch")
    status = decide_rejection(
        is_owner=idea.owner_id == actor.id,
        branch=proposal.branch,
        proposal_status=proposal.proposal_status,
        rationale=rationale,
    )
    await repository.resolve_branch(idea.id, proposal.branch, status.status)
    proposal.proposal_status = status.status
    proposal.rationale = status.rationale
    await repository.session.flush()
    return proposal


async def rollback_iteration(
    repository: PostgresIterations,
    idea_id: UUID,
    target_id: UUID,
    subject: str,
    *,
    expected_main_parent_id: UUID | None,
    message: str,
    lang: str,
) -> Iteration:
    context = await repository.accessible_idea(idea_id, subject, lock=True)
    if context is None:
        raise IterationNotFoundError
    idea, actor = context
    target = await repository.get(idea_id, target_id)
    if target is None:
        raise IterationNotFoundError
    if target.branch != "main" and target.proposal_status != "accepted":
        raise InvalidTransitionError("Only an accepted snapshot can be restored")
    main_head = await repository.head(idea_id, "main")
    decision = decide_rollback(
        is_owner=idea.owner_id == actor.id,
        expected_main_parent_id=expected_main_parent_id,
        current_main_head_id=main_head.id if main_head else None,
    )
    identifier = uuid4()
    revision = await repository.next_revision(idea.id)
    rollback = Iteration(
        id=identifier,
        idea_id=idea.id,
        parent_id=decision.parent_id,
        author_id=actor.id,
        message=message,
        lang=lang,
        payload=target.payload,
        branch="main",
        proposal_status=None,
        short_hash=_short_hash(identifier),
        revision=revision,
    )
    return await repository.append(rollback, idea, project=True)
