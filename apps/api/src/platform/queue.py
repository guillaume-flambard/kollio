import logging
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import Depends

from src.platform.config import Settings, get_settings

logger = logging.getLogger("kollio.queue")


class AnalysisQueue:
    """Enqueues deposit analyses. Overridable in tests via dependency overrides."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def enqueue(self, **job: Any) -> None:
        pool = await create_pool(RedisSettings.from_dsn(self.settings.redis_url))
        try:
            await pool.enqueue_job("analyze_deposit", **job)
        finally:
            await pool.aclose()


async def get_analysis_queue(
    settings: Settings = Depends(get_settings),
) -> AnalysisQueue:
    return AnalysisQueue(settings)
