from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.iterations.adapters.postgres import PostgresIterations
from src.modules.iterations.api.schemas import (
    CreateIterationRequest,
    IterationResponse,
    ResolveProposalRequest,
    RollbackRequest,
)
from src.modules.iterations.domain.rules import (
    AuthorizationError,
    ConflictError,
    InvalidTransitionError,
)
from src.modules.iterations.service.operations import (
    IterationNotFoundError,
    accept_proposal,
    create_iteration,
    list_iterations,
    reject_proposal,
    rollback_iteration,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/ideas/{idea_id}/iterations", tags=["iterations"])


def _transition_error(request: Request, error: Exception) -> HTTPException:
    messages = MESSAGES[request.state.locale]
    if isinstance(error, IterationNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, messages["not_found"])
    if isinstance(error, AuthorizationError):
        return HTTPException(status.HTTP_403_FORBIDDEN, messages["forbidden"])
    if isinstance(error, (ConflictError, InvalidTransitionError)):
        return HTTPException(status.HTTP_409_CONFLICT, messages["conflict"])
    raise error


@router.get("", response_model=list[IterationResponse], operation_id="list_idea_iterations")
async def read_iterations(
    idea_id: UUID,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> list[IterationResponse]:
    try:
        iterations = await list_iterations(PostgresIterations(session), idea_id, identity.subject)
    except IterationNotFoundError as error:
        raise _transition_error(request, error) from error
    return [IterationResponse.model_validate(iteration) for iteration in iterations]


@router.post(
    "",
    response_model=IterationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_idea_iteration",
)
async def append_iteration(
    idea_id: UUID,
    body: CreateIterationRequest,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> IterationResponse:
    try:
        iteration = await create_iteration(
            PostgresIterations(session),
            idea_id,
            identity.subject,
            message=body.message,
            lang=body.lang,
            snapshot=body.snapshot,
            branch=body.branch,
            expected_parent_id=body.expected_parent_id,
        )
        await session.commit()
    except (IterationNotFoundError, AuthorizationError, ConflictError) as error:
        raise _transition_error(request, error) from error
    return IterationResponse.model_validate(iteration)


@router.post(
    "/{iteration_id}/accept",
    response_model=IterationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="accept_idea_iteration",
)
async def accept_iteration(
    idea_id: UUID,
    iteration_id: UUID,
    body: ResolveProposalRequest,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> IterationResponse:
    try:
        iteration = await accept_proposal(
            PostgresIterations(session),
            idea_id,
            iteration_id,
            identity.subject,
            expected_main_parent_id=body.expected_main_parent_id,
        )
        await session.commit()
    except (
        IterationNotFoundError,
        AuthorizationError,
        ConflictError,
        InvalidTransitionError,
    ) as error:
        raise _transition_error(request, error) from error
    return IterationResponse.model_validate(iteration)


@router.post(
    "/{iteration_id}/reject",
    response_model=IterationResponse,
    operation_id="reject_idea_iteration",
)
async def reject_iteration(
    idea_id: UUID,
    iteration_id: UUID,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> IterationResponse:
    try:
        iteration = await reject_proposal(
            PostgresIterations(session), idea_id, iteration_id, identity.subject
        )
        await session.commit()
    except (
        IterationNotFoundError,
        AuthorizationError,
        ConflictError,
        InvalidTransitionError,
    ) as error:
        raise _transition_error(request, error) from error
    return IterationResponse.model_validate(iteration)


@router.post(
    "/{iteration_id}/rollback",
    response_model=IterationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="rollback_idea_iteration",
)
async def restore_iteration(
    idea_id: UUID,
    iteration_id: UUID,
    body: RollbackRequest,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> IterationResponse:
    try:
        iteration = await rollback_iteration(
            PostgresIterations(session),
            idea_id,
            iteration_id,
            identity.subject,
            expected_main_parent_id=body.expected_main_parent_id,
            message=body.message,
            lang=body.lang,
        )
        await session.commit()
    except (
        IterationNotFoundError,
        AuthorizationError,
        ConflictError,
        InvalidTransitionError,
    ) as error:
        raise _transition_error(request, error) from error
    return IterationResponse.model_validate(iteration)
