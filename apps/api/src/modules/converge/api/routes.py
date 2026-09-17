from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.converge.adapters.postgres import PostgresConverge
from src.modules.converge.api.schemas import (
    ClusterCreate,
    ClusterMemberAdd,
    ClusterResponse,
    MapContributionResponse,
    MapResponse,
    RelationCreate,
    RelationResponse,
)
from src.modules.converge.service.converge import (
    MapForbiddenError,
    MapNotFoundError,
    MapValidationError,
    assign_member,
    create_cluster,
    create_relation,
    delete_cluster,
    delete_relation,
    read_map,
    unassign_member,
)
from src.platform.auth import Identity, current_identity
from src.platform.db import get_session
from src.platform.locale import MESSAGES

router = APIRouter(prefix="/workspaces", tags=["converge-map"])


def _not_found(request: Request, key: str = "not_found_space") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, MESSAGES[request.state.locale][key])


def _invalid(request: Request) -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT, MESSAGES[request.state.locale]["invalid"]
    )


def _forbidden(request: Request) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, MESSAGES[request.state.locale]["forbidden"])


@router.get(
    "/{workspace_id}/decision-spaces/{space_id}/converge/map",
    response_model=MapResponse,
    operation_id="get_converge_map",
)
async def read_converge_map(
    workspace_id: UUID,
    space_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> MapResponse:
    try:
        snapshot = await read_map(
            PostgresConverge(session), workspace_id, space_id, identity.subject
        )
    except MapNotFoundError as error:
        raise _not_found(request) from error
    return MapResponse(
        contributions=[
            MapContributionResponse.model_validate(contribution)
            for contribution in snapshot.contributions
        ],
        relations=[RelationResponse.model_validate(relation) for relation in snapshot.relations],
        clusters=[_cluster_view(cluster, snapshot.contributions) for cluster in snapshot.clusters],
    )


def _cluster_view(cluster, contributions) -> ClusterResponse:
    return ClusterResponse(
        id=cluster.id,
        space_id=cluster.space_id,
        title=cluster.title,
        created_by=cluster.created_by,
        created_at=cluster.created_at,
        member_ids=[
            contribution.id
            for contribution in contributions
            if contribution.cluster_id == cluster.id
        ],
    )


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/relations",
    response_model=RelationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_relation",
)
async def create_space_relation(
    workspace_id: UUID,
    space_id: UUID,
    body: RelationCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> RelationResponse:
    try:
        relation = await create_relation(
            PostgresConverge(session),
            workspace_id,
            space_id,
            identity.subject,
            from_contribution_id=body.from_contribution_id,
            to_contribution_id=body.to_contribution_id,
            relation_type=body.relation_type,
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request) from error
    except MapValidationError as error:
        raise _invalid(request) from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error
    return RelationResponse.model_validate(relation)


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/relations/{relation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_relation",
)
async def delete_space_relation(
    workspace_id: UUID,
    space_id: UUID,
    relation_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> None:
    try:
        await delete_relation(
            PostgresConverge(session), workspace_id, space_id, relation_id, identity.subject
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request, "not_found_relation") from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/clusters",
    response_model=ClusterResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_cluster",
)
async def create_space_cluster(
    workspace_id: UUID,
    space_id: UUID,
    body: ClusterCreate,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ClusterResponse:
    try:
        cluster = await create_cluster(
            PostgresConverge(session),
            workspace_id,
            space_id,
            identity.subject,
            title=body.title,
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request) from error
    except MapValidationError as error:
        raise _invalid(request) from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error
    return ClusterResponse(
        id=cluster.id,
        space_id=cluster.space_id,
        title=cluster.title,
        created_by=cluster.created_by,
        created_at=cluster.created_at,
        member_ids=[],
    )


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/clusters/{cluster_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_cluster",
)
async def delete_space_cluster(
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> None:
    try:
        await delete_cluster(
            PostgresConverge(session), workspace_id, space_id, cluster_id, identity.subject
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request, "not_found_cluster") from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error


async def _cluster_with_members(
    repository: PostgresConverge, workspace_id: UUID, space_id: UUID, cluster_id: UUID, subject: str
) -> ClusterResponse:
    snapshot = await read_map(repository, workspace_id, space_id, subject)
    cluster = next(c for c in snapshot.clusters if c.id == cluster_id)
    return _cluster_view(cluster, snapshot.contributions)


@router.post(
    "/{workspace_id}/decision-spaces/{space_id}/clusters/{cluster_id}/members",
    response_model=ClusterResponse,
    operation_id="add_cluster_member",
)
async def add_member_to_cluster(
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    body: ClusterMemberAdd,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ClusterResponse:
    repository = PostgresConverge(session)
    try:
        await assign_member(
            repository,
            workspace_id,
            space_id,
            cluster_id,
            identity.subject,
            contribution_id=body.contribution_id,
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request, "not_found_cluster") from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error
    return await _cluster_with_members(
        repository, workspace_id, space_id, cluster_id, identity.subject
    )


@router.delete(
    "/{workspace_id}/decision-spaces/{space_id}/clusters/{cluster_id}/members/{contribution_id}",
    response_model=ClusterResponse,
    operation_id="remove_cluster_member",
)
async def remove_member_from_cluster(
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    contribution_id: UUID,
    request: Request,
    identity: Identity = Depends(current_identity),
    session: AsyncSession = Depends(get_session),
) -> ClusterResponse:
    repository = PostgresConverge(session)
    try:
        await unassign_member(
            repository,
            workspace_id,
            space_id,
            cluster_id,
            identity.subject,
            contribution_id=contribution_id,
        )
        await session.commit()
    except MapNotFoundError as error:
        raise _not_found(request, "not_found_cluster") from error
    except MapForbiddenError as error:
        raise _forbidden(request) from error
    return await _cluster_with_members(
        repository, workspace_id, space_id, cluster_id, identity.subject
    )
