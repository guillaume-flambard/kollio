from collections.abc import Mapping
from typing import Any, cast
from uuid import UUID

from src.modules.constraint_analysis.service.ports import AnalysisQueue
from src.platform.worker import execute_constraint_analysis


class TaskiqAnalysisQueue(AnalysisQueue):
    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None:
        task = cast(Any, execute_constraint_analysis)
        await task.kiq(str(workflow_id), dict(trace_context), None)

    async def dispatch_review(
        self,
        workflow_id: UUID,
        approved: bool,
        trace_context: Mapping[str, str],
    ) -> None:
        task = cast(Any, execute_constraint_analysis)
        await task.kiq(str(workflow_id), dict(trace_context), approved)
