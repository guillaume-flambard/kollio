from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.platform.db import Base


class WorkspaceModelProvider(Base):
    __tablename__ = "workspace_model_providers"
    __table_args__ = (
        UniqueConstraint("workspace_id", "provider_key"),
        CheckConstraint("length(btrim(provider_name)) > 0"),
        CheckConstraint("length(btrim(region)) > 0"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    provider_key: Mapped[str] = mapped_column(String(80))
    provider_name: Mapped[str] = mapped_column(Text)
    region: Mapped[str] = mapped_column(String(120))
    retention_policy: Mapped[str] = mapped_column(Text)
    training_policy: Mapped[str] = mapped_column(Text)
    usage_mode: Mapped[str] = mapped_column(String(20), default="production")
    is_approved: Mapped[bool] = mapped_column(default=False)
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ModelTransmissionAudit(Base):
    __tablename__ = "model_transmission_audits"
    __table_args__ = (CheckConstraint("outcome IN ('allowed', 'refused', 'completed', 'failed')"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workspace_model_providers.id", ondelete="SET NULL")
    )
    model: Mapped[str] = mapped_column(String(200))
    excerpt_ids: Mapped[list[str]] = mapped_column(JSONB)
    workflow_id: Mapped[str] = mapped_column(String(200))
    outcome: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
