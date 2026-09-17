from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from opentelemetry.propagate import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.challenge.adapters.postgres import PostgresChallenge
from src.modules.challenge.api.schemas import (
    ChallengeCoverageResponse,
    ChallengeFindingCreate,
    ChallengeFindingResponse,
    ChallengeListResponse,
    ChallengeRunDetailResponse,
    ChallengeRunResponse,
    FindingResolutionRequest,
)
from src.modules.challenge.domain.coverage import Coverage
from src.modules.challenge.service.challenge import (
    ChallengeForbiddenError,
    ChallengeNotFoundError,
    ChallengeValidationError,
    complete_challenge,
    list_challenges,
    open_challenge,
    read_challenge,
    record_finding,
    resolve_finding,
)
from src.modules.challenge.service.ports import ChallengeQueue
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["challenge"])


def get_challenge_queue(request: Request) -> ChallengeQueue:
    return cast(ChallengeQueue, request.app.state.challenge_queue)


def _trace_context() -> dict[str, str]:
    carrier: dict[str, str] = {}
    inject(carrier)
    return carrier


def _not_found(request: Request, key: str = "not_found_challenge") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale][key])


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


def _coverage(coverage: Coverage) -> ChallengeCoverageResponse:
    return ChallengeCoverageResponse(
        covered=sorted(coverage.covered), uncovered=sorted(coverage.uncovered)
    )


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges",
    response_model=ChallengeListResponse,
    operation_id="list_challenges",
)
async def list_option_challenges(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ChallengeListResponse:
    try:
        snapshot = await list_challenges(
            PostgresChallenge(session), workspace_id, space_id, option_id, identity.subject
        )
    except ChallengeNotFoundError as error:
        raise _not_found(request, "not_found_option") from error
    return ChallengeListResponse(
        runs=[ChallengeRunResponse.model_validate(run) for run in snapshot.runs],
        findings=[
            ChallengeFindingResponse.model_validate(finding) for finding in snapshot.findings
        ],
        coverage=_coverage(snapshot.coverage),
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges",
    response_model=ChallengeRunResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="open_challenge",
)
async def open_option_challenge(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
    queue: ChallengeQueue = Depends(get_challenge_queue),
) -> ChallengeRunResponse:
    try:
        run = await open_challenge(
            PostgresChallenge(session),
            workspace_id,
            space_id,
            option_id,
            identity.subject,
            lang=request.state.locale,
            queue=queue,
            trace_context=_trace_context(),
        )
        await session.commit()
    except ChallengeNotFoundError as error:
        raise _not_found(request, "not_found_option") from error
    except ChallengeForbiddenError as error:
        raise _forbidden(request) from error
    return ChallengeRunResponse.model_validate(run)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges/{run_id}",
    response_model=ChallengeRunDetailResponse,
    operation_id="get_challenge",
)
async def read_option_challenge(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ChallengeRunDetailResponse:
    try:
        snapshot = await read_challenge(
            PostgresChallenge(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            identity.subject,
        )
    except ChallengeNotFoundError as error:
        raise _not_found(request) from error
    return ChallengeRunDetailResponse(
        run=ChallengeRunResponse.model_validate(snapshot.run),
        findings=[
            ChallengeFindingResponse.model_validate(finding) for finding in snapshot.findings
        ],
        coverage=_coverage(snapshot.coverage),
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges/{run_id}/findings",
    response_model=ChallengeFindingResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="record_challenge_finding",
)
async def record_challenge_finding(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    body: ChallengeFindingCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ChallengeFindingResponse:
    try:
        finding = await record_finding(
            PostgresChallenge(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            identity.subject,
            kind=body.kind,
            severity=body.severity,
            detail=body.detail,
            contribution_id=body.contribution_id,
            lang=request.state.locale,
        )
        await session.commit()
    except ChallengeNotFoundError as error:
        raise _not_found(request) from error
    except ChallengeValidationError as error:
        raise _invalid(request) from error
    except ChallengeForbiddenError as error:
        raise _forbidden(request) from error
    return ChallengeFindingResponse.model_validate(finding)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges/{run_id}"
    "/findings/{finding_id}/resolution",
    response_model=ChallengeFindingResponse,
    operation_id="resolve_challenge_finding",
)
async def resolve_challenge_finding(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    finding_id: UUID,
    body: FindingResolutionRequest,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ChallengeFindingResponse:
    try:
        finding = await resolve_finding(
            PostgresChallenge(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            finding_id,
            identity.subject,
            resolution=body.resolution,
            lang=request.state.locale,
        )
        await session.commit()
    except ChallengeNotFoundError as error:
        raise _not_found(request, "not_found_finding") from error
    except ChallengeForbiddenError as error:
        raise _forbidden(request) from error
    return ChallengeFindingResponse.model_validate(finding)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/challenges/{run_id}/completion",
    response_model=ChallengeRunResponse,
    operation_id="complete_challenge",
)
async def complete_option_challenge(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ChallengeRunResponse:
    try:
        run = await complete_challenge(
            PostgresChallenge(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            identity.subject,
            lang=request.state.locale,
        )
        await session.commit()
    except ChallengeNotFoundError as error:
        raise _not_found(request) from error
    except ChallengeValidationError as error:
        raise _invalid(request) from error
    except ChallengeForbiddenError as error:
        raise _forbidden(request) from error
    return ChallengeRunResponse.model_validate(run)
