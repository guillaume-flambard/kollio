from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.company_context.adapters.postgres import PostgresCompanyContext
from src.modules.company_context.api.schemas import (
    CompanyContextResponse,
    CompanyProfileResponse,
    CompanyProfileWrite,
    ConstraintCreate,
    ConstraintResponse,
    ConstraintUpdate,
    ObjectiveCreate,
    ObjectiveResponse,
    ObjectiveUpdate,
)
from src.modules.company_context.service.context import (
    ConstraintNotFoundError,
    ContextNotFoundError,
    ObjectiveNotFoundError,
    create_constraint,
    create_objective,
    get_context,
    save_profile,
    update_constraint,
    update_objective,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["company-context"])


def _not_found(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_workspace"]
    )


@router.get(
    "/{workspace_id}/company-context",
    response_model=CompanyContextResponse,
    operation_id="get_company_context",
)
async def read_company_context(
    workspace_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> CompanyContextResponse:
    try:
        snapshot = await get_context(
            PostgresCompanyContext(session), workspace_id, identity.subject
        )
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return CompanyContextResponse(
        profile=CompanyProfileResponse.model_validate(snapshot.profile)
        if snapshot.profile is not None
        else CompanyProfileResponse(),
        objectives=[
            ObjectiveResponse.model_validate(objective) for objective in snapshot.objectives
        ],
        constraints=[
            ConstraintResponse.model_validate(constraint) for constraint in snapshot.constraints
        ],
    )


@router.put(
    "/{workspace_id}/company-context/profile",
    response_model=CompanyProfileResponse,
    operation_id="save_company_profile",
)
async def save_company_profile(
    workspace_id: UUID,
    body: CompanyProfileWrite,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> CompanyProfileResponse:
    try:
        profile = await save_profile(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            body.model_dump(),
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return CompanyProfileResponse.model_validate(profile)


@router.post(
    "/{workspace_id}/company-context/objectives",
    response_model=ObjectiveResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_company_objective",
)
async def create_company_objective(
    workspace_id: UUID,
    body: ObjectiveCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ObjectiveResponse:
    try:
        objective = await create_objective(
            PostgresCompanyContext(session), workspace_id, identity.subject, title=body.title
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return ObjectiveResponse.model_validate(objective)


@router.patch(
    "/{workspace_id}/company-context/objectives/{objective_id}",
    response_model=ObjectiveResponse,
    operation_id="update_company_objective",
)
async def update_company_objective(
    workspace_id: UUID,
    objective_id: UUID,
    body: ObjectiveUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ObjectiveResponse:
    try:
        objective = await update_objective(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            objective_id,
            body.model_dump(exclude_unset=True),
        )
        await session.commit()
    except (ContextNotFoundError, ObjectiveNotFoundError) as error:
        raise _not_found(request) from error
    return ObjectiveResponse.model_validate(objective)


@router.post(
    "/{workspace_id}/company-context/constraints",
    response_model=ConstraintResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_company_constraint",
)
async def create_company_constraint(
    workspace_id: UUID,
    body: ConstraintCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ConstraintResponse:
    try:
        constraint = await create_constraint(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            title=body.title,
            detail=body.detail,
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return ConstraintResponse.model_validate(constraint)


@router.patch(
    "/{workspace_id}/company-context/constraints/{constraint_id}",
    response_model=ConstraintResponse,
    operation_id="update_company_constraint",
)
async def update_company_constraint(
    workspace_id: UUID,
    constraint_id: UUID,
    body: ConstraintUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ConstraintResponse:
    try:
        constraint = await update_constraint(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            constraint_id,
            body.model_dump(exclude_unset=True),
        )
        await session.commit()
    except (ContextNotFoundError, ConstraintNotFoundError) as error:
        raise _not_found(request) from error
    return ConstraintResponse.model_validate(constraint)
