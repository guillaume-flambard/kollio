import json
import logging
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from opentelemetry.propagate import inject
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.constraint_analysis.adapters.postgres import PostgresAnalysisWorkflows
from src.modules.constraint_analysis.service.operations import launch_analysis
from src.modules.constraint_analysis.service.read_model import head_analysis
from src.modules.ideas.adapters.postgres import Idea, PostgresIdeas
from src.modules.ideas.api.schemas import (
    AnalysisResponse,
    ApplyJoinBody,
    CollaboratorResponse,
    DepositIdeaRequest,
    IdeaPageResponse,
    IdeaResponse,
    IdeaSummaryResponse,
    JoinRequestResponse,
    LegacyIdeaContext,
    RejectJoinBody,
)
from src.modules.ideas.service.deposit_idea import DepositNotFoundError, deposit_idea
from src.modules.ideas.service.get_idea import get_idea
from src.modules.ideas.service.list_ideas import list_workspace_ideas
from src.modules.ideas.service.team_service import (
    TeamNotFoundError,
    apply_to_join,
    leave_team,
    remove_member,
    resolve_join_request,
)
from src.modules.iterations.adapters.postgres import PostgresIterations
from src.modules.iterations.service.operations import create_initial_iteration
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/ideas", tags=["ideas"])
workspace_ideas_router = APIRouter(prefix="/workspaces", tags=["ideas"])


def legacy_context(provenance: dict[str, Any]) -> LegacyIdeaContext | None:
    source_id = provenance.get("cle")
    if not isinstance(source_id, str):
        return None
    charge = provenance.get("charge", {})
    if isinstance(charge, str):
        try:
            charge = json.loads(charge)
        except json.JSONDecodeError:
            charge = {}
    if not isinstance(charge, dict):
        charge = {}
    return LegacyIdeaContext(
        source="prospecteur",
        source_id=source_id,
        domain=provenance.get("domaine"),
        verdict=provenance.get("verdict"),
        fatal_constraint=provenance.get("porte_fatale"),
        channel=charge.get("canal"),
        why_now=charge.get("pourquoi_maintenant"),
    )


@router.get("/{idea_id}", response_model=IdeaResponse, operation_id="get_idea")
async def read_idea(
    idea_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> IdeaResponse:
    idea = await get_idea(PostgresIdeas(session), idea_id, identity.subject)
    if idea is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    repository = PostgresIdeas(session)
    collaborators = [
        CollaboratorResponse(
            id=user.id,
            handle=user.handle,
            display_name=user.display_name,
            role=role,
            roles=user.roles,
            bio=user.bio,
            avatar_key=user.avatar_key,
        )
        for user, role in await repository.collaborators(idea.id)
    ]
    response = IdeaResponse.model_validate(idea)
    join_requests = await _visible_join_requests(repository, idea, identity.subject)
    display = await head_analysis(session, idea.id)
    return response.model_copy(
        update={
            "legacy_context": legacy_context(idea.provenance),
            "collaborators": collaborators,
            "sought_roles": idea.sought_roles,
            "join_requests": [
                JoinRequestResponse.model_validate(join_request) for join_request in join_requests
            ],
            "analysis": _display_response(display),
        }
    )


def _display_response(display) -> AnalysisResponse:
    return AnalysisResponse(
        state=display.state,
        iteration_id=display.iteration_id,
        realism_score=display.realism_score,
        constraints=display.constraints,
        locale=display.locale,
        model=display.model,
        created_at=display.created_at,
    )


async def _visible_join_requests(repository: PostgresIdeas, idea: Idea, subject: str):
    all_requests = await repository.join_requests_for_idea(idea.id)
    actor = await repository.user_by_subject(subject)
    if actor is not None and idea.owner_id == actor.id:
        return all_requests
    if actor is None:
        return []
    return [
        item for item in all_requests if item.status == "pending" and item.requester_id == actor.id
    ]


@workspace_ideas_router.post(
    "/{workspace_id}/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="deposit_workspace_idea",
)
async def deposit_workspace_idea(
    workspace_id: UUID,
    body: DepositIdeaRequest,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> IdeaResponse:
    messages = MESSAGES[request.state.locale]
    try:
        idea = await deposit_idea(
            PostgresIdeas(session),
            workspace_id,
            identity.subject,
            title=body.title,
            pitch=body.pitch,
            lang=body.lang or request.state.locale,
        )
        iteration = await create_initial_iteration(
            PostgresIterations(session),
            idea,
            idea.owner_id,
            message=messages["initial_deposit"],
            lang=idea.lang,
        )
        await session.commit()
    except DepositNotFoundError as error:
        raise HTTPException(404, messages["not_found"]) from error
    await _trigger_deposit_analysis(request, session, idea, iteration.id, identity.subject)
    return IdeaResponse.model_validate(idea)


async def _trigger_deposit_analysis(request, session, idea, iteration_id, subject) -> None:
    carrier: dict[str, str] = {}
    inject(carrier)
    try:
        workflows = PostgresAnalysisWorkflows(session)
        outcome = await launch_analysis(
            workflows,
            idea.id,
            subject,
            idempotency_key=f"deposit-{iteration_id}",
            locale=idea.lang,
            evidence=[],
            trace_context=carrier,
        )
        await session.commit()
        queue = getattr(request.app.state, "analysis_queue", None)
        if queue is None:
            return
        if outcome.created or outcome.workflow.current_step == "dispatch":
            locked = await workflows.get_for_worker(outcome.workflow.id, lock=True)
            if locked is not None and locked.current_step == "dispatch":
                await queue.dispatch(locked.id, locked.trace_context)
                locked.current_step = "queued"
                await session.commit()
    except Exception:
        logging.getLogger("kollio.deposit").warning(
            "Deposit analysis could not start for idea %s; the deposit stands without analysis",
            idea.id,
        )


@workspace_ideas_router.get(
    "/{workspace_id}/ideas",
    response_model=IdeaPageResponse,
    operation_id="list_workspace_ideas",
)
async def read_workspace_ideas(
    workspace_id: UUID,
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 24,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: Annotated[str | None, Query(max_length=160)] = None,
    stage: Literal["seed", "iterating", "team_formed"] | None = None,
    sought_role: Annotated[str | None, Query(max_length=20)] = None,
    realism_min: Annotated[int | None, Query(ge=1, le=99)] = None,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> IdeaPageResponse:
    page = await list_workspace_ideas(
        PostgresIdeas(session),
        workspace_id,
        identity.subject,
        limit,
        offset,
        query_text=q,
        stage=stage,
        sought_role=sought_role,
        realism_min=realism_min,
    )
    if page is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    collaborators_by_idea = await PostgresIdeas(session).collaborators_for_ideas(
        [item.id for item in page.items]
    )
    return IdeaPageResponse(
        items=[
            IdeaSummaryResponse.model_validate(item).model_copy(
                update={
                    "sought_roles": item.sought_roles,
                    "realism_score": page.realism_scores.get(item.id),
                    "last_activity_at": page.last_activity.get(item.id),
                    "collaborators": [
                        CollaboratorResponse(
                            id=user.id,
                            handle=user.handle,
                            display_name=user.display_name,
                            role=role,
                            roles=user.roles,
                            bio=user.bio,
                            avatar_key=user.avatar_key,
                        )
                        for user, role in collaborators_by_idea.get(item.id, [])
                    ],
                }
            )
            for item in page.items
        ],
        total=page.total,
        limit=limit,
        offset=offset,
    )


def _team_error(request: Request, error: Exception) -> HTTPException:
    messages = MESSAGES[request.state.locale]
    if isinstance(error, TeamNotFoundError):
        return HTTPException(404, messages["not_found"])
    raise error


@router.post(
    "/{idea_id}/join-requests",
    response_model=JoinRequestResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="request_idea_membership",
)
async def request_idea_membership(
    idea_id: UUID,
    body: ApplyJoinBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> JoinRequestResponse:
    repository = PostgresIdeas(session)
    try:
        applied = await apply_to_join(
            repository, idea_id, identity.subject, role=body.role, note=body.note
        )
        await session.commit()
    except (TeamNotFoundError, ValueError) as error:
        raise _team_error(request, error) from error
    return JoinRequestResponse.model_validate(applied)


@router.post(
    "/{idea_id}/join-requests/{request_id}/accept",
    response_model=JoinRequestResponse,
    operation_id="accept_idea_membership_request",
)
async def accept_idea_membership_request(
    idea_id: UUID,
    request_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> JoinRequestResponse:
    repository = PostgresIdeas(session)
    try:
        resolved = await resolve_join_request(
            repository, idea_id, request_id, identity.subject, action="accept"
        )
        await session.commit()
    except (TeamNotFoundError, ValueError) as error:
        raise _team_error(request, error) from error
    return JoinRequestResponse.model_validate(resolved)


@router.post(
    "/{idea_id}/join-requests/{request_id}/reject",
    response_model=JoinRequestResponse,
    operation_id="reject_idea_membership_request",
)
async def reject_idea_membership_request(
    idea_id: UUID,
    request_id: UUID,
    body: RejectJoinBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> JoinRequestResponse:
    repository = PostgresIdeas(session)
    try:
        resolved = await resolve_join_request(
            repository,
            idea_id,
            request_id,
            identity.subject,
            action="reject",
            rationale=body.rationale,
        )
        await session.commit()
    except (TeamNotFoundError, ValueError) as error:
        raise _team_error(request, error) from error
    return JoinRequestResponse.model_validate(resolved)


@router.post(
    "/{idea_id}/leave",
    operation_id="leave_idea_team",
)
async def leave_idea_team(
    idea_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict:
    repository = PostgresIdeas(session)
    try:
        outcome = await leave_team(repository, idea_id, identity.subject)
        await session.commit()
    except (TeamNotFoundError, ValueError) as error:
        raise _team_error(request, error) from error
    return outcome


class RemoveMemberBody(BaseModel):
    reason: str | None = Field(default=None, min_length=1, max_length=500)


@router.post(
    "/{idea_id}/members/{member_id}/remove",
    operation_id="remove_idea_member",
)
async def remove_idea_member(
    idea_id: UUID,
    member_id: UUID,
    body: RemoveMemberBody | None,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> dict:
    repository = PostgresIdeas(session)
    try:
        outcome = await remove_member(
            repository, idea_id, identity.subject, member_id, reason=body.reason if body else None
        )
        await session.commit()
    except (TeamNotFoundError, ValueError) as error:
        raise _team_error(request, error) from error
    return outcome
