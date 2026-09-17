from decimal import Decimal


class VariableRuleError(ValueError):
    """Raised when a scenario variable breaks a rule."""


def validate_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise VariableRuleError("A scenario variable needs a name")
    return cleaned


def validate_range(
    *, low: Decimal, base: Decimal, high: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    if not low <= base <= high:
        raise VariableRuleError("The range must be ordered: low <= base <= high")
    return (low, base, high)
