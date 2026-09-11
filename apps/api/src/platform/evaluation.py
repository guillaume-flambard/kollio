"""Budget and rate controls for opt-in live evaluations."""

import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from time import monotonic


class LiveEvaluationBudgetExceeded(RuntimeError):
    pass


@dataclass
class LiveEvaluationGuard:
    max_cases: int
    budget_usd: Decimal
    estimated_case_cost_usd: Decimal
    requests_per_minute: int
    attempted_cases: int = 0
    reserved_usd: Decimal = Decimal("0")
    last_started_at: float | None = None

    def __post_init__(self) -> None:
        if self.max_cases < 1:
            raise ValueError("max_cases must be positive")
        if self.budget_usd <= 0 or self.estimated_case_cost_usd <= 0:
            raise ValueError("evaluation costs must be positive")
        if self.requests_per_minute < 1:
            raise ValueError("requests_per_minute must be positive")

    @classmethod
    def from_environment(cls) -> LiveEvaluationGuard:
        return cls(
            max_cases=int(os.environ.get("KOLLIO_LIVE_EVAL_MAX_CASES", "2")),
            budget_usd=Decimal(os.environ.get("KOLLIO_LIVE_EVAL_BUDGET_USD", "0.10")),
            estimated_case_cost_usd=Decimal(
                os.environ.get("KOLLIO_LIVE_EVAL_ESTIMATED_CASE_COST_USD", "0.01")
            ),
            requests_per_minute=int(os.environ.get("KOLLIO_LIVE_EVAL_REQUESTS_PER_MINUTE", "6")),
        )

    async def authorize(self, incomplete_cases: int) -> None:
        projected_spend = self.reserved_usd + self.estimated_case_cost_usd
        if self.attempted_cases >= self.max_cases or projected_spend > self.budget_usd:
            raise LiveEvaluationBudgetExceeded(
                f"Live evaluation budget exhausted; {incomplete_cases} cases incomplete"
            )
        minimum_interval = 60 / self.requests_per_minute
        now = monotonic()
        if self.last_started_at is not None:
            await asyncio.sleep(max(0, minimum_interval - (now - self.last_started_at)))
        self.attempted_cases += 1
        self.reserved_usd = projected_spend
        self.last_started_at = monotonic()
