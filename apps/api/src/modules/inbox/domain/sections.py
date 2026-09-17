from datetime import datetime
from uuid import UUID


def needs_convergence(status: str) -> bool:
    """A space the team has declared converging is waiting to be converged."""
    return status == "CONVERGING"


def is_ready_to_decide(status: str, *, has_decision: bool) -> bool:
    """A prepared space is prompted once, until a Decision exists for it."""
    return status == "READY_TO_DECIDE" and not has_decision


def experiment_needs_outcome(experiment_status: str, outcome_count: int) -> bool:
    """A completed experiment with nothing observed has nothing to compare."""
    return experiment_status == "completed" and outcome_count == 0


def learning_awaits_confirmation(learning_status: str) -> bool:
    """A draft Learning is waiting for the human who makes it canonical."""
    return learning_status == "draft"


def is_answered_by(owner_id: UUID, participant_ids: frozenset[UUID], actor_id: UUID) -> bool:
    """Only the owner and the participants are asked for their own input."""
    return actor_id == owner_id or actor_id in participant_ids


def inbox_order_key(entry: tuple[datetime, UUID]) -> tuple[datetime, UUID]:
    """Longest wait first, and deterministic when two things are the same age."""
    return entry
