from collections.abc import Hashable, Sequence
from typing import Final

RUN_LEVELS: Final[frozenset[str]] = frozenset({"optimistic", "base", "pessimistic", "failure"})


class RunRuleError(ValueError):
    """Raised when a scenario run breaks a rule."""


def validate_level(value: str) -> str:
    if value not in RUN_LEVELS:
        raise RunRuleError(f"Unknown scenario run level: {value}")
    return value


def validate_assumptions(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise RunRuleError("A scenario run states its assumptions")
    return cleaned


def assert_single_base(level: str, existing_levels: frozenset[str]) -> None:
    if level == "base" and "base" in existing_levels:
        raise RunRuleError("An option holds at most one base run")


def validate_values[Key: Hashable, Value](
    values: Sequence[tuple[Key, Value]],
) -> tuple[tuple[Key, Value], ...]:
    seen: set[Key] = set()
    for key, _ in values:
        if key in seen:
            raise RunRuleError("A run declares each variable once")
        seen.add(key)
    return tuple(values)
