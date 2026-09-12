from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import PostgresIdeas
from src.modules.ideas.api.schemas import IdeaPageResponse, IdeaResponse
from src.modules.ideas.service.get_idea import get_idea
from src.modules.ideas.service.list_ideas import list_workspace_ideas
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/ideas", tags=["ideas"])
workspace_ideas_router = APIRouter(prefix="/workspaces", tags=["ideas"])


@router.get("/{idea_id}", response_model=IdeaResponse, operation_id="get_idea")
async def read_idea(
    idea_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
):
    idea = await get_idea(PostgresIdeas(session), idea_id, identity.subject)
    if idea is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    return idea


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
):
    page = await list_workspace_ideas(
        PostgresIdeas(session), workspace_id, identity.subject, limit, offset
    )
    if page is None:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"])
    items, total = page
    return IdeaPageResponse(items=items, total=total, limit=limit, offset=offset)
