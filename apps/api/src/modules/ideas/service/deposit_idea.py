import re
from uuid import UUID, uuid4

from src.modules.ideas.adapters.postgres import Idea, PostgresIdeas
from src.modules.ideas.domain.initiative import validate_initiative_type
from src.modules.ideas.domain.permissions import can_read_idea


class DepositNotFoundError(LookupError):
    """Raised when the workspace is missing or closed to the depositor."""


class IdeaNotFoundError(LookupError):
    """Raised when an idea does not exist inside the requester's workspaces."""


class IdeaUpdateForbiddenError(LookupError):
    """Raised when the requester may not edit the idea."""


def _slugify(title: str, identifier: UUID) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:160] or "idea"
    return f"{stem}-{identifier.hex[:8]}"


async def deposit_idea(
    ideas: PostgresIdeas,
    workspace_id: UUID,
    subject: str,
    *,
    title: str,
    pitch: str,
    lang: str,
    initiative_type: str = "idea",
) -> Idea:
    validate_initiative_type(initiative_type)
    if not can_read_idea(workspace_id, await ideas.memberships(subject)):
        raise DepositNotFoundError
    actor = await ideas.user_by_subject(subject)
    if actor is None:
        raise DepositNotFoundError
    identifier = uuid4()
    idea = Idea(
        id=identifier,
        slug=_slugify(title, identifier),
        title=title,
        pitch=pitch,
        owner_id=actor.id,
        workspace_id=workspace_id,
        stage="seed",
        initiative_type=initiative_type,
        lang=lang,
        visibility="workspace",
    )
    ideas.add_idea(idea)
    return idea


async def update_initiative_type(
    ideas: PostgresIdeas, idea_id: UUID, subject: str, initiative_type: str
) -> Idea:
    validate_initiative_type(initiative_type)
    idea = await ideas.get(idea_id)
    if idea is None or not can_read_idea(idea.workspace_id, await ideas.memberships(subject)):
        raise IdeaNotFoundError
    actor = await ideas.user_by_subject(subject)
    if actor is None or idea.owner_id != actor.id:
        raise IdeaUpdateForbiddenError
    idea.initiative_type = initiative_type
    await ideas.session.flush()
    return idea
