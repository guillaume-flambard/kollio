from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from opentelemetry.propagate import inject
from sqlalchemy.exc import IntegrityError
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
    LaunchOutcome,
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
        repository = PostgresAnalysisWorkflows(session)
        outcome = await launch_analysis(
            repository,
            idea_id,
            identity.subject,
            idempotency_key=idempotency_key,
            locale=request.state.locale,
            evidence=body.evidence,
            trace_context=_trace_context(),
        )
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            existing = await repository.find_launch(idea_id, idempotency_key)
            if existing is None:
                raise
            outcome = LaunchOutcome(existing, created=False)
        await session.refresh(outcome.workflow)
        response_workflow = outcome.workflow
        dispatch_pending = outcome.workflow.current_step == "dispatch"
        if outcome.created or dispatch_pending:
            locked_workflow = await repository.get_for_worker(outcome.workflow.id, lock=True)
            if locked_workflow is None:
                raise AnalysisNotFoundError
            if locked_workflow.current_step == "dispatch":
                try:
                    await queue.dispatch(locked_workflow.id, locked_workflow.trace_context)
                except Exception as error:
                    raise HTTPException(
                        status.HTTP_503_SERVICE_UNAVAILABLE,
                        MESSAGES[request.state.locale]["unavailable"],
                    ) from error
                locked_workflow.current_step = "queued"
                await session.commit()
                await session.refresh(locked_workflow)
            response_workflow = locked_workflow
    except AnalysisNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found"]
        ) from error
    return AnalysisWorkflowResponse.model_validate(response_workflow)


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
        repository = PostgresAnalysisWorkflows(session)
        workflow = await request_review(
            repository,
            idea_id,
            workflow_id,
            identity.subject,
            approved=body.approved,
            trace_context=trace_context,
        )
        await session.commit()
        await session.refresh(workflow)
        locked_workflow = await repository.get_for_worker(workflow.id, lock=True)
        if locked_workflow is None:
            raise AnalysisNotFoundError
        if locked_workflow.current_step == "dispatch_review":
            try:
                await queue.dispatch_review(locked_workflow.id, body.approved, trace_context)
            except Exception as error:
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    MESSAGES[request.state.locale]["unavailable"],
                ) from error
            locked_workflow.current_step = "review_queued"
            await session.commit()
            await session.refresh(locked_workflow)
        workflow = locked_workflow
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
