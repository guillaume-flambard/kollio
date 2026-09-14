from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workspaces.adapters.postgres import PostgresWorkspaces
from src.modules.workspaces.api.schemas import WorkspaceMemberResponse, WorkspaceResponse
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse], operation_id="list_workspaces")
async def list_workspaces(
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
):
    return await PostgresWorkspaces(session).for_subject(identity.subject)


@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    operation_id="list_workspace_members",
)
async def list_workspace_members(
    workspace_id: UUID,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
):
    members = await PostgresWorkspaces(session).members(workspace_id, identity.subject)
    if members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "workspace_not_found", "message": "This workspace is not visible"},
        )
    return members
