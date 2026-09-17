import itertools

import pytest

from src.modules.decision_spaces.domain.lifecycle import (
    DECISION_SPACE_STATUSES,
    DECLARED_TRANSITIONS,
    DecisionSpaceStatusError,
    can_transition,
    reopen_requires_reason,
    validate_status,
)

# Independent transcription of the transition table in design.md. If the module
# and this set ever disagree, one of the two changed without the other.
DECLARED: frozenset[tuple[str, str]] = frozenset(
    {
        ("OPEN", "EXPLORING"),
        ("EXPLORING", "CONVERGING"),
        ("CONVERGING", "READY_TO_DECIDE"),
        ("READY_TO_DECIDE", "DECIDED"),
        ("DECIDED", "TESTING"),
        ("TESTING", "LEARNED"),
        ("DECIDED", "REOPENED"),
        ("TESTING", "REOPENED"),
        ("LEARNED", "REOPENED"),
        ("REOPENED", "EXPLORING"),
    }
)

REOPEN_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        ("DECIDED", "REOPENED"),
        ("TESTING", "REOPENED"),
        ("LEARNED", "REOPENED"),
    }
)

UNDECLARED: frozenset[tuple[str, str]] = (
    frozenset(itertools.product(DECISION_SPACE_STATUSES, DECISION_SPACE_STATUSES)) - DECLARED
)


def test_statuses_are_the_eight_declared_ones():
    assert DECISION_SPACE_STATUSES == frozenset(
        {
            "OPEN",
            "EXPLORING",
            "CONVERGING",
            "READY_TO_DECIDE",
            "DECIDED",
            "TESTING",
            "LEARNED",
            "REOPENED",
        }
    )


def test_declared_transitions_match_the_design_table():
    assert DECLARED_TRANSITIONS == DECLARED


@pytest.mark.parametrize(("from_status", "to_status"), sorted(DECLARED))
def test_every_declared_edge_is_accepted(from_status: str, to_status: str):
    assert can_transition(from_status, to_status) is True


@pytest.mark.parametrize(("from_status", "to_status"), sorted(UNDECLARED))
def test_every_undeclared_edge_is_refused(from_status: str, to_status: str):
    assert can_transition(from_status, to_status) is False


def test_a_status_never_transitions_to_itself():
    for status in DECISION_SPACE_STATUSES:
        assert can_transition(status, status) is False


def test_ready_to_decide_cannot_go_back_to_converging():
    assert can_transition("READY_TO_DECIDE", "CONVERGING") is False


def test_terminal_space_cannot_resume_without_reopening():
    assert can_transition("LEARNED", "TESTING") is False
    assert can_transition("LEARNED", "EXPLORING") is False


def test_a_space_that_was_never_decided_cannot_be_reopened():
    for status in ("OPEN", "EXPLORING", "CONVERGING", "READY_TO_DECIDE", "REOPENED"):
        assert can_transition(status, "REOPENED") is False


@pytest.mark.parametrize(("from_status", "to_status"), sorted(REOPEN_EDGES))
def test_reopening_requires_a_reason(from_status: str, to_status: str):
    assert reopen_requires_reason(from_status, to_status) is True


@pytest.mark.parametrize(("from_status", "to_status"), sorted(DECLARED - REOPEN_EDGES))
def test_forward_transitions_do_not_require_a_reason(from_status: str, to_status: str):
    assert reopen_requires_reason(from_status, to_status) is False


@pytest.mark.parametrize("status", sorted(DECISION_SPACE_STATUSES))
def test_validate_status_accepts_the_closed_set(status: str):
    assert validate_status(status) == status


@pytest.mark.parametrize("value", ["", "open", "ARCHIVED", "DONE", "decided"])
def test_validate_status_refuses_anything_outside_the_closed_set(value: str):
    with pytest.raises(DecisionSpaceStatusError):
        validate_status(value)
