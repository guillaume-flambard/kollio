from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.decision_spaces.adapters.postgres import PostgresDecisionSpaces
from src.modules.decisions.adapters.postgres import PostgresDecisions
from src.modules.decisions.api.schemas import (
    DecisionArgumentResponse,
    DecisionCommit,
    DecisionListResponse,
    DecisionResponse,
)
from src.modules.decisions.service.records import (
    DecisionForbiddenError,
    DecisionNotFoundError,
    DecisionSpaceNotFoundError,
    DecisionValidationError,
    RecordSnapshot,
    commit_decision,
    list_versions,
    read_current_record,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["decisions"])


def _space_not_found(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_space"]
    )


def _record_not_found(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_decision"]
    )


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


def _render(snapshot: RecordSnapshot) -> DecisionResponse:
    decision = snapshot.decision
    return DecisionResponse(
        id=decision.id,
        space_id=decision.space_id,
        version=decision.version,
        selected_option_id=decision.selected_option_id,
        rationale=decision.rationale,
        critical_assumptions=decision.critical_assumptions,
        uncertainty=decision.uncertainty,
        success_criteria=decision.success_criteria,
        revisit_triggers=decision.revisit_triggers,
        reviewer_ids=decision.reviewer_ids,
        decided_by=decision.decided_by,
        lang=decision.lang,
        created_at=decision.created_at,
        rejected_option_ids=snapshot.alternatives,
        arguments=[
            DecisionArgumentResponse.model_validate(argument) for argument in snapshot.arguments
        ],
    )


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/decision",
    response_model=DecisionResponse,
    operation_id="get_decision_record",
)
async def read_decision_record(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionResponse:
    try:
        snapshot = await read_current_record(
            PostgresDecisions(session), workspace_id, space_id, identity.subject
        )
    except DecisionSpaceNotFoundError as error:
        raise _space_not_found(request) from error
    except DecisionNotFoundError as error:
        raise _record_not_found(request) from error
    return _render(snapshot)


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/decision/versions",
    response_model=DecisionListResponse,
    operation_id="list_decision_versions",
)
async def list_decision_versions(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionListResponse:
    try:
        snapshots = await list_versions(
            PostgresDecisions(session), workspace_id, space_id, identity.subject
        )
    except DecisionSpaceNotFoundError as error:
        raise _space_not_found(request) from error
    return DecisionListResponse(items=[_render(snapshot) for snapshot in snapshots])


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/decision",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="commit_decision",
)
async def commit_decision_record(
    workspace_id: UUID,
    space_id: UUID,
    body: DecisionCommit,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionResponse:
    try:
        snapshot = await commit_decision(
            PostgresDecisionSpaces(session),
            PostgresDecisions(session),
            workspace_id,
            space_id,
            identity.subject,
            selected_option_id=body.selected_option_id,
            rationale=body.rationale,
            critical_assumptions=body.critical_assumptions,
            uncertainty=body.uncertainty,
            success_criteria=body.success_criteria,
            revisit_triggers=(
                [trigger.model_dump() for trigger in body.revisit_triggers]
                if body.revisit_triggers is not None
                else None
            ),
            rejected_option_ids=body.rejected_option_ids,
            arguments=[(argument.contribution_id, argument.side) for argument in body.arguments],
            lang=request.state.locale,
        )
        await session.commit()
    except DecisionSpaceNotFoundError as error:
        raise _space_not_found(request) from error
    except DecisionForbiddenError as error:
        raise _forbidden(request) from error
    except DecisionValidationError as error:
        raise _invalid(request) from error
    return _render(snapshot)
