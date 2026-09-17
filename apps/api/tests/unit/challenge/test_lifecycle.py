import pytest

from src.modules.challenge.domain.lifecycle import (
    InvalidRunTransition,
    complete_run,
    fail_run,
    is_terminal,
    start_run,
)


def test_a_run_starts_from_open():
    assert start_run("OPEN") == "RUNNING"


def test_a_running_run_can_be_completed():
    assert complete_run("RUNNING") == "COMPLETED"


def test_a_running_run_can_fail():
    assert fail_run("RUNNING") == "FAILED"


@pytest.mark.parametrize("status", ["RUNNING", "COMPLETED", "FAILED"])
def test_only_open_can_start(status: str):
    with pytest.raises(InvalidRunTransition):
        start_run(status)


@pytest.mark.parametrize("status", ["OPEN", "COMPLETED", "FAILED"])
def test_only_running_can_complete(status: str):
    with pytest.raises(InvalidRunTransition):
        complete_run(status)


@pytest.mark.parametrize("status", ["OPEN", "COMPLETED", "FAILED"])
def test_only_running_can_fail(status: str):
    with pytest.raises(InvalidRunTransition):
        fail_run(status)


@pytest.mark.parametrize("status", ["COMPLETED", "FAILED"])
def test_completed_and_failed_are_terminal(status: str):
    assert is_terminal(status) is True


@pytest.mark.parametrize("status", ["OPEN", "RUNNING"])
def test_open_and_running_are_not_terminal(status: str):
    assert is_terminal(status) is False
