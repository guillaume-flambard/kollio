import pytest

from src.modules.scenarios.domain.runs import (
    RUN_LEVELS,
    RunRuleError,
    assert_single_base,
    validate_assumptions,
    validate_level,
    validate_values,
)

BASE = "base"


def test_levels_are_the_four_declared_ones():
    assert RUN_LEVELS == frozenset({"optimistic", "base", "pessimistic", "failure"})


@pytest.mark.parametrize("level", sorted(RUN_LEVELS))
def test_validate_level_accepts_the_closed_set(level: str):
    assert validate_level(level) == level


@pytest.mark.parametrize("value", ["", "worst", "Optimistic", "likely"])
def test_validate_level_refuses_anything_else(value: str):
    with pytest.raises(RunRuleError):
        validate_level(value)


def test_assumptions_are_trimmed():
    assert validate_assumptions("  CTR stays stable  ") == "CTR stays stable"


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_assumptions_refused(value: str):
    with pytest.raises(RunRuleError):
        validate_assumptions(value)


def test_first_base_run_accepted():
    assert_single_base(BASE, existing_levels=frozenset())


def test_second_base_run_refused():
    with pytest.raises(RunRuleError):
        assert_single_base(BASE, existing_levels=frozenset({BASE}))


def test_repeated_optimistic_run_accepted():
    assert_single_base("optimistic", existing_levels=frozenset({BASE, "optimistic"}))


def test_duplicate_variable_in_one_run_refused():
    with pytest.raises(RunRuleError):
        validate_values([("v1", "1"), ("v1", "2")])


def test_distinct_variables_accepted():
    assert validate_values([("v1", "1"), ("v2", "2")]) == (("v1", "1"), ("v2", "2"))


def test_no_values_accepted():
    assert validate_values([]) == ()
