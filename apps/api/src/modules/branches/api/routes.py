from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.branches.adapters.postgres import PostgresBranches
from src.modules.branches.api.schemas import (
    BranchCreate,
    BranchListResponse,
    BranchResponse,
    ContributionListResponse,
    ContributionPropose,
    ContributionResponse,
)
from src.modules.branches.service.branches import (
    BranchForbiddenError,
    BranchNotFoundError,
    BranchValidationError,
    ContributionNotFoundError,
    confirm_contribution,
    create_branch,
    get_branch,
    list_branches,
    list_contributions,
    propose_contribution,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["branches"])


def _not_found(request: Request, key: str = "not_found_branch") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale][key])


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/branches",
    response_model=BranchListResponse,
    operation_id="list_branches",
)
async def list_branches_in_space(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> BranchListResponse:
    try:
        branches = await list_branches(
            PostgresBranches(session), workspace_id, space_id, identity.subject
        )
    except BranchNotFoundError as error:
        raise _not_found(request, "not_found_space") from error
    return BranchListResponse(items=[BranchResponse.model_validate(branch) for branch in branches])


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/branches",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_branch",
)
async def create_branch_in_space(
    workspace_id: UUID,
    space_id: UUID,
    body: BranchCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> BranchResponse:
    try:
        branch = await create_branch(
            PostgresBranches(session),
            workspace_id,
            space_id,
            identity.subject,
            title=body.title,
            summary=body.summary,
            visibility=body.visibility,
            lang=request.state.locale,
        )
        await session.commit()
    except BranchNotFoundError as error:
        raise _not_found(request, "not_found_space") from error
    except BranchValidationError as error:
        raise _invalid(request) from error
    except BranchForbiddenError as error:
        raise _forbidden(request) from error
    return BranchResponse.model_validate(branch)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/branches/{branch_id}",
    response_model=BranchResponse,
    operation_id="get_branch",
)
async def read_branch(
    workspace_id: UUID,
    space_id: UUID,
    branch_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> BranchResponse:
    try:
        branch = await get_branch(
            PostgresBranches(session), workspace_id, space_id, branch_id, identity.subject
        )
    except BranchNotFoundError as error:
        raise _not_found(request) from error
    return BranchResponse.model_validate(branch)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/contributions",
    response_model=ContributionResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="propose_contribution",
)
async def propose_contribution_in_space(
    workspace_id: UUID,
    space_id: UUID,
    body: ContributionPropose,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ContributionResponse:
    try:
        contribution = await propose_contribution(
            PostgresBranches(session),
            workspace_id,
            space_id,
            identity.subject,
            branch_id=body.branch_id,
            kind=body.kind,
            title=body.title,
            body=body.body,
            source=body.source,
            tool_model=body.tool_model,
            transformation_history=body.transformation_history,
            as_suggestion=False,
            lang=request.state.locale,
        )
        await session.commit()
    except BranchNotFoundError as error:
        raise _not_found(request) from error
    except BranchValidationError as error:
        raise _invalid(request) from error
    except BranchForbiddenError as error:
        raise _forbidden(request) from error
    return ContributionResponse.model_validate(contribution)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/contributions",
    response_model=ContributionListResponse,
    operation_id="list_contributions",
)
async def list_contributions_in_space(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ContributionListResponse:
    try:
        contributions = await list_contributions(
            PostgresBranches(session), workspace_id, space_id, identity.subject
        )
    except BranchNotFoundError as error:
        raise _not_found(request, "not_found_space") from error
    return ContributionListResponse(
        items=[ContributionResponse.model_validate(contribution) for contribution in contributions]
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/contributions/{contribution_id}/confirmation",
    response_model=ContributionResponse,
    operation_id="confirm_contribution",
)
async def confirm_contribution_in_space(
    workspace_id: UUID,
    space_id: UUID,
    contribution_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ContributionResponse:
    try:
        contribution = await confirm_contribution(
            PostgresBranches(session),
            workspace_id,
            space_id,
            contribution_id,
            identity.subject,
        )
        await session.commit()
    except BranchNotFoundError as error:
        raise _not_found(request, "not_found_space") from error
    except ContributionNotFoundError as error:
        raise _not_found(request, "not_found_contribution") from error
    except BranchForbiddenError as error:
        raise _forbidden(request) from error
    return ContributionResponse.model_validate(contribution)
