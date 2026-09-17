from collections.abc import Mapping, Sequence
from typing import Final

TRIGGER_DIRECTIONS: Final[frozenset[str]] = frozenset({"above", "below"})


class TriggerShapeError(ValueError):
    """Raised when a revisit trigger is not a metric with optional direction, threshold and note."""


def _text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TriggerShapeError(f"{field} must be text")
    cleaned = value.strip()
    if not cleaned:
        raise TriggerShapeError(f"{field} must not be blank")
    return cleaned


def validate_triggers(values: Sequence[object] | None) -> list[dict[str, str | None]]:
    """Normalize revisit triggers: a metric is required, the rest is optional.

    A metric alone is a legitimate trigger: it is a reminder to look, and the
    stored shape says so instead of pretending to a threshold.
    """
    if values is None:
        return []
    triggers: list[dict[str, str | None]] = []
    for value in values:
        if not isinstance(value, Mapping):
            raise TriggerShapeError("a revisit trigger must be an object")
        metric = _text(value.get("metric"), "metric")
        if metric is None:
            raise TriggerShapeError("a revisit trigger needs a metric")
        direction = _text(value.get("direction"), "direction")
        if direction is not None and direction not in TRIGGER_DIRECTIONS:
            raise TriggerShapeError(f"Unknown revisit direction: {direction}")
        triggers.append(
            {
                "metric": metric,
                "direction": direction,
                "threshold": _text(value.get("threshold"), "threshold"),
                "note": _text(value.get("note"), "note"),
            }
        )
    return triggers
