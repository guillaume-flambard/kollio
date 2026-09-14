from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.constraint_analysis.adapters.postgres import (
    AnalysisWorkflow,
    ConstraintAnalysis,
)
from src.modules.iterations.adapters.postgres import Iteration

DISPLAY_STATES = Literal["resolved", "abstained", "running", "unavailable"]

OPEN_STATUSES = frozenset({"queued", "running", "awaiting_review", "review_queued"})


@dataclass(frozen=True)
class AnalysisDisplay:
    state: str
    iteration_id: UUID | None
    realism_score: int | None
    constraints: dict[str, dict[str, Any]]
    contradictions: list[dict[str, Any]]
    locale: str | None
    model: str | None
    created_at: Any | None


def display_from(workflow: AnalysisWorkflow | None, final: ConstraintAnalysis | None):
    if final is None:
        if workflow is not None and workflow.status in OPEN_STATUSES:
            return AnalysisDisplay(
                "running", workflow.source_iteration_id, None, {}, [], None, None, None
            )
        return AnalysisDisplay("unavailable", None, None, {}, [], None, None, None)
    result = final.result
    state = "abstained" if result.get("verdict") == "unknown" else "resolved"
    constraints = {
        str(factor["name"]): {
            "score": factor["score"],
            "note": factor["summary"],
            "basis": factor.get("basis", "assumed"),
            "gap": factor.get("gap"),
        }
        for factor in result.get("factors", [])
    }
    contradictions = [
        {
            "target": item.get("target"),
            "ref_id": item.get("ref_id"),
            "detail": item.get("detail"),
        }
        for item in result.get("contradictions", [])
    ]
    score = None if state == "abstained" else result.get("overall_score")
    return AnalysisDisplay(
        state,
        final.source_iteration_id,
        score,
        constraints,
        contradictions,
        final.locale,
        final.model,
        final.created_at,
    )


async def analysis_for_iteration(
    session: AsyncSession, idea_id: UUID, iteration: Iteration
) -> AnalysisDisplay:
    target_id = iteration.id
    if iteration.proposal_status == "pending" and iteration.parent_id is not None:
        target_id = iteration.parent_id
    workflow = await session.scalar(
        select(AnalysisWorkflow)
        .where(
            AnalysisWorkflow.idea_id == idea_id,
            AnalysisWorkflow.source_iteration_id == target_id,
        )
        .order_by(AnalysisWorkflow.created_at.desc())
        .limit(1)
    )
    final = None
    if workflow is not None:
        final = await session.scalar(
            select(ConstraintAnalysis).where(ConstraintAnalysis.workflow_id == workflow.id)
        )
    return display_from(workflow, final)


async def head_analysis(session: AsyncSession, idea_id: UUID) -> AnalysisDisplay:
    head = await session.scalar(
        select(Iteration)
        .where(Iteration.idea_id == idea_id, Iteration.branch == "main")
        .order_by(Iteration.revision.desc())
        .limit(1)
    )
    workflow = await session.scalar(
        select(AnalysisWorkflow)
        .where(AnalysisWorkflow.idea_id == idea_id)
        .order_by(AnalysisWorkflow.created_at.desc())
        .limit(1)
    )
    final = None
    if workflow is not None:
        final = await session.scalar(
            select(ConstraintAnalysis).where(ConstraintAnalysis.workflow_id == workflow.id)
        )
    if head is None and workflow is None:
        return AnalysisDisplay("unavailable", None, None, {}, [], None, None, None)
    display = display_from(workflow, final)
    if display.iteration_id is None and head is not None:
        display = AnalysisDisplay(
            display.state,
            head.id,
            display.realism_score,
            display.constraints,
            display.contradictions,
            display.locale,
            display.model,
            display.created_at,
        )
    return display
