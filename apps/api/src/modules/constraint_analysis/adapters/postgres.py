from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.company_context.adapters.postgres import (
    CompanyConstraint,
    CompanyObjective,
    CompanyProfile,
)
from src.modules.constraint_analysis.domain.lifecycle import AnalysisStatus
from src.modules.ideas.adapters.postgres import Idea, User, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.db import Base


class AnalysisWorkflow(Base):
    __tablename__ = "analysis_workflows"
    __table_args__ = (
        CheckConstraint("locale IN ('fr', 'en')"),
        CheckConstraint(
            "status IN ('queued', 'running', 'awaiting_review', 'review_queued', "
            "'completed', 'rejected', 'failed')"
        ),
        UniqueConstraint("idea_id", "idempotency_key"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    source_iteration_id: Mapped[UUID | None] = mapped_column(ForeignKey("iterations.id"))
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    idempotency_key: Mapped[str] = mapped_column(String(200))
    locale: Mapped[str] = mapped_column(String(2))
    status: Mapped[str] = mapped_column(String(24))
    current_step: Mapped[str] = mapped_column(String(64))
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    draft_result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    review_decision: Mapped[bool | None] = mapped_column(Boolean)
    trace_context: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ConstraintAnalysis(Base):
    __tablename__ = "constraint_analyses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    workflow_id: Mapped[UUID] = mapped_column(
        ForeignKey("analysis_workflows.id", ondelete="CASCADE"), unique=True
    )
    idea_id: Mapped[UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), index=True)
    source_iteration_id: Mapped[UUID | None] = mapped_column(ForeignKey("iterations.id"))
    result: Mapped[dict[str, Any]] = mapped_column(JSONB)
    model: Mapped[str] = mapped_column(String(200))
    locale: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostgresAnalysisWorkflows:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def accessible_idea(self, idea_id: UUID, subject: str) -> tuple[Idea, User] | None:
        query = (
            select(Idea, User)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Idea.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(Idea.id == idea_id, User.auth_subject == subject)
        )
        row = (await self.session.execute(query)).one_or_none()
        return (row[0], row[1]) if row is not None else None

    async def main_head(self, idea_id: UUID) -> Iteration | None:
        return cast(
            Iteration | None,
            await self.session.scalar(
                select(Iteration)
                .where(Iteration.idea_id == idea_id, Iteration.branch == "main")
                .order_by(Iteration.revision.desc())
                .limit(1)
            ),
        )

    async def find_launch(self, idea_id: UUID, idempotency_key: str) -> AnalysisWorkflow | None:
        return cast(
            AnalysisWorkflow | None,
            await self.session.scalar(
                select(AnalysisWorkflow).where(
                    AnalysisWorkflow.idea_id == idea_id,
                    AnalysisWorkflow.idempotency_key == idempotency_key,
                )
            ),
        )

    async def memberships(self, subject: str) -> frozenset[UUID]:
        """The workspaces the viewer may read, for scoped retrieval."""
        query = (
            select(WorkspaceMembership.workspace_id).join(User).where(User.auth_subject == subject)
        )
        return frozenset((await self.session.scalars(query)).all())

    async def active_company_context(self, workspace_id: UUID) -> dict[str, Any]:
        """The active objectives and constraints the analysis may contradict."""
        profile = await self.session.get(CompanyProfile, workspace_id)
        objectives = await self.session.scalars(
            select(CompanyObjective)
            .where(
                CompanyObjective.workspace_id == workspace_id,
                CompanyObjective.state == "active",
            )
            .order_by(CompanyObjective.priority.desc(), CompanyObjective.created_at)
        )
        constraints = await self.session.scalars(
            select(CompanyConstraint)
            .where(
                CompanyConstraint.workspace_id == workspace_id,
                CompanyConstraint.state == "active",
            )
            .order_by(CompanyConstraint.created_at)
        )
        return {
            "profile": (
                {
                    "name": profile.name,
                    "description": profile.description,
                    "business_model": profile.business_model,
                    "customer_segments": profile.customer_segments,
                    "markets": profile.markets,
                    "lang": profile.lang,
                }
                if profile is not None
                else None
            ),
            "objectives": [
                {
                    "id": f"objective:{item.id}",
                    "title": item.title,
                    "priority": item.priority,
                    "lang": item.lang,
                }
                for item in objectives
            ],
            "constraints": [
                {
                    "id": f"constraint:{item.id}",
                    "title": item.title,
                    "detail": item.detail,
                    "lang": item.lang,
                }
                for item in constraints
            ],
        }

    async def add(self, workflow: AnalysisWorkflow) -> AnalysisWorkflow:
        self.session.add(workflow)
        return workflow

    async def accessible_workflow(
        self, idea_id: UUID, workflow_id: UUID, subject: str, *, lock: bool = False
    ) -> tuple[AnalysisWorkflow, Idea, User] | None:
        query = (
            select(AnalysisWorkflow, Idea, User)
            .join(Idea, Idea.id == AnalysisWorkflow.idea_id)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Idea.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(
                AnalysisWorkflow.id == workflow_id,
                AnalysisWorkflow.idea_id == idea_id,
                User.auth_subject == subject,
            )
        )
        if lock:
            query = query.with_for_update(of=AnalysisWorkflow)
        row = (await self.session.execute(query)).one_or_none()
        return (row[0], row[1], row[2]) if row is not None else None

    async def get_for_worker(
        self, workflow_id: UUID, *, lock: bool = False
    ) -> AnalysisWorkflow | None:
        query = select(AnalysisWorkflow).where(AnalysisWorkflow.id == workflow_id)
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return cast(AnalysisWorkflow | None, await self.session.scalar(query))

    async def final_result(self, workflow_id: UUID) -> ConstraintAnalysis | None:
        return cast(
            ConstraintAnalysis | None,
            await self.session.scalar(
                select(ConstraintAnalysis).where(ConstraintAnalysis.workflow_id == workflow_id)
            ),
        )

    async def store_final(self, analysis: ConstraintAnalysis) -> ConstraintAnalysis:
        existing = await self.final_result(analysis.workflow_id)
        if existing is not None:
            return existing
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    @staticmethod
    def set_status(
        workflow: AnalysisWorkflow,
        status: AnalysisStatus,
        *,
        step: str,
        finished_at: datetime | None = None,
    ) -> None:
        workflow.status = status.value
        workflow.current_step = step
        workflow.finished_at = finished_at
