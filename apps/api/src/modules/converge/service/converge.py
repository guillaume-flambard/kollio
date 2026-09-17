from dataclasses import dataclass
from uuid import UUID

from src.modules.branches.adapters.postgres import Contribution
from src.modules.converge.adapters.postgres import (
    Cluster,
    ContributionRelation,
    PostgresConverge,
)
from src.modules.converge.domain.access import can_read_map, can_write_map
from src.modules.converge.domain.clusters import ClusterTitleError, validate_cluster_title
from src.modules.converge.domain.relations import (
    RelationLinkError,
    RelationTypeError,
    validate_relation_ends,
    validate_relation_type,
)
from src.modules.decision_spaces.adapters.postgres import DecisionSpace


class MapNotFoundError(LookupError):
    """Raised when the workspace, space, relation, cluster or member is not visible."""


class MapValidationError(ValueError):
    """Raised when a request breaks a map rule."""


class MapForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


@dataclass(frozen=True)
class MapSnapshot:
    contributions: list[Contribution]
    relations: list[ContributionRelation]
    clusters: list[Cluster]


async def _authorize_read(repository: PostgresConverge, workspace_id: UUID, subject: str) -> None:
    if not can_read_map(workspace_id, await repository.memberships(subject)):
        raise MapNotFoundError


async def _actor(repository: PostgresConverge, subject: str) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise MapNotFoundError
    return user.id


async def _space(repository: PostgresConverge, workspace_id: UUID, space_id: UUID) -> DecisionSpace:
    space = await repository.space(space_id)
    if space is None or space.workspace_id != workspace_id:
        raise MapNotFoundError
    return space


async def _authorize_write(
    repository: PostgresConverge, space: DecisionSpace, actor_id: UUID
) -> None:
    if not can_write_map(space.owner_id, await repository.participant_ids(space.id), actor_id):
        raise MapForbiddenError


async def read_map(
    repository: PostgresConverge, workspace_id: UUID, space_id: UUID, subject: str
) -> MapSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    return MapSnapshot(
        contributions=await repository.confirmed_contributions(space_id),
        relations=await repository.list_relations(space_id),
        clusters=await repository.list_clusters(space_id),
    )


async def create_relation(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    from_contribution_id: UUID,
    to_contribution_id: UUID,
    relation_type: str,
) -> ContributionRelation:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    await _authorize_write(repository, space, actor_id)
    try:
        validate_relation_type(relation_type)
        validate_relation_ends(str(from_contribution_id), str(to_contribution_id))
    except (RelationTypeError, RelationLinkError) as error:
        raise MapValidationError(str(error)) from error
    if await repository.contribution(space_id, from_contribution_id) is None:
        raise MapNotFoundError
    if await repository.contribution(space_id, to_contribution_id) is None:
        raise MapNotFoundError
    if (
        await repository.relation_between(space_id, from_contribution_id, to_contribution_id)
        is not None
    ):
        raise MapValidationError("This directed pair already carries a relation")
    return await repository.create_relation(
        space_id=space.id,
        from_contribution_id=from_contribution_id,
        to_contribution_id=to_contribution_id,
        relation_type=relation_type,
        created_by=actor_id,
    )


async def delete_relation(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    relation_id: UUID,
    subject: str,
) -> None:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    relation = await repository.relation(space_id, relation_id)
    if relation is None:
        raise MapNotFoundError
    await _authorize_write(repository, space, await _actor(repository, subject))
    await repository.delete_relation(relation)


async def create_cluster(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    subject: str,
    *,
    title: str,
) -> Cluster:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    actor_id = await _actor(repository, subject)
    await _authorize_write(repository, space, actor_id)
    try:
        cleaned = validate_cluster_title(title)
    except ClusterTitleError as error:
        raise MapValidationError(str(error)) from error
    return await repository.create_cluster(space_id=space.id, title=cleaned, created_by=actor_id)


async def delete_cluster(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    subject: str,
) -> None:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    cluster = await repository.cluster(space_id, cluster_id)
    if cluster is None:
        raise MapNotFoundError
    await _authorize_write(repository, space, await _actor(repository, subject))
    await repository.delete_cluster(cluster)


async def assign_member(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    subject: str,
    *,
    contribution_id: UUID,
) -> Contribution:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    cluster = await repository.cluster(space_id, cluster_id)
    if cluster is None:
        raise MapNotFoundError
    contribution = await repository.contribution(space_id, contribution_id)
    if contribution is None:
        raise MapNotFoundError
    await _authorize_write(repository, space, await _actor(repository, subject))
    return await repository.assign_member(contribution, cluster.id)


async def unassign_member(
    repository: PostgresConverge,
    workspace_id: UUID,
    space_id: UUID,
    cluster_id: UUID,
    subject: str,
    *,
    contribution_id: UUID,
) -> Contribution:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    cluster = await repository.cluster(space_id, cluster_id)
    if cluster is None:
        raise MapNotFoundError
    contribution = await repository.contribution(space_id, contribution_id)
    if contribution is None or contribution.cluster_id != cluster.id:
        raise MapNotFoundError
    await _authorize_write(repository, space, await _actor(repository, subject))
    return await repository.unassign_member(contribution)
