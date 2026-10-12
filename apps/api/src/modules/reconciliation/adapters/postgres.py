from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
VISIBILITY_CHECK = "visibility IN ('private', 'shared')"
NON_BLANK_TITLE_CHECK = "length(btrim(title)) > 0"
NON_BLANK_AUTHOR_CHECK = "length(btrim(stated_author)) > 0"
NON_BLANK_ORIGIN_CHECK = "length(btrim(origin_label)) > 0"
NON_BLANK_BODY_CHECK = "length(btrim(body)) > 0"
EXCERPT_OFFSETS_CHECK = (
    "(start_offset IS NULL AND end_offset IS NULL) OR "
    "(start_offset IS NOT NULL AND end_offset IS NOT NULL AND "
    "start_offset >= 0 AND end_offset > start_offset)"
)
RESOLUTION_OUTCOME_CHECK = (
    "outcome IN ('prefer_left', 'prefer_right', 'combine', 'cannot_combine', 'unresolved')"
)
DISTINCT_EXCERPTS_CHECK = "left_excerpt_id <> right_excerpt_id"
NON_BLANK_RATIONALE_CHECK = "length(btrim(rationale)) > 0"


class SourceMaterial(Base):
    __tablename__ = "source_materials"
    __table_args__ = (
        CheckConstraint(NON_BLANK_TITLE_CHECK, name="source_materials_title_not_blank"),
        CheckConstraint(NON_BLANK_AUTHOR_CHECK, name="source_materials_author_not_blank"),
        CheckConstraint(NON_BLANK_ORIGIN_CHECK, name="source_materials_origin_not_blank"),
        CheckConstraint(VISIBILITY_CHECK, name="source_materials_visibility_check"),
        CheckConstraint(LANG_CHECK, name="source_materials_lang_check"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(Text)
    stated_author: Mapped[str] = mapped_column(Text)
    origin_label: Mapped[str] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(10))
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceRevision(Base):
    __tablename__ = "source_revisions"
    __table_args__ = (
        UniqueConstraint("material_id", "sequence", name="source_revisions_material_sequence_key"),
        CheckConstraint(NON_BLANK_BODY_CHECK, name="source_revisions_body_not_blank"),
        CheckConstraint(LANG_CHECK, name="source_revisions_lang_check"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    material_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_materials.id", ondelete="CASCADE"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceExcerpt(Base):
    __tablename__ = "source_excerpts"
    __table_args__ = (
        CheckConstraint(NON_BLANK_BODY_CHECK, name="source_excerpts_body_not_blank"),
        CheckConstraint(EXCERPT_OFFSETS_CHECK, name="source_excerpts_offsets_check"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_revisions.id", ondelete="CASCADE"), index=True
    )
    body: Mapped[str] = mapped_column(Text)
    start_offset: Mapped[int | None] = mapped_column(Integer)
    end_offset: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReconciliationResolution(Base):
    __tablename__ = "reconciliation_resolutions"
    __table_args__ = (
        CheckConstraint(RESOLUTION_OUTCOME_CHECK, name="reconciliation_resolutions_outcome_check"),
        CheckConstraint(
            DISTINCT_EXCERPTS_CHECK, name="reconciliation_resolutions_distinct_excerpts"
        ),
        CheckConstraint(
            NON_BLANK_RATIONALE_CHECK, name="reconciliation_resolutions_rationale_not_blank"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    left_excerpt_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_excerpts.id", ondelete="CASCADE"), index=True
    )
    right_excerpt_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_excerpts.id", ondelete="CASCADE"), index=True
    )
    outcome: Mapped[str] = mapped_column(String(20))
    rationale: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresReconciliation:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_material(
        self,
        *,
        space_id: UUID,
        title: str,
        stated_author: str,
        origin_label: str,
        visibility: str,
        created_by: UUID,
        lang: str,
    ) -> SourceMaterial:
        material = SourceMaterial(
            space_id=space_id,
            title=title,
            stated_author=stated_author,
            origin_label=origin_label,
            visibility=visibility,
            created_by=created_by,
            lang=lang,
        )
        self.session.add(material)
        await self.session.flush()
        return material

    async def material(self, space_id: UUID, material_id: UUID) -> SourceMaterial | None:
        return await self.session.scalar(
            select(SourceMaterial).where(
                SourceMaterial.id == material_id,
                SourceMaterial.space_id == space_id,
            )
        )

    async def append_revision(
        self, *, material_id: UUID, body: str, created_by: UUID, lang: str
    ) -> SourceRevision:
        await self.session.scalar(
            select(SourceMaterial).where(SourceMaterial.id == material_id).with_for_update()
        )
        sequence = await self.session.scalar(
            select(func.coalesce(func.max(SourceRevision.sequence), 0) + 1).where(
                SourceRevision.material_id == material_id
            )
        )
        revision = SourceRevision(
            material_id=material_id,
            sequence=sequence,
            body=body,
            created_by=created_by,
            lang=lang,
        )
        self.session.add(revision)
        await self.session.flush()
        return revision

    async def list_revisions(self, space_id: UUID, material_id: UUID) -> list[SourceRevision]:
        rows = await self.session.execute(
            select(SourceRevision)
            .join(SourceMaterial, SourceMaterial.id == SourceRevision.material_id)
            .where(
                SourceMaterial.space_id == space_id,
                SourceRevision.material_id == material_id,
            )
            .order_by(SourceRevision.sequence)
        )
        return list(rows.scalars().all())

    async def create_excerpt(
        self,
        *,
        revision_id: UUID,
        body: str,
        start_offset: int | None,
        end_offset: int | None,
        created_by: UUID,
    ) -> SourceExcerpt:
        excerpt = SourceExcerpt(
            revision_id=revision_id,
            body=body,
            start_offset=start_offset,
            end_offset=end_offset,
            created_by=created_by,
        )
        self.session.add(excerpt)
        await self.session.flush()
        return excerpt

    async def excerpt(self, space_id: UUID, excerpt_id: UUID) -> SourceExcerpt | None:
        return await self.session.scalar(
            select(SourceExcerpt)
            .join(SourceRevision, SourceRevision.id == SourceExcerpt.revision_id)
            .join(SourceMaterial, SourceMaterial.id == SourceRevision.material_id)
            .where(SourceExcerpt.id == excerpt_id, SourceMaterial.space_id == space_id)
        )

    async def append_resolution(
        self,
        *,
        space_id: UUID,
        left_excerpt_id: UUID,
        right_excerpt_id: UUID,
        outcome: str,
        rationale: str,
        created_by: UUID,
    ) -> ReconciliationResolution:
        left_excerpt = await self.excerpt(space_id, left_excerpt_id)
        right_excerpt = await self.excerpt(space_id, right_excerpt_id)
        if left_excerpt is None or right_excerpt is None:
            raise ValueError("Both excerpts must belong to the decision space")
        resolution = ReconciliationResolution(
            space_id=space_id,
            left_excerpt_id=left_excerpt_id,
            right_excerpt_id=right_excerpt_id,
            outcome=outcome,
            rationale=rationale,
            created_by=created_by,
        )
        self.session.add(resolution)
        await self.session.flush()
        return resolution

    async def list_resolutions(self, space_id: UUID) -> list[ReconciliationResolution]:
        rows = await self.session.execute(
            select(ReconciliationResolution)
            .where(ReconciliationResolution.space_id == space_id)
            .order_by(ReconciliationResolution.created_at, ReconciliationResolution.id)
        )
        return list(rows.scalars().all())
