from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.inbox.adapters.postgres import PostgresInbox
from src.modules.inbox.api.schemas import (
    DecisionInboxResponse,
    InboxEntryResponse,
    InboxSectionResponse,
)
from src.modules.inbox.service.inbox import (
    MAX_LIMIT,
    InboxNotFoundError,
    InboxValidationError,
    read_inbox,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(tags=["decision-inbox"])


@router.get(
    "/inbox",
    response_model=DecisionInboxResponse,
    operation_id="read_decision_inbox",
)
async def read_decision_inbox(
    request: Request,
    limit: int | None = Query(default=None, ge=1, le=MAX_LIMIT),
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> DecisionInboxResponse:
    try:
        snapshot = await read_inbox(PostgresInbox(session), identity.subject, limit=limit)
    except InboxNotFoundError as error:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale]["not_found_account"]
        ) from error
    except InboxValidationError as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
        ) from error

    def section(values) -> InboxSectionResponse:
        return InboxSectionResponse(
            entries=[InboxEntryResponse.model_validate(entry) for entry in values.entries],
            total=values.total,
        )

    return DecisionInboxResponse(
        needs_convergence=section(snapshot.needs_convergence),
        needs_my_input=section(snapshot.needs_my_input),
        ready_to_decide=section(snapshot.ready_to_decide),
        needs_learning=section(snapshot.needs_learning),
    )
