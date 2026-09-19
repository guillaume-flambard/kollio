from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.experiments.adapters.postgres import PostgresExperiments
from src.modules.experiments.api.schemas import (
    ExperimentCreateBody,
    ExperimentDetailResponse,
    ExperimentResponse,
    ExperimentStatusBody,
    LearningResponse,
    LearningWriteBody,
    OutcomeCreateBody,
    OutcomeResponse,
)
from src.modules.experiments.domain.lifecycle import ExperimentRuleError
from src.modules.experiments.service.operations import (
    ExperimentNotFoundError,
    change_status,
    create_experiment,
    list_experiments,
    list_learnings,
    list_space_experiments,
    list_space_learnings,
    read_experiment,
    record_outcome,
    write_learning,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session

router = APIRouter()
space_experiments_router = APIRouter()


def _not_found(request: Request) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "experiment_not_found", "message": "This experiment is not visible to you"},
        headers={"x-request-id": getattr(request.state, "request_id", "")},
    )


def _rule_error(request: Request, error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={"code": "experiment_rule", "message": str(error)},
        headers={"x-request-id": getattr(request.state, "request_id", "")},
    )


@router.post(
    "/ideas/{idea_id}/experiments",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_experiment",
)
async def create_idea_experiment(
    idea_id: UUID,
    body: ExperimentCreateBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ExperimentResponse:
    try:
        experiment = await create_experiment(
            PostgresExperiments(session),
            idea_id=idea_id,
            subject=identity.subject,
            title=body.title,
            hypothesis=body.hypothesis,
            success_metric=body.success_metric,
            baseline=body.baseline,
            target=body.target,
            decision_space_id=body.decision_space_id,
            option_id=body.option_id,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    except ExperimentRuleError as error:
        raise _rule_error(request, error) from error
    await session.commit()
    return ExperimentResponse.model_validate(experiment)


@router.get(
    "/ideas/{idea_id}/experiments",
    response_model=list[ExperimentResponse],
    operation_id="list_idea_experiments",
)
async def list_idea_experiments(
    idea_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[ExperimentResponse]:
    try:
        experiments = await list_experiments(
            PostgresExperiments(session), idea_id=idea_id, subject=identity.subject
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    return [ExperimentResponse.model_validate(item) for item in experiments]


@router.get(
    "/ideas/{idea_id}/learnings",
    response_model=list[LearningResponse],
    operation_id="list_idea_learnings",
)
async def list_idea_learnings(
    idea_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[LearningResponse]:
    try:
        learnings = await list_learnings(
            PostgresExperiments(session), idea_id=idea_id, subject=identity.subject
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    return [LearningResponse.model_validate(item) for item in learnings]


@router.get(
    "/experiments/{experiment_id}",
    response_model=ExperimentDetailResponse,
    operation_id="get_experiment",
)
async def get_experiment(
    experiment_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ExperimentDetailResponse:
    try:
        experiment, outcomes, learning = await read_experiment(
            PostgresExperiments(session), experiment_id=experiment_id, subject=identity.subject
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    return ExperimentDetailResponse(
        experiment=ExperimentResponse.model_validate(experiment),
        outcomes=[OutcomeResponse.model_validate(item) for item in outcomes],
        learning=LearningResponse.model_validate(learning) if learning is not None else None,
    )


@router.post(
    "/experiments/{experiment_id}/status",
    response_model=ExperimentResponse,
    operation_id="change_experiment_status",
)
async def change_experiment_status(
    experiment_id: UUID,
    body: ExperimentStatusBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ExperimentResponse:
    try:
        experiment = await change_status(
            PostgresExperiments(session),
            experiment_id=experiment_id,
            subject=identity.subject,
            target=body.status,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    except ExperimentRuleError as error:
        raise _rule_error(request, error) from error
    await session.commit()
    return ExperimentResponse.model_validate(experiment)


@router.post(
    "/experiments/{experiment_id}/outcomes",
    response_model=OutcomeResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="record_experiment_outcome",
)
async def record_experiment_outcome(
    experiment_id: UUID,
    body: OutcomeCreateBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> OutcomeResponse:
    try:
        outcome = await record_outcome(
            PostgresExperiments(session),
            experiment_id=experiment_id,
            subject=identity.subject,
            metric=body.metric,
            value=body.value,
            unit=body.unit,
            observed_at=body.observed_at,
            comment=body.comment,
            qualitative=body.qualitative,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    await session.commit()
    return OutcomeResponse.model_validate(outcome)


@router.post(
    "/experiments/{experiment_id}/learnings",
    response_model=LearningResponse,
    operation_id="write_experiment_learning",
)
async def write_experiment_learning(
    experiment_id: UUID,
    body: LearningWriteBody,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> LearningResponse:
    try:
        learning = await write_learning(
            PostgresExperiments(session),
            experiment_id=experiment_id,
            subject=identity.subject,
            text=body.text,
            confirm=body.confirm,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    except ExperimentRuleError as error:
        raise _rule_error(request, error) from error
    await session.commit()
    return LearningResponse.model_validate(learning)


@space_experiments_router.get(
    "/workspaces/{workspace_id}/decision-spaces/{space_id}/experiments",
    response_model=list[ExperimentResponse],
    operation_id="list_space_experiments",
)
async def list_decision_space_experiments(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[ExperimentResponse]:
    try:
        experiments = await list_space_experiments(
            PostgresExperiments(session),
            workspace_id=workspace_id,
            space_id=space_id,
            subject=identity.subject,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    return [ExperimentResponse.model_validate(item) for item in experiments]


@space_experiments_router.get(
    "/workspaces/{workspace_id}/decision-spaces/{space_id}/learnings",
    response_model=list[LearningResponse],
    operation_id="list_space_learnings",
)
async def list_decision_space_learnings(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> list[LearningResponse]:
    try:
        learnings = await list_space_learnings(
            PostgresExperiments(session),
            workspace_id=workspace_id,
            space_id=space_id,
            subject=identity.subject,
        )
    except ExperimentNotFoundError as error:
        raise _not_found(request) from error
    return [LearningResponse.model_validate(item) for item in learnings]
