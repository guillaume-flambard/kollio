from uuid import UUID

from src.modules.profiles.adapters.postgres import PostgresProfiles, ProfileRecord
from src.modules.profiles.domain.visibility import can_read_profile


class ProfileNotFoundError(LookupError):
    """Raised when no profile is visible to the viewer."""


async def get_profile(repository: PostgresProfiles, user_id: UUID, subject: str) -> ProfileRecord:
    person = await repository.user(user_id)
    if person is None:
        raise ProfileNotFoundError
    viewer_workspaces = await repository.workspace_ids_for_subject(subject)
    person_workspaces = await repository.workspace_ids(person.id)
    if not can_read_profile(person_workspaces, viewer_workspaces):
        raise ProfileNotFoundError
    shared = person_workspaces & viewer_workspaces
    return ProfileRecord(
        user=person,
        owned_ideas=await repository.owned_ideas(person.id, shared),
        memberships=await repository.memberships(person.id, shared),
        contributions=await repository.contributions(person.id, shared),
    )
