from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.profiles.adapters.postgres import PostgresProfiles
from src.modules.profiles.api.schemas import (
    ContributionResponse,
    MembershipResponse,
    OwnedIdeaResponse,
    ProfileResponse,
)
from src.modules.profiles.service.get_profile import ProfileNotFoundError, get_profile
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/users", tags=["profiles"])


@router.get("/{user_id}", response_model=ProfileResponse, operation_id="get_profile")
async def read_profile(
    user_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    try:
        record = await get_profile(PostgresProfiles(session), user_id, identity.subject)
    except ProfileNotFoundError as error:
        raise HTTPException(404, MESSAGES[request.state.locale]["not_found"]) from error
    return ProfileResponse(
        id=record.user.id,
        display_name=record.user.display_name,
        handle=record.user.handle,
        roles=record.user.roles,
        bio=record.user.bio,
        owned_ideas=[OwnedIdeaResponse.model_validate(row) for row in record.owned_ideas],
        memberships=[MembershipResponse.model_validate(row) for row in record.memberships],
        contributions=[ContributionResponse.model_validate(row) for row in record.contributions],
    )
