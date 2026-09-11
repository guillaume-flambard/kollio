from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
from pgvector.sqlalchemy import Vector
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func, select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.platform.config import Settings
from src.platform.db import Base


class IdeaEmbedding(Base):
    __tablename__ = "idea_embeddings"
    __table_args__ = (
        CheckConstraint("source_language IN ('fr', 'en')"),
        CheckConstraint("dimensions = vector_dims(vector)"),
    )
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id"), primary_key=True)
    model: Mapped[str] = mapped_column(primary_key=True)
    dimensions: Mapped[int] = mapped_column(Integer, primary_key=True)
    vector = mapped_column(Vector(), nullable=False)
    source_language: Mapped[str]
    source_identifier: Mapped[str] = mapped_column(String, nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@dataclass(frozen=True)
class EmbeddingRecord:
    idea_id: UUID
    text: str
    source_language: str
    source_identifier: str
    provenance: dict[str, Any]


def validate_vectors(
    vectors: list[list[float]], expected_count: int, expected_dimensions: int
) -> None:
    if len(vectors) != expected_count:
        raise ValueError("Embedding count or index mismatch")
    if any(len(vector) != expected_dimensions for vector in vectors):
        raise ValueError("Embedding dimension mismatch")


async def embed(texts: list[str], settings: Settings) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            settings.llm_base_url + "/embeddings",
            json={
                "model": settings.embedding_model,
                "input": texts,
                "dimensions": settings.embedding_dimensions,
            },
            headers={"Authorization": "Bearer " + settings.llm_api_key.get_secret_value()},
        )
        response.raise_for_status()
    payload = response.json()
    data = payload.get("data")
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ValueError("Embedding response data is invalid")
    data = sorted(data, key=lambda item: item.get("index", -1))
    if [item.get("index") for item in data] != list(range(len(texts))):
        raise ValueError("Embedding count or index mismatch")
    vectors = [item.get("embedding") for item in data]
    if any(
        not isinstance(vector, list) or any(not isinstance(value, int | float) for value in vector)
        for vector in vectors
    ):
        raise ValueError("Embedding vector is invalid")
    validate_vectors(vectors, len(texts), settings.embedding_dimensions)
    return vectors


async def store_embeddings(
    session: AsyncSession,
    records: list[EmbeddingRecord],
    vectors: list[list[float]],
    settings: Settings,
) -> None:
    validate_vectors(vectors, len(records), settings.embedding_dimensions)
    for record, vector in zip(records, vectors, strict=True):
        if record.source_language not in {"fr", "en"}:
            raise ValueError("Embedding language is unsupported")
        await session.execute(
            insert(IdeaEmbedding)
            .values(
                idea_id=record.idea_id,
                model=settings.embedding_source_model,
                dimensions=settings.embedding_dimensions,
                vector=vector,
                source_language=record.source_language,
                source_identifier=record.source_identifier,
                provenance=record.provenance,
            )
            .on_conflict_do_update(
                index_elements=[
                    IdeaEmbedding.idea_id,
                    IdeaEmbedding.model,
                    IdeaEmbedding.dimensions,
                ],
                set_={
                    "vector": vector,
                    "source_language": record.source_language,
                    "source_identifier": record.source_identifier,
                    "provenance": record.provenance,
                    "updated_at": func.now(),
                },
            )
        )


async def similar_idea_ids(
    session: AsyncSession,
    query_vector: list[float],
    settings: Settings,
    limit: int = 10,
) -> list[UUID]:
    validate_vectors([query_vector], 1, settings.embedding_dimensions)
    distance = IdeaEmbedding.vector.cosine_distance(query_vector)
    query = (
        select(IdeaEmbedding.idea_id)
        .where(
            IdeaEmbedding.model == settings.embedding_source_model,
            IdeaEmbedding.dimensions == settings.embedding_dimensions,
            func.vector_dims(IdeaEmbedding.vector) == settings.embedding_dimensions,
        )
        .order_by(distance)
        .limit(limit)
    )
    return list((await session.scalars(query)).all())
