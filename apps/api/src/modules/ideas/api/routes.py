import json
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import PostgresIdeas
from src.modules.ideas.api.schemas import (
    IdeaPageResponse,
    IdeaResponse,
    IdeaSummaryResponse,
    LegacyIdeaContext,
)
from src.modules.ideas.service.get_idea import get_idea
from src.modules.ideas.service.list_ideas import list_workspace_ideas
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
    response = IdeaResponse.model_validate(idea)
    return response.model_copy(update={"legacy_context": legacy_context(idea.provenance)})


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
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> IdeaPageResponse:
    page = await list_workspace_ideas(
        PostgresIdeas(session), workspace_id, identity.subject, limit, offset
    )
    if page is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    items, total = page
    return IdeaPageResponse(
        items=[IdeaSummaryResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
