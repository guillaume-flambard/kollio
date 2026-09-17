TERMINAL_RUN_STATUSES: frozenset[str] = frozenset({"COMPLETED", "FAILED"})


class InvalidRunTransition(ValueError):
    """Raised when a challenge run lifecycle transition is not allowed."""


def start_run(status: str) -> str:
    if status != "OPEN":
        raise InvalidRunTransition(f"Cannot start a challenge run in {status} status")
    return "RUNNING"


def complete_run(status: str) -> str:
    if status != "RUNNING":
        raise InvalidRunTransition(f"Cannot complete a challenge run in {status} status")
    return "COMPLETED"


def fail_run(status: str) -> str:
    if status != "RUNNING":
        raise InvalidRunTransition(f"Cannot fail a challenge run in {status} status")
    return "FAILED"


def is_terminal(status: str) -> bool:
    return status in TERMINAL_RUN_STATUSES
