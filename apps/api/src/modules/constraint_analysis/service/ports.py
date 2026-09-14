from collections.abc import Mapping
from typing import Protocol
from uuid import UUID

from src.modules.constraint_analysis.domain.models import (
    AnalystReport,
    ChallengerReport,
    CompanyFitReport,
    ConstraintAnalysisResult,
    EvidenceReport,
)


class AnalysisQueue(Protocol):
    async def dispatch(self, workflow_id: UUID, trace_context: Mapping[str, str]) -> None: ...

    async def dispatch_review(
        self, workflow_id: UUID, approved: bool, trace_context: Mapping[str, str]
    ) -> None: ...


class ConstraintReasoningGateway(Protocol):
    """The five adversarial steps behind one analysis. Each method is one call
    to a task-class-routed model; `synthesize` reads the challenger and the
    evidence critic, so it is the only place the member-facing conclusion is
    written. `model_commodity` and `model_visible` name which model ran each
    tier, so the persisted steps can be audited later."""

    model_commodity: str
    model_visible: str

    async def analyst(self, *, brief: dict, locale: str) -> AnalystReport: ...

    async def challenger(self, *, brief: dict, locale: str) -> ChallengerReport: ...

    async def evidence_critic(self, *, brief: dict, locale: str) -> EvidenceReport: ...

    async def company_fit(self, *, brief: dict, locale: str) -> CompanyFitReport: ...

    async def synthesize(
        self,
        *,
        brief: dict,
        analyst: AnalystReport,
        challenger: ChallengerReport,
        evidence_critic: EvidenceReport,
        company_fit: CompanyFitReport,
        locale: str,
    ) -> ConstraintAnalysisResult: ...
