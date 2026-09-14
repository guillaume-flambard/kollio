from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.constraint_analysis.adapters.postgres import (
    AnalysisWorkflow,
    PostgresAnalysisWorkflows,
)
from src.modules.constraint_analysis.domain.lifecycle import AnalysisStatus, queue_review
from src.modules.constraint_analysis.domain.models import AnalysisEvidence
from src.modules.experiments.service.reuse import learning_texts, reusable_learning_ids
from src.platform.config import get_settings


class AnalysisNotFoundError(LookupError):
    """Raised when an idea or analysis workflow is inaccessible."""


class AnalysisAuthorizationError(PermissionError):
    """Raised when the current member cannot perform an analysis action."""


@dataclass(frozen=True)
class LaunchOutcome:
    workflow: AnalysisWorkflow
    created: bool


async def launch_analysis(
    repository: PostgresAnalysisWorkflows,
    idea_id: UUID,
    subject: str,
    *,
    idempotency_key: str,
    locale: str,
    evidence: list[AnalysisEvidence],
    trace_context: Mapping[str, str],
) -> LaunchOutcome:
    context = await repository.accessible_idea(idea_id, subject)
    if context is None:
        raise AnalysisNotFoundError
    idea, actor = context
    existing = await repository.find_launch(idea_id, idempotency_key)
    if existing is not None:
        return LaunchOutcome(existing, created=False)
    head = await repository.main_head(idea_id)
    snapshot = (
        dict(head.payload)
        if head is not None
        else {"title": idea.title, "pitch": idea.pitch, "stage": idea.stage}
    )
    snapshot["company_context"] = await repository.active_company_context(idea.workspace_id)
    effective_evidence = list(evidence)
    settings = get_settings()
    workspace_ids = await repository.memberships(subject)
    reusable_ids = await reusable_learning_ids(
        repository.session,
        text=f"{snapshot.get('title', '')} {snapshot.get('pitch', '')}".strip(),
        workspace_ids=workspace_ids,
        settings=settings,
    )
    if reusable_ids:
        for learning_id, text in await learning_texts(repository.session, reusable_ids):
            effective_evidence.append(
                AnalysisEvidence(
                    id=f"learning:{learning_id}",
                    url=f"kollio://learning/{learning_id}",
                    text=text,
                )
            )
    snapshot["reused_learning_ids"] = [str(item) for item in reusable_ids]
    workflow = AnalysisWorkflow(
        id=uuid4(),
        idea_id=idea.id,
        source_iteration_id=head.id if head is not None else None,
        requested_by_id=actor.id,
        idempotency_key=idempotency_key,
        locale=locale,
        status=AnalysisStatus.QUEUED.value,
        current_step="dispatch",
        input_snapshot=snapshot,
        evidence=[item.model_dump(mode="json") for item in effective_evidence],
        draft_result=None,
        review_decision=None,
        trace_context=dict(trace_context),
        error_code=None,
    )
    return LaunchOutcome(await repository.add(workflow), created=True)


async def get_analysis(
    repository: PostgresAnalysisWorkflows,
    idea_id: UUID,
    workflow_id: UUID,
    subject: str,
) -> AnalysisWorkflow:
    context = await repository.accessible_workflow(idea_id, workflow_id, subject)
    if context is None:
        raise AnalysisNotFoundError
    workflow, _, _ = context
    return workflow


async def request_review(
    repository: PostgresAnalysisWorkflows,
    idea_id: UUID,
    workflow_id: UUID,
    subject: str,
    *,
    approved: bool,
    trace_context: Mapping[str, str],
) -> AnalysisWorkflow:
    context = await repository.accessible_workflow(idea_id, workflow_id, subject, lock=True)
    if context is None:
        raise AnalysisNotFoundError
    workflow, idea, actor = context
    if idea.owner_id != actor.id:
        raise AnalysisAuthorizationError
    if (
        workflow.status == AnalysisStatus.REVIEW_QUEUED.value
        and workflow.current_step == "dispatch_review"
        and workflow.review_decision is approved
    ):
        workflow.trace_context = dict(trace_context)
        return workflow
    workflow.status = queue_review(AnalysisStatus(workflow.status)).value
    workflow.current_step = "dispatch_review"
    workflow.review_decision = approved
    workflow.trace_context = dict(trace_context)
    return workflow
