from decimal import Decimal

import pytest

from src.platform.evaluation import LiveEvaluationBudgetExceeded, LiveEvaluationGuard


async def test_live_evaluation_guard_reports_incomplete_cases_when_budget_is_exhausted():
    guard = LiveEvaluationGuard(
        max_cases=1,
        budget_usd=Decimal("0.01"),
        estimated_case_cost_usd=Decimal("0.01"),
        requests_per_minute=60_000,
    )
    await guard.authorize(incomplete_cases=2)
    with pytest.raises(LiveEvaluationBudgetExceeded, match="2 cases incomplete"):
        await guard.authorize(incomplete_cases=2)
