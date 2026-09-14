"""Experiment lifecycle and learning rules.

Wayfinder ticket "Experiment/Outcome/Learning" (#47) fixed the shape: an
experiment runs proposed -> running -> completed or cancelled, outcomes
are observed facts any reader-member may record, and a learning is
drafted on completion then confirmed by a member, linked to its
experiment, outcomes and idea.
"""

from typing import Final

STATUSES: Final[frozenset[str]] = frozenset({"proposed", "running", "completed", "cancelled"})
TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "proposed": frozenset({"running", "cancelled"}),
    "running": frozenset({"completed", "cancelled"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
}
LEARNING_STATUSES: Final[frozenset[str]] = frozenset({"draft", "confirmed"})


class ExperimentRuleError(ValueError):
    """Raised when an experiment transition or learning edit is invalid."""


def decide_transition(*, current: str, target: str) -> str:
    if target not in STATUSES:
        raise ExperimentRuleError(f"Unknown experiment status: {target}")
    if target not in TRANSITIONS[current]:
        raise ExperimentRuleError(f"Cannot move an experiment from {current} to {target}")
    return target


def compose_learning_draft(
    *,
    hypothesis: str,
    success_metric: str,
    target: str | None,
    outcomes: list[dict[str, str | None]],
) -> str:
    """A deterministic draft the member edits; not a model claim."""
    lines = [f"Hypothesis: {hypothesis}", f"Success metric: {success_metric}"]
    if target:
        lines.append(f"Target: {target}")
    if outcomes:
        lines.append("Observed:")
        for outcome in outcomes:
            value = outcome.get("value") or ""
            unit = f" {outcome['unit']}" if outcome.get("unit") else ""
            comment = f" - {outcome['comment']}" if outcome.get("comment") else ""
            lines.append(f"- {outcome.get('metric')}: {value}{unit}{comment}")
    else:
        lines.append("Observed: no outcome recorded yet")
    return "\n".join(lines)


def decide_learning_status(*, current: str, target: str) -> str:
    if target not in LEARNING_STATUSES:
        raise ExperimentRuleError(f"Unknown learning status: {target}")
    if current == "confirmed" and target == "draft":
        raise ExperimentRuleError("A confirmed learning cannot return to draft")
    return target
