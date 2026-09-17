from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.decision_spaces.api.schemas import (
    DecisionSpaceCreate,
    DecisionSpaceDetailResponse,
    DecisionSpaceListResponse,
    DecisionSpaceParticipantResponse,
    DecisionSpaceResponse,
    DecisionSpaceStatusEventResponse,
    DecisionSpaceTransition,
    ParticipantAdd,
)
from src.modules.decision_spaces.service.spaces import (
    SpaceForbiddenError,
    SpaceNotFoundError,
    SpaceValidationError,
    add_participant,
    get_space,
    list_spaces,
    open_space,
    remove_participant,
    transition_space,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["decision-spaces"])


def _not_found(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_space"]
    )


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


@router.get(
    "/{workspace_id}/decision-spaces",
    response_model=DecisionSpaceListResponse,
    operation_id="list_decision_spaces",
)
async def list_decision_spaces(
    workspace_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionSpaceListResponse:
    try:
        spaces = await list_spaces(PostgresDecisionSpaces(session), workspace_id, identity.subject)
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    return DecisionSpaceListResponse(
        items=[DecisionSpaceResponse.model_validate(space) for space in spaces]
    )


@router.post(
    "/{workspace_id}/decision-spaces",
    response_model=DecisionSpaceResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="open_decision_space",
)
async def open_decision_space(
    workspace_id: UUID,
    body: DecisionSpaceCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionSpaceResponse:
    try:
        space = await open_space(
            PostgresDecisionSpaces(session),
            workspace_id,
            identity.subject,
            question=body.question,
            description=body.description,
            deadline=body.deadline,
            lang=request.state.locale,
        )
        await session.commit()
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    except SpaceValidationError as error:
        raise _invalid(request) from error
    return DecisionSpaceResponse.model_validate(space)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}",
    response_model=DecisionSpaceDetailResponse,
    operation_id="get_decision_space",
)
async def read_decision_space(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionSpaceDetailResponse:
    try:
        snapshot = await get_space(
            PostgresDecisionSpaces(session), workspace_id, space_id, identity.subject
        )
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    return DecisionSpaceDetailResponse(
        **DecisionSpaceResponse.model_validate(snapshot.space).model_dump(),
        participants=[
            DecisionSpaceParticipantResponse.model_validate(participant)
            for participant in snapshot.participants
        ],
        history=[
            DecisionSpaceStatusEventResponse.model_validate(event) for event in snapshot.history
        ],
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/transitions",
    response_model=DecisionSpaceResponse,
    operation_id="transition_decision_space",
)
async def transition_decision_space(
    workspace_id: UUID,
    space_id: UUID,
    body: DecisionSpaceTransition,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionSpaceResponse:
    try:
        space = await transition_space(
            PostgresDecisionSpaces(session),
            workspace_id,
            space_id,
            identity.subject,
            to_status=body.to_status,
            reason=body.reason,
            lang=request.state.locale,
        )
        await session.commit()
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    except SpaceValidationError as error:
        raise _invalid(request) from error
    except SpaceForbiddenError as error:
        raise _forbidden(request) from error
    return DecisionSpaceResponse.model_validate(space)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/participants",
    response_model=list[DecisionSpaceParticipantResponse],
    status_code=status.HTTP_201_CREATED,
    operation_id="add_decision_space_participant",
)
async def add_decision_space_participant(
    workspace_id: UUID,
    space_id: UUID,
    body: ParticipantAdd,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[DecisionSpaceParticipantResponse]:
    try:
        participants = await add_participant(
            PostgresDecisionSpaces(session),
            workspace_id,
            space_id,
            identity.subject,
            user_id=body.user_id,
        )
        await session.commit()
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    except SpaceValidationError as error:
        raise _invalid(request) from error
    except SpaceForbiddenError as error:
        raise _forbidden(request) from error
    return [
        DecisionSpaceParticipantResponse.model_validate(participant) for participant in participants
    ]


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/participants/{user_id}",
    response_model=list[DecisionSpaceParticipantResponse],
    operation_id="remove_decision_space_participant",
)
async def remove_decision_space_participant(
    workspace_id: UUID,
    space_id: UUID,
    user_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[DecisionSpaceParticipantResponse]:
    try:
        participants = await remove_participant(
            PostgresDecisionSpaces(session),
            workspace_id,
            space_id,
            identity.subject,
            user_id=user_id,
        )
        await session.commit()
    except SpaceNotFoundError as error:
        raise _not_found(request) from error
    except SpaceValidationError as error:
        raise _invalid(request) from error
    except SpaceForbiddenError as error:
        raise _forbidden(request) from error
    return [
        DecisionSpaceParticipantResponse.model_validate(participant) for participant in participants
    ]
