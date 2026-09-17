from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.options.adapters.postgres import PostgresOptions
from src.modules.options.api.schemas import (
    EvidenceLink,
    OptionCreate,
    OptionDetailResponse,
    OptionEvidenceResponse,
    OptionListResponse,
    OptionResponse,
    OptionUpdate,
)
from src.modules.options.service.options import (
    OptionForbiddenError,
    OptionNotFoundError,
    OptionSnapshot,
    OptionValidationError,
    create_option,
    delete_option,
    get_option,
    link_evidence,
    list_options,
    unlink_evidence,
    update_option,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["options"])

TEXT_FIELDS = (
    "mechanism",
    "upside",
    "cost",
    "risks",
    "critical_assumptions",
    "success_metrics",
)


def _not_found(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_option"]
    )


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


def _detail(snapshot: OptionSnapshot) -> OptionDetailResponse:
    return OptionDetailResponse(
        **OptionResponse.model_validate(snapshot.option).model_dump(),
        evidence=[OptionEvidenceResponse.model_validate(link) for link in snapshot.evidence],
    )


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options",
    response_model=OptionListResponse,
    operation_id="list_options",
)
async def list_options_in_space(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionListResponse:
    try:
        options = await list_options(
            PostgresOptions(session), workspace_id, space_id, identity.subject
        )
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    return OptionListResponse(items=[OptionResponse.model_validate(option) for option in options])


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options",
    response_model=OptionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_option",
)
async def create_option_in_space(
    workspace_id: UUID,
    space_id: UUID,
    body: OptionCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionDetailResponse:
    try:
        snapshot = await create_option(
            PostgresOptions(session),
            workspace_id,
            space_id,
            identity.subject,
            title=body.title,
            proposal=body.proposal,
            fields={field: getattr(body, field) for field in TEXT_FIELDS},
            lang=request.state.locale,
        )
        await session.commit()
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    except OptionValidationError as error:
        raise _invalid(request) from error
    except OptionForbiddenError as error:
        raise _forbidden(request) from error
    return _detail(snapshot)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}",
    response_model=OptionDetailResponse,
    operation_id="get_option",
)
async def read_option(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionDetailResponse:
    try:
        snapshot = await get_option(
            PostgresOptions(session), workspace_id, space_id, option_id, identity.subject
        )
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    return _detail(snapshot)


@router.patch(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}",
    response_model=OptionDetailResponse,
    operation_id="update_option",
)
async def update_option_in_space(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    body: OptionUpdate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionDetailResponse:
    try:
        snapshot = await update_option(
            PostgresOptions(session),
            workspace_id,
            space_id,
            option_id,
            identity.subject,
            values=body.model_dump(exclude_unset=True),
            lang=request.state.locale,
        )
        await session.commit()
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    except OptionValidationError as error:
        raise _invalid(request) from error
    except OptionForbiddenError as error:
        raise _forbidden(request) from error
    return _detail(snapshot)


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_option",
)
async def delete_option_in_space(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> Response:
    try:
        await delete_option(
            PostgresOptions(session), workspace_id, space_id, option_id, identity.subject
        )
        await session.commit()
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    except OptionValidationError as error:
        raise _invalid(request) from error
    except OptionForbiddenError as error:
        raise _forbidden(request) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/evidence",
    response_model=OptionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="link_option_evidence",
)
async def link_option_evidence(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    body: EvidenceLink,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionDetailResponse:
    try:
        snapshot = await link_evidence(
            PostgresOptions(session),
            workspace_id,
            space_id,
            option_id,
            identity.subject,
            contribution_id=body.contribution_id,
            side=body.side,
        )
        await session.commit()
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    except OptionValidationError as error:
        raise _invalid(request) from error
    except OptionForbiddenError as error:
        raise _forbidden(request) from error
    return _detail(snapshot)


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/evidence/{contribution_id}",
    response_model=OptionDetailResponse,
    operation_id="unlink_option_evidence",
)
async def unlink_option_evidence(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    contribution_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OptionDetailResponse:
    try:
        snapshot = await unlink_evidence(
            PostgresOptions(session),
            workspace_id,
            space_id,
            option_id,
            contribution_id,
            identity.subject,
        )
        await session.commit()
    except OptionNotFoundError as error:
        raise _not_found(request) from error
    except OptionValidationError as error:
        raise _invalid(request) from error
    except OptionForbiddenError as error:
        raise _forbidden(request) from error
    return _detail(snapshot)
