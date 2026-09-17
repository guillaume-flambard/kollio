from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from src.modules.inbox.domain.sections import (
    experiment_needs_outcome,
    inbox_order_key,
    is_answered_by,
    is_ready_to_decide,
    learning_awaits_confirmation,
    needs_convergence,
)

OWNER = UUID("00000000-0000-0000-0000-000000000011")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000012")
MEMBER = UUID("00000000-0000-0000-0000-000000000013")

OTHER_STATUSES = [
    "OPEN",
    "EXPLORING",
    "READY_TO_DECIDE",
    "DECIDED",
    "TESTING",
    "LEARNED",
    "REOPENED",
]


def test_a_converging_space_needs_convergence():
    assert needs_convergence("CONVERGING") is True


@pytest.mark.parametrize("status", OTHER_STATUSES)
def test_no_other_status_needs_convergence(status: str):
    assert needs_convergence(status) is False


def test_a_prepared_space_without_a_decision_is_ready_to_decide():
    assert is_ready_to_decide("READY_TO_DECIDE", has_decision=False) is True


def test_a_prepared_space_holding_a_decision_is_not_prompted_again():
    assert is_ready_to_decide("READY_TO_DECIDE", has_decision=True) is False


@pytest.mark.parametrize("status", ["OPEN", "EXPLORING", "CONVERGING", "DECIDED", "LEARNED"])
def test_no_other_status_is_ready_to_decide(status: str):
    assert is_ready_to_decide(status, has_decision=False) is False


def test_a_completed_experiment_without_an_outcome_needs_learning():
    assert experiment_needs_outcome("completed", outcome_count=0) is True


def test_a_completed_experiment_with_an_outcome_does_not():
    assert experiment_needs_outcome("completed", outcome_count=1) is False


@pytest.mark.parametrize("status", ["proposed", "running", "cancelled"])
def test_an_unfinished_experiment_does_not_need_an_outcome(status: str):
    assert experiment_needs_outcome(status, outcome_count=0) is False


def test_a_draft_learning_awaits_confirmation():
    assert learning_awaits_confirmation("draft") is True


def test_a_confirmed_learning_is_done():
    assert learning_awaits_confirmation("confirmed") is False


def test_the_owner_answers_for_a_space():
    assert is_answered_by(OWNER, frozenset({OWNER}), OWNER) is True


def test_a_participant_answers_for_a_space():
    assert is_answered_by(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_an_uninvolved_member_does_not_answer_for_a_space():
    assert is_answered_by(OWNER, frozenset({OWNER}), MEMBER) is False


def test_a_space_with_no_participants_is_answered_only_by_its_owner():
    assert is_answered_by(OWNER, frozenset(), MEMBER) is False


def test_order_puts_the_longest_wait_first():
    now = datetime(2026, 9, 17, 12, 0, tzinfo=UTC)
    older = (now - timedelta(days=2), UUID(int=2))
    newer = (now - timedelta(hours=1), UUID(int=1))
    assert sorted([newer, older], key=inbox_order_key) == [older, newer]


def test_order_is_deterministic_on_an_identical_age():
    now = datetime(2026, 9, 17, 12, 0, tzinfo=UTC)
    first = (now, UUID(int=1))
    second = (now, UUID(int=2))
    assert sorted([second, first], key=inbox_order_key) == [first, second]
