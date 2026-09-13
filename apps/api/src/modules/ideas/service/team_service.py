import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.ideas.adapters.postgres import Idea, JoinRequest, PostgresIdeas
from src.modules.ideas.domain.permissions import can_read_idea
from src.modules.ideas.domain.team import (
    ROLES,
    TeamAuthorizationError,
    TeamRuleError,
    decide_acceptance,
    decide_application,
    decide_departure,
    decide_rejection,
)

logger = logging.getLogger("kollio.team")


class TeamNotFoundError(LookupError):
    """Raised when the idea is inaccessible to the actor."""


async def _accessible_idea(
    ideas: PostgresIdeas, idea_id: UUID, subject: str
) -> tuple[Idea, object]:
    idea = await ideas.get(idea_id)
    if idea is None:
        raise TeamNotFoundError
    memberships = await ideas.memberships(subject)
    if not can_read_idea(idea.workspace_id, memberships):
        raise TeamNotFoundError
    actor = await ideas.user_by_subject(subject)
    if actor is None:
        raise TeamNotFoundError
    return idea, actor


async def apply_to_join(
    ideas: PostgresIdeas, idea_id: UUID, subject: str, *, role: str, note: str
) -> JoinRequest:
    idea, actor = await _accessible_idea(ideas, idea_id, subject)
    is_owner = idea.owner_id == actor.id
    existing = await ideas.pending_join_request(idea_id, actor.id)
    decision = decide_application(
        actor_is_owner=is_owner,
        actor_is_member=True,
        role=role,
        note=note,
        already_pending=existing is not None,
    )
    request = JoinRequest(
        id=uuid4(),
        idea_id=idea_id,
        requester_id=actor.id,
        role=decision.role,
        note=decision.note,
        status="pending",
    )
    ideas.commit_team_state(request)
    await ideas.session.flush()
    return request


async def resolve_join_request(
    ideas: PostgresIdeas,
    idea_id: UUID,
    request_id: UUID,
    subject: str,
    *,
    action: str,
    role: str | None = None,
    rationale: str | None = None,
) -> JoinRequest:
    idea, actor = await _accessible_idea(ideas, idea_id, subject)
    request = await ideas.join_request(idea_id, request_id)
    if request is None:
        raise TeamNotFoundError
    is_owner = idea.owner_id == actor.id
    if action == "accept":
        if role is not None and role not in ROLES:
            raise TeamRuleError(f"Unknown or reserved role: {role}")
        decide_acceptance(is_owner=is_owner, current_status=request.status)
        request.status = "accepted"
        request.resolved_at = datetime.now(UTC)
        await ideas.add_idea_membership(idea_id, request.requester_id, role or request.role)
    elif action == "reject":
        if rationale is None:
            raise TeamRuleError("A rejection explains itself in a short rationale")
        decision = decide_rejection(
            is_owner=is_owner, current_status=request.status, rationale=rationale
        )
        request.status = decision.status
        request.rationale = decision.rationale
        request.resolved_at = datetime.now(UTC)
    else:
        raise TeamRuleError(f"Unknown action: {action}")
    ideas.commit_team_state(request)
    await ideas.session.flush()
    return request


async def leave_team(ideas: PostgresIdeas, idea_id: UUID, subject: str) -> dict:
    idea, actor = await _accessible_idea(ideas, idea_id, subject)
    is_owner = idea.owner_id == actor.id
    membership = await ideas.membership(idea_id, actor.id)
    decide_departure(
        actor_is_owner=is_owner,
        actor_is_member=membership is not None,
    )
    if is_owner and membership is None:
        raise TeamNotFoundError
    if membership is None:
        raise TeamNotFoundError
    await ideas.remove_membership(idea_id, actor.id)
    await ideas.record_departure(idea_id, actor.id, "left", None)
    return {"recorded": True}


async def remove_member(
    ideas: PostgresIdeas, idea_id: UUID, subject: str, member_id: UUID, *, reason: str | None
) -> dict:
    idea, actor = await _accessible_idea(ideas, idea_id, subject)
    if idea.owner_id != actor.id:
        raise TeamAuthorizationError("Only the owner can remove a member")
    if member_id == idea.owner_id:
        raise TeamRuleError("The owner is always in the loop")
    membership = await ideas.membership(idea_id, member_id)
    if membership is None:
        raise TeamNotFoundError
    await ideas.remove_membership(idea_id, member_id)
    await ideas.record_departure(idea_id, member_id, "removed", reason)
    return {"recorded": True}
