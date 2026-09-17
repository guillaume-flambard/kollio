from collections.abc import Mapping
from typing import Any, cast
from uuid import UUID

from src.modules.challenge.service.ports import ChallengeQueue
from src.platform.worker import execute_challenge


class TaskiqChallengeQueue(ChallengeQueue):
    async def dispatch(self, run_id: UUID, trace_context: Mapping[str, str]) -> None:
        task = cast(Any, execute_challenge)
        await task.kiq(str(run_id), dict(trace_context))
