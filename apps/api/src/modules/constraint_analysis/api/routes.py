from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from opentelemetry.propagate import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.constraint_analysis.adapters.postgres import PostgresAnalysisWorkflows
from src.modules.constraint_analysis.api.schemas import (
    AnalysisWorkflowResponse,
    LaunchAnalysisRequest,
    ReviewAnalysisRequest,
)
from src.modules.constraint_analysis.domain.lifecycle import InvalidAnalysisTransition
from src.modules.constraint_analysis.service.operations import (
    AnalysisAuthorizationError,
    AnalysisNotFoundError,
    get_analysis,
    launch_analysis,
    request_review,
)
from src.modules.constraint_analysis.service.ports import AnalysisQueue
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/ideas/{idea_id}/analyses", tags=["constraint-analysis"])


def get_analysis_queue(request: Request) -> AnalysisQueue:
    return cast(AnalysisQueue, request.app.state.analysis_queue)


def _trace_context() -> dict[str, str]:
    carrier: dict[str, str] = {}
    inject(carrier)
    return carrier


@router.post(
    "",
    response_model=AnalysisWorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="launch_constraint_analysis",
)
async def launch(
    idea_id: UUID,
    body: LaunchAnalysisRequest,
    request: Request,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    queue: Annotated[AnalysisQueue, Depends(get_analysis_queue)],
    idempotency_key: Annotated[str, Header(min_length=8, max_length=200)],
) -> AnalysisWorkflowResponse:
    try:
        outcome = await launch_analysis(
            PostgresAnalysisWorkflows(session),
            idea_id,
            identity.subject,
            idempotency_key=idempotency_key,
            locale=request.state.locale,
            evidence=body.evidence,
            trace_context=_trace_context(),
        )
        await session.commit()
        await session.refresh(outcome.workflow)
        if outcome.created:
            await queue.dispatch(outcome.workflow.id, outcome.workflow.trace_context)
    except AnalysisNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found"]
        ) from error
    return AnalysisWorkflowResponse.model_validate(outcome.workflow)


@router.get(
    "/{workflow_id}",
    response_model=AnalysisWorkflowResponse,
    operation_id="get_constraint_analysis",
)
async def read(
    idea_id: UUID,
    workflow_id: UUID,
    request: Request,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AnalysisWorkflowResponse:
    try:
        workflow = await get_analysis(
            PostgresAnalysisWorkflows(session), idea_id, workflow_id, identity.subject
        )
    except AnalysisNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found"]
        ) from error
    return AnalysisWorkflowResponse.model_validate(workflow)


@router.post(
    "/{workflow_id}/review",
    response_model=AnalysisWorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="review_constraint_analysis",
)
async def review(
    idea_id: UUID,
    workflow_id: UUID,
    body: ReviewAnalysisRequest,
    request: Request,
    identity: Annotated[Identity, Depends(current_identity)],
    session: Annotated[AsyncSession, Depends(get_session)],
    queue: Annotated[AnalysisQueue, Depends(get_analysis_queue)],
) -> AnalysisWorkflowResponse:
    trace_context = _trace_context()
    try:
        workflow = await request_review(
            PostgresAnalysisWorkflows(session),
            idea_id,
            workflow_id,
            identity.subject,
            approved=body.approved,
            trace_context=trace_context,
        )
        await session.commit()
        await session.refresh(workflow)
        await queue.dispatch_review(workflow.id, body.approved, trace_context)
    except AnalysisNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found"]
        ) from error
    except AnalysisAuthorizationError as error:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"]
        ) from error
    except InvalidAnalysisTransition as error:
        raise HTTPException(
            status.HTTP_409_CONFLICT, MESSAGES[request.state.locale]["conflict"]
        ) from error
    return AnalysisWorkflowResponse.model_validate(workflow)
