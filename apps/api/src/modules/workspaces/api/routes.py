from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workspaces.adapters.postgres import PostgresWorkspaces
from src.modules.workspaces.api.schemas import WorkspaceResponse
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse], operation_id="list_workspaces")
async def list_workspaces(
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
):
    return await PostgresWorkspaces(session).for_subject(identity.subject)
