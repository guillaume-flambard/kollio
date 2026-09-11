from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ideas.adapters.postgres import PostgresIdeas
from src.modules.ideas.api.schemas import IdeaResponse
from src.modules.ideas.service.get_idea import get_idea
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/ideas", tags=["ideas"])


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
