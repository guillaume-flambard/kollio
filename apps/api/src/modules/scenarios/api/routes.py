from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.scenarios.adapters.postgres import PostgresScenarios
from src.modules.scenarios.api.schemas import (
    CriterionDirection,
    RunValueResponse,
    ScenarioRunListResponse,
    ScenarioRunResponse,
    ScenarioRunWrite,
    ScenarioVariableListResponse,
    ScenarioVariableResponse,
    ScenarioVariableWrite,
    SensitivityCriterionResponse,
    SensitivityEvidenceResponse,
    SensitivityResponse,
    SensitivityVariableResponse,
)
from src.modules.scenarios.service.scenarios import (
    RunSnapshot,
    ScenarioForbiddenError,
    ScenarioNotFoundError,
    ScenarioValidationError,
    create_run,
    create_variable,
    delete_run,
    delete_variable,
    list_runs,
    list_variables,
    read_sensitivity,
    update_run,
    update_variable,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["scenarios"])


def _not_found(request: Request, key: str = "not_found_space") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale][key])


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


def _run_response(snapshot: RunSnapshot) -> ScenarioRunResponse:
    return ScenarioRunResponse(
        id=snapshot.run.id,
        option_id=snapshot.run.option_id,
        level=snapshot.run.level,
        assumptions=snapshot.run.assumptions,
        created_by=snapshot.run.created_by,
        lang=snapshot.run.lang,
        created_at=snapshot.run.created_at,
        updated_at=snapshot.run.updated_at,
        values=[
            RunValueResponse(variable_id=variable_id, value=value)
            for variable_id, value in sorted(snapshot.values.items(), key=lambda item: str(item[0]))
        ],
    )


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/scenario-variables",
    response_model=ScenarioVariableListResponse,
    operation_id="list_scenario_variables",
)
async def list_scenario_variables(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioVariableListResponse:
    try:
        variables = await list_variables(
            PostgresScenarios(session), workspace_id, space_id, identity.subject
        )
    except ScenarioNotFoundError as error:
        raise _not_found(request) from error
    return ScenarioVariableListResponse(
        items=[ScenarioVariableResponse.model_validate(variable) for variable in variables]
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/scenario-variables",
    response_model=ScenarioVariableResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_scenario_variable",
)
async def create_scenario_variable(
    workspace_id: UUID,
    space_id: UUID,
    body: ScenarioVariableWrite,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioVariableResponse:
    try:
        variable = await create_variable(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            identity.subject,
            name=body.name,
            unit=body.unit,
            low=body.low,
            base=body.base,
            high=body.high,
            lang=request.state.locale,
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request) from error
    except ScenarioValidationError as error:
        raise _invalid(request) from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error
    return ScenarioVariableResponse.model_validate(variable)


@router.patch(
    "/{workspace_id}/decision-spaces/{space_id}/scenario-variables/{variable_id}",
    response_model=ScenarioVariableResponse,
    operation_id="update_scenario_variable",
)
async def update_scenario_variable(
    workspace_id: UUID,
    space_id: UUID,
    variable_id: UUID,
    body: ScenarioVariableWrite,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioVariableResponse:
    try:
        variable = await update_variable(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            variable_id,
            identity.subject,
            name=body.name,
            unit=body.unit,
            low=body.low,
            base=body.base,
            high=body.high,
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_variable") from error
    except ScenarioValidationError as error:
        raise _invalid(request) from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error
    return ScenarioVariableResponse.model_validate(variable)


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/scenario-variables/{variable_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_scenario_variable",
)
async def delete_scenario_variable(
    workspace_id: UUID,
    space_id: UUID,
    variable_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> None:
    try:
        await delete_variable(
            PostgresScenarios(session), workspace_id, space_id, variable_id, identity.subject
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_variable") from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/scenario-runs",
    response_model=ScenarioRunListResponse,
    operation_id="list_scenario_runs",
)
async def list_scenario_runs(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioRunListResponse:
    try:
        snapshots = await list_runs(
            PostgresScenarios(session), workspace_id, space_id, option_id, identity.subject
        )
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_option") from error
    return ScenarioRunListResponse(items=[_run_response(snapshot) for snapshot in snapshots])


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/scenario-runs",
    response_model=ScenarioRunResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_scenario_run",
)
async def create_scenario_run(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    body: ScenarioRunWrite,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioRunResponse:
    try:
        snapshot = await create_run(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            option_id,
            identity.subject,
            level=body.level,
            assumptions=body.assumptions,
            values=[(item.variable_id, item.value) for item in body.values],
            lang=request.state.locale,
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_option") from error
    except ScenarioValidationError as error:
        raise _invalid(request) from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error
    return _run_response(snapshot)


@router.patch(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/scenario-runs/{run_id}",
    response_model=ScenarioRunResponse,
    operation_id="update_scenario_run",
)
async def update_scenario_run(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    body: ScenarioRunWrite,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ScenarioRunResponse:
    try:
        snapshot = await update_run(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            identity.subject,
            level=body.level,
            assumptions=body.assumptions,
            values=[(item.variable_id, item.value) for item in body.values],
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_run") from error
    except ScenarioValidationError as error:
        raise _invalid(request) from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error
    return _run_response(snapshot)


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/scenario-runs/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_scenario_run",
)
async def delete_scenario_run(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> None:
    try:
        await delete_run(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            option_id,
            run_id,
            identity.subject,
        )
        await session.commit()
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_run") from error
    except ScenarioForbiddenError as error:
        raise _forbidden(request) from error


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/options/{option_id}/sensitivity",
    response_model=SensitivityResponse,
    operation_id="read_sensitivity",
)
async def read_option_sensitivity(
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    request: Request,
    metric_variable_id: Annotated[UUID, Query()],
    direction: Annotated[CriterionDirection, Query()],
    threshold: Annotated[Decimal, Query()],
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> SensitivityResponse:
    try:
        result = await read_sensitivity(
            PostgresScenarios(session),
            workspace_id,
            space_id,
            option_id,
            identity.subject,
            metric_variable_id=metric_variable_id,
            direction=direction,
            threshold=threshold,
        )
    except ScenarioNotFoundError as error:
        raise _not_found(request, "not_found_option") from error
    return SensitivityResponse(
        criterion=SensitivityCriterionResponse(
            metric_variable_id=metric_variable_id,
            direction=direction,
            threshold=threshold,
        ),
        ranked=[
            SensitivityVariableResponse(
                variable_id=entry.variable_id,
                status=entry.status,
                interval=entry.interval,
                crossing=entry.crossing,
                crossings=entry.crossings,
                slope_min=entry.slope_min,
                slope_max=entry.slope_max,
                travel=entry.travel,
            )
            for entry in result.report.ranked
        ],
        incomplete_run_ids=list(result.report.incomplete_run_ids),
        evidence=SensitivityEvidenceResponse(
            for_count=result.evidence_for, against_count=result.evidence_against
        ),
    )
