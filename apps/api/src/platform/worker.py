from arq.connections import RedisSettings
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.agents.graph import build_analysis_graph, build_graph
from src.modules.iterations.adapters.postgres import PostgresIterations
from src.platform.config import get_settings
from src.platform.llm import Gateway
from src.platform.telemetry import configure_telemetry


async def assess_idea(
    ctx, workflow_id: str, locale: str, title: str, pitch: str, evidence: list[dict]
):
    if locale not in ("fr", "en"):
        raise ValueError("Unsupported locale")
    settings = get_settings()
    async with AsyncPostgresSaver.from_conn_string(settings.checkpoint_url) as saver:
        graph = build_graph(Gateway(settings), saver, ctx["sessions"])
        result = await graph.ainvoke(
            {
                "workflow_id": workflow_id,
                "locale": locale,
                "title": title,
                "pitch": pitch,
                "evidence": evidence,
                "finding": {},
            },
            {"configurable": {"thread_id": workflow_id}},
        )
        return {"workflow_id": workflow_id, "awaiting_review": bool(result.get("__interrupt__"))}


async def analyze_deposit(
    ctx,
    workflow_id: str,
    idea_id: str,
    iteration_id: str,
    locale: str,
    title: str,
    pitch: str,
):
    from uuid import UUID

    if locale not in ("fr", "en"):
        raise ValueError("Unsupported locale")

    settings = get_settings()
    async with AsyncPostgresSaver.from_conn_string(settings.checkpoint_url) as saver:
        sessions = ctx["sessions"]
        async with sessions() as session:
            analyses = PostgresIterations(session)
            graph = build_analysis_graph(Gateway(settings), saver, sessions, analyses)
            result = await graph.ainvoke(
                {
                    "workflow_id": workflow_id,
                    "locale": locale,
                    "title": title,
                    "pitch": pitch,
                    "evidence": [],
                    "finding": {},
                    "idea_id": UUID(idea_id),
                    "iteration_id": UUID(iteration_id),
                },
                {"configurable": {"thread_id": workflow_id}},
            )
            return {"workflow_id": workflow_id, "analysis_id": result.get("analysis_id")}


async def startup(ctx):
    settings = get_settings()
    ctx["engine"] = create_async_engine(settings.database_url, pool_pre_ping=True)
    ctx["sessions"] = async_sessionmaker(ctx["engine"], expire_on_commit=False)
    ctx["telemetry"] = configure_telemetry(settings)


async def shutdown(ctx):
    await ctx["engine"].dispose()
    if ctx["telemetry"]:
        ctx["telemetry"].shutdown()


class WorkerSettings:
    functions = [assess_idea, analyze_deposit]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 2
    job_timeout = 180
