from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from opentelemetry import trace
from opentelemetry.propagate import extract
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from taskiq import Context as TaskiqContext
from taskiq import SimpleRetryMiddleware, TaskiqDepends, TaskiqEvents, TaskiqState
from taskiq_redis import RedisStreamBroker

from src.modules.constraint_analysis.adapters.litellm import (
    LiteLLMConstraintAnalysisGateway,
)
from src.modules.constraint_analysis.adapters.postgres import (
    AnalysisWorkflow,
    ConstraintAnalysis,
    PostgresAnalysisWorkflows,
)
from src.modules.constraint_analysis.agent.graph import build_constraint_analysis_graph
from src.modules.constraint_analysis.domain.lifecycle import (
    AnalysisStatus,
    await_review,
    failure_status,
    finish_review,
    start_execution,
)
from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult
from src.platform.config import get_settings
from src.platform.telemetry import configure_telemetry

settings = get_settings()
broker = RedisStreamBroker(settings.redis_url, queue_name="kollio-agent-jobs").with_middlewares(
    SimpleRetryMiddleware(default_retry_count=3)
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    state.engine = engine
    state.sessions = async_sessionmaker(engine, expire_on_commit=False)
    state.telemetry = configure_telemetry(settings)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    await state.engine.dispose()
    if state.telemetry:
        state.telemetry.shutdown()


async def _load_and_start(
    sessions: async_sessionmaker[AsyncSession],
    workflow_id: UUID,
) -> AnalysisWorkflow | None:
    async with sessions() as session:
        repository = PostgresAnalysisWorkflows(session)
        workflow = await repository.get_for_worker(workflow_id, lock=True)
        if workflow is None:
            return None
        status = AnalysisStatus(workflow.status)
        if status in (AnalysisStatus.COMPLETED, AnalysisStatus.REJECTED):
            return None
        workflow.status = start_execution(status).value
        workflow.current_step = "analyze" if status is AnalysisStatus.QUEUED else "review"
        await session.commit()
        return workflow


async def _record_failure(
    sessions: async_sessionmaker[AsyncSession],
    workflow_id: UUID,
    code: str,
    *,
    retrying: bool,
    review: bool,
) -> None:
    async with sessions() as session:
        workflow = await PostgresAnalysisWorkflows(session).get_for_worker(workflow_id, lock=True)
        if workflow is not None:
            workflow.status = failure_status(retrying=retrying, review=review).value
            workflow.current_step = "retry" if retrying else "failed"
            workflow.error_code = code[:100]
            workflow.finished_at = None if retrying else datetime.now(UTC)
            await session.commit()


@broker.task(
    task_name="constraint-analysis.execute",
    timeout=180,
    retry_on_error=True,
    max_retries=3,
)
async def execute_constraint_analysis(
    workflow_id: str,
    trace_context: dict[str, str],
    approved: bool | None,
    task_context: Annotated[TaskiqContext, TaskiqDepends()],
) -> dict[str, Any]:
    identifier = UUID(workflow_id)
    otel_context = extract(carrier=trace_context)
    tracer = trace.get_tracer("kollio.constraint_analysis")
    try:
        with tracer.start_as_current_span(
            "constraint_analysis.worker", context=otel_context
        ) as span:
            span.set_attribute("kollio.workflow.id", workflow_id)
            workflow = await _load_and_start(task_context.state.sessions, identifier)
            if workflow is None:
                return {"workflow_id": workflow_id, "ignored": True}
            span.set_attribute("kollio.idea.id", str(workflow.idea_id))
            span.set_attribute("kollio.locale", workflow.locale)
            async with AsyncPostgresSaver.from_conn_string(settings.checkpoint_url) as saver:
                graph = build_constraint_analysis_graph(
                    LiteLLMConstraintAnalysisGateway(settings), saver
                )
                config = {"configurable": {"thread_id": workflow_id}}
                if approved is None:
                    graph_input: dict[str, Any] | Command[Any] = {
                        "workflow_id": workflow_id,
                        "locale": workflow.locale,
                        "title": str(workflow.input_snapshot["title"]),
                        "pitch": str(workflow.input_snapshot["pitch"]),
                        "evidence": workflow.evidence,
                        "result": {},
                        "approved": None,
                    }
                else:
                    graph_input = Command(resume=approved)
                result = await graph.ainvoke(graph_input, config)

            async with task_context.state.sessions() as session:
                repository = PostgresAnalysisWorkflows(session)
                current = await repository.get_for_worker(identifier, lock=True)
                if current is None:
                    return {"workflow_id": workflow_id, "ignored": True}
                if result.get("__interrupt__"):
                    draft = ConstraintAnalysisResult.model_validate(result["result"])
                    current.draft_result = draft.model_dump(mode="json")
                    current.status = await_review(AnalysisStatus(current.status)).value
                    current.current_step = "human_review"
                elif approved is False:
                    current.status = finish_review(AnalysisStatus(current.status), False).value
                    current.current_step = "rejected"
                    current.finished_at = datetime.now(UTC)
                else:
                    final = ConstraintAnalysisResult.model_validate(result["result"])
                    await repository.store_final(
                        ConstraintAnalysis(
                            id=uuid4(),
                            workflow_id=current.id,
                            idea_id=current.idea_id,
                            source_iteration_id=current.source_iteration_id,
                            result=final.model_dump(mode="json"),
                            model=settings.llm_model,
                            locale=current.locale,
                        )
                    )
                    current.draft_result = final.model_dump(mode="json")
                    current.status = finish_review(AnalysisStatus(current.status), True).value
                    current.current_step = "completed"
                    current.finished_at = datetime.now(UTC)
                await session.commit()
            return {"workflow_id": workflow_id, "status": current.status}
    except Exception as error:
        retries = int(task_context.message.labels.get("_retries", 0)) + 1
        max_retries = int(task_context.message.labels.get("max_retries", 3))
        await _record_failure(
            task_context.state.sessions,
            identifier,
            type(error).__name__,
            retrying=retries < max_retries,
            review=approved is not None,
        )
        raise
