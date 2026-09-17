from decimal import Decimal

import pytest

from src.modules.scenarios.domain.variables import (
    VariableRuleError,
    validate_name,
    validate_range,
)


def test_name_is_trimmed():
    assert validate_name("  CTR  ") == "CTR"


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_name_refused(value: str):
    with pytest.raises(VariableRuleError):
        validate_name(value)


def test_ordered_range_accepted():
    assert validate_range(low=Decimal("1"), base=Decimal("2"), high=Decimal("3")) == (
        Decimal("1"),
        Decimal("2"),
        Decimal("3"),
    )


def test_flat_range_accepted():
    assert validate_range(low=Decimal("2"), base=Decimal("2"), high=Decimal("2")) == (
        Decimal("2"),
        Decimal("2"),
        Decimal("2"),
    )


def test_low_above_base_refused():
    with pytest.raises(VariableRuleError):
        validate_range(low=Decimal("3"), base=Decimal("2"), high=Decimal("4"))


def test_base_above_high_refused():
    with pytest.raises(VariableRuleError):
        validate_range(low=Decimal("1"), base=Decimal("4"), high=Decimal("3"))


def test_low_above_high_refused():
    with pytest.raises(VariableRuleError):
        validate_range(low=Decimal("4"), base=Decimal("4"), high=Decimal("3"))
