from collections.abc import Mapping
from typing import Protocol
from uuid import UUID

from src.modules.constraint_analysis.domain.models import (
    AnalysisEvidence,
    ConstraintAnalysisResult,
)


class AnalysisQueue(Protocol):
    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None: ...

    async def dispatch_review(
        self, workflow_id: UUID, approved: bool, trace_context: Mapping[str, str]
    ) -> None: ...


class ConstraintAnalysisGateway(Protocol):
    async def analyze(
        self,
        *,
        title: str,
        pitch: str,
        locale: str,
        evidence: list[AnalysisEvidence],
    ) -> ConstraintAnalysisResult: ...
