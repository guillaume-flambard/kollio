import pytest

from src.modules.experiments.domain.lifecycle import (
    ExperimentRuleError,
    compose_learning_draft,
    decide_learning_status,
    decide_transition,
)


def test_the_lifecycle_accepts_the_decided_moves():
    assert decide_transition(current="proposed", target="running") == "running"
    assert decide_transition(current="running", target="completed") == "completed"
    assert decide_transition(current="running", target="cancelled") == "cancelled"
    assert decide_transition(current="proposed", target="cancelled") == "cancelled"


def test_terminal_statuses_never_move():
    with pytest.raises(ExperimentRuleError):
        decide_transition(current="completed", target="running")
    with pytest.raises(ExperimentRuleError):
        decide_transition(current="cancelled", target="running")


def test_an_unknown_status_is_refused():
    with pytest.raises(ExperimentRuleError):
        decide_transition(current="proposed", target="paused")


def test_the_draft_composes_the_hypothesis_and_observations():
    draft = compose_learning_draft(
        hypothesis="Offline matters",
        success_metric="trials",
        target="20",
        outcomes=[{"metric": "trials", "value": "26", "unit": None, "comment": "enterprise only"}],
    )
    assert "Hypothesis: Offline matters" in draft
    assert "Success metric: trials" in draft
    assert "Target: 20" in draft
    assert "- trials: 26 - enterprise only" in draft


def test_the_draft_says_when_nothing_was_observed():
    draft = compose_learning_draft(
        hypothesis="H", success_metric="trials", target=None, outcomes=[]
    )
    assert "no outcome recorded yet" in draft


def test_a_confirmed_learning_does_not_return_to_draft():
    assert decide_learning_status(current="draft", target="confirmed") == "confirmed"
    with pytest.raises(ExperimentRuleError):
        decide_learning_status(current="confirmed", target="draft")
