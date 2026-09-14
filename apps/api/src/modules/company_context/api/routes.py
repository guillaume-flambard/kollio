from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.company_context.adapters.postgres import PostgresCompanyContext
from src.modules.company_context.api.schemas import (
    CompanyConstraintCreate,
    CompanyConstraintResponse,
    CompanyConstraintUpdate,
    CompanyContextResponse,
    CompanyProfileResponse,
    CompanyProfileWrite,
    MetricCreate,
    MetricResponse,
    MetricUpdate,
    ObjectiveCreate,
    ObjectiveResponse,
    ObjectiveUpdate,
    PrincipleCreate,
    PrincipleResponse,
    PrincipleUpdate,
)
from src.modules.company_context.service.context import (
    ConstraintNotFoundError,
    ContextNotFoundError,
    MetricNotFoundError,
    ObjectiveNotFoundError,
    PrincipleNotFoundError,
    create_constraint,
    create_metric,
    create_objective,
    create_principle,
    get_context,
    save_profile,
    update_constraint,
    update_metric,
    update_objective,
    update_principle,
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
            CompanyConstraintResponse.model_validate(constraint)
            for constraint in snapshot.constraints
        ],
        principles=[
            PrincipleResponse.model_validate(principle) for principle in snapshot.principles
        ],
        metrics=[MetricResponse.model_validate(metric) for metric in snapshot.metrics],
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
            request.state.locale,
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
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            title=body.title,
            lang=request.state.locale,
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
            request.state.locale,
        )
        await session.commit()
    except (ContextNotFoundError, ObjectiveNotFoundError) as error:
        raise _not_found(request) from error
    return ObjectiveResponse.model_validate(objective)


@router.post(
    "/{workspace_id}/company-context/constraints",
    response_model=CompanyConstraintResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_company_constraint",
)
async def create_company_constraint(
    workspace_id: UUID,
    body: CompanyConstraintCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> CompanyConstraintResponse:
    try:
        constraint = await create_constraint(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            title=body.title,
            detail=body.detail,
            lang=request.state.locale,
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return CompanyConstraintResponse.model_validate(constraint)


@router.patch(
    "/{workspace_id}/company-context/constraints/{constraint_id}",
    response_model=CompanyConstraintResponse,
    operation_id="update_company_constraint",
)
async def update_company_constraint(
    workspace_id: UUID,
    constraint_id: UUID,
    body: CompanyConstraintUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> CompanyConstraintResponse:
    try:
        constraint = await update_constraint(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            constraint_id,
            body.model_dump(exclude_unset=True),
            request.state.locale,
        )
        await session.commit()
    except (ContextNotFoundError, ConstraintNotFoundError) as error:
        raise _not_found(request) from error
    return CompanyConstraintResponse.model_validate(constraint)


@router.post(
    "/{workspace_id}/company-context/principles",
    response_model=PrincipleResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_company_principle",
)
async def create_company_principle(
    workspace_id: UUID,
    body: PrincipleCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> PrincipleResponse:
    try:
        principle = await create_principle(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            title=body.title,
            detail=body.detail,
            lang=request.state.locale,
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return PrincipleResponse.model_validate(principle)


@router.patch(
    "/{workspace_id}/company-context/principles/{principle_id}",
    response_model=PrincipleResponse,
    operation_id="update_company_principle",
)
async def update_company_principle(
    workspace_id: UUID,
    principle_id: UUID,
    body: PrincipleUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> PrincipleResponse:
    try:
        principle = await update_principle(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            principle_id,
            body.model_dump(exclude_unset=True),
            request.state.locale,
        )
        await session.commit()
    except (ContextNotFoundError, PrincipleNotFoundError) as error:
        raise _not_found(request) from error
    return PrincipleResponse.model_validate(principle)


@router.post(
    "/{workspace_id}/company-context/metrics",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_company_metric",
)
async def create_company_metric(
    workspace_id: UUID,
    body: MetricCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> MetricResponse:
    try:
        metric = await create_metric(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            name=body.name,
            value=body.value,
            unit=body.unit,
            observed_at=body.observed_at,
            source=body.source,
            lang=request.state.locale,
        )
        await session.commit()
    except ContextNotFoundError as error:
        raise _not_found(request) from error
    return MetricResponse.model_validate(metric)


@router.patch(
    "/{workspace_id}/company-context/metrics/{metric_id}",
    response_model=MetricResponse,
    operation_id="update_company_metric",
)
async def update_company_metric(
    workspace_id: UUID,
    metric_id: UUID,
    body: MetricUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> MetricResponse:
    try:
        metric = await update_metric(
            PostgresCompanyContext(session),
            workspace_id,
            identity.subject,
            metric_id,
            body.model_dump(exclude_unset=True),
            request.state.locale,
        )
        await session.commit()
    except (ContextNotFoundError, MetricNotFoundError) as error:
        raise _not_found(request) from error
    return MetricResponse.model_validate(metric)
