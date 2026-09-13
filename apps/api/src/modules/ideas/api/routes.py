import json
import logging
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import PostgresIdeas
from src.modules.ideas.api.schemas import (
    CollaboratorResponse,
    DepositIdeaRequest,
    IdeaPageResponse,
    IdeaResponse,
    IdeaSummaryResponse,
    LegacyIdeaContext,
)
from src.modules.ideas.service.deposit_idea import DepositNotFoundError, deposit_idea
from src.modules.ideas.service.get_idea import get_idea
from src.modules.ideas.service.list_ideas import list_workspace_ideas
from src.modules.iterations.adapters.postgres import PostgresIterations
from src.modules.iterations.service.operations import create_initial_iteration
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES
from src.platform.queue import AnalysisQueue, get_analysis_queue

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
    return response.model_copy(
        update={
            "legacy_context": legacy_context(idea.provenance),
            "collaborators": collaborators,
        }
    )


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
    queue: AnalysisQueue = Depends(get_analysis_queue),
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
    try:
        await queue.enqueue(
            workflow_id=f"deposit-{iteration.id}",
            idea_id=str(idea.id),
            iteration_id=str(iteration.id),
            locale=idea.lang,
            title=idea.title,
            pitch=idea.pitch,
        )
    except Exception:
        logging.getLogger("kollio.deposit").warning(
            "Analysis enqueue failed for iteration %s; deposit stands without analysis",
            iteration.id,
        )
    return IdeaResponse.model_validate(idea)


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
    domain: Annotated[str | None, Query(max_length=120)] = None,
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
        domain=domain,
    )
    if page is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    items, total = page
    collaborators_by_idea = await PostgresIdeas(session).collaborators_for_ideas(
        [item.id for item in items]
    )
    return IdeaPageResponse(
        items=[
            IdeaSummaryResponse.model_validate(item).model_copy(
                update={
                    "domain": item.provenance.get("domaine"),
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
            for item in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
