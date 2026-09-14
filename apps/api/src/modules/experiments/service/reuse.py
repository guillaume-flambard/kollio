"""Reuse of confirmed learnings.

A confirmed learning is embedded with the same model and dimensions as
an idea, its provenance carrying the workspace, the idea and the
experiment. At analysis launch the nearest learnings of the viewer's
workspaces enter the input as evidence entries.

Both hooks are best effort: a missing embedding provider degrades the
analysis to the evidence the caller supplied instead of failing the run,
and the snapshot records why nothing was reused.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.platform.config import Settings
from src.platform.embeddings import (
    LearningEmbeddingRecord,
    embed,
    similar_learning_ids,
    store_learning_embeddings,
)

logger = logging.getLogger(__name__)


async def embed_confirmed_learning(
    session: AsyncSession,
    *,
    learning_id: UUID,
    text: str,
    language: str,
    workspace_id: UUID,
    idea_id: UUID,
    experiment_id: UUID,
    settings: Settings,
) -> bool:
    """Embed one confirmed learning; returns whether the vector was stored."""
    try:
        vectors = await embed([text], settings)
        await store_learning_embeddings(
            session,
            [
                LearningEmbeddingRecord(
                    learning_id=learning_id,
                    text=text,
                    source_language=language if language in {"fr", "en"} else "en",
                    source_identifier="learning.confirmed",
                    provenance={
                        "workspace_id": str(workspace_id),
                        "idea_id": str(idea_id),
                        "experiment_id": str(experiment_id),
                    },
                )
            ],
            vectors,
            settings,
        )
    except Exception:
        logger.warning("learning embedding skipped", exc_info=True)
        return False
    return True


async def reusable_learning_ids(
    session: AsyncSession,
    *,
    text: str,
    workspace_ids: frozenset[UUID],
    settings: Settings,
    limit: int = 3,
) -> list[UUID]:
    """The nearest confirmed learnings the viewer's workspaces may read."""
    if not workspace_ids or not text.strip():
        return []
    try:
        vectors = await embed([text], settings)
        return await similar_learning_ids(
            session, vectors[0], settings, workspace_ids=workspace_ids, limit=limit
        )
    except Exception:
        logger.warning("learning retrieval skipped", exc_info=True)
        return []


async def learning_texts(session: AsyncSession, learning_ids: list[UUID]) -> list[tuple[UUID, str]]:
    """The text of the given learnings, in the order requested."""
    if not learning_ids:
        return []
    from src.modules.experiments.adapters.postgres import Learning

    rows = (
        await session.execute(
            select(Learning.id, Learning.text).where(Learning.id.in_(learning_ids))
        )
    ).all()
    found = {row[0]: row[1] for row in rows}
    return [
        (learning_id, found[learning_id]) for learning_id in learning_ids if learning_id in found
    ]
