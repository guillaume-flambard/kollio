from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.modules.company_context.api.routes import router as company_context_router
from src.modules.constraint_analysis.adapters.taskiq import TaskiqAnalysisQueue
from src.modules.constraint_analysis.api.routes import router as analysis_router
from src.modules.decision_spaces.api.routes import router as decision_spaces_router
from src.modules.experiments.api.routes import router as experiments_router
from src.modules.ideas.api.routes import (
    router as ideas_router,
)
from src.modules.ideas.api.routes import (
    workspace_ideas_router,
)
from src.modules.iterations.api.routes import router as iterations_router
from src.modules.profiles.api.routes import router as profiles_router
from src.modules.workspaces.api.routes import router as workspaces_router
from src.platform.config import Settings, get_settings
from src.platform.locale import MESSAGES, resolve_locale
from src.platform.telemetry import configure_telemetry
from src.platform.worker import broker


class Health(BaseModel):
    status: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        provider = configure_telemetry(settings)
        engine = (
            create_async_engine(settings.database_url, pool_pre_ping=True)
            if settings.database_url
            else None
        )
        app.state.sessions = async_sessionmaker(engine, expire_on_commit=False) if engine else None
        app.state.redis = Redis.from_url(
            settings.redis_url, socket_connect_timeout=2, socket_timeout=2
        )
        await broker.startup()
        try:
            yield
        finally:
            await broker.shutdown()
            await app.state.redis.aclose()
            if engine:
                await engine.dispose()
            if provider:
                provider.shutdown()

    app = FastAPI(title="Kollio API", lifespan=lifespan)
    app.state.analysis_queue = TaskiqAnalysisQueue()
    app.dependency_overrides[get_settings] = lambda: settings

    @app.middleware("http")
    async def locale(request: Request, call_next):
        request.state.locale = resolve_locale(request.headers.get("accept-language", ""))
        response = await call_next(request)
        response.headers["Content-Language"] = request.state.locale
        response.headers["Vary"] = "Accept-Language"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422, content={"detail": MESSAGES[request.state.locale]["invalid"]}
        )

    @app.get("/health/live", response_model=Health, operation_id="health_live")
    async def live():
        return Health(status="ok")

    @app.get("/health/ready", response_model=Health, operation_id="health_ready")
    async def ready(request: Request):
        try:
            async with app.state.sessions() as session:
                await session.execute(text("SELECT 1 FROM ideas LIMIT 1"))
            await app.state.redis.ping()
        except Exception:
            return JSONResponse(
                status_code=503, content={"detail": MESSAGES[request.state.locale]["unavailable"]}
            )
        return Health(status="ok")

    app.include_router(ideas_router)
    app.include_router(analysis_router)
    app.include_router(iterations_router)
    app.include_router(workspace_ideas_router)
    app.include_router(workspaces_router)
    app.include_router(profiles_router)
    app.include_router(company_context_router)
    app.include_router(decision_spaces_router)
    app.include_router(experiments_router)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health/live,health/ready")
    return app


app = create_app()
