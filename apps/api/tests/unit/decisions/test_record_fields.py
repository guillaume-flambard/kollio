import pytest

from src.modules.decisions.domain.record import (
    RECORD_SIDES,
    RecordFieldError,
    RecordSideError,
    validate_alternatives,
    validate_rationale,
    validate_side,
)

SELECTED = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"


def test_sides_are_for_and_against():
    assert RECORD_SIDES == frozenset({"for", "against"})


def test_validate_rationale_trims_and_keeps_content():
    assert validate_rationale("  Because B is cheaper  ") == "Because B is cheaper"


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_rationale_refused(value: str):
    with pytest.raises(RecordFieldError):
        validate_rationale(value)


@pytest.mark.parametrize("side", sorted(RECORD_SIDES))
def test_validate_side_accepts_the_closed_set(side: str):
    assert validate_side(side) == side


@pytest.mark.parametrize("value", ["", "pro", "FOR", "neutral"])
def test_validate_side_refuses_anything_else(value: str):
    with pytest.raises(RecordSideError):
        validate_side(value)


def test_no_alternatives_is_allowed():
    assert validate_alternatives([], SELECTED) == []


def test_alternatives_are_kept_in_order():
    assert validate_alternatives([OTHER], SELECTED) == [OTHER]


def test_the_selected_option_cannot_be_a_rejected_alternative():
    with pytest.raises(RecordFieldError):
        validate_alternatives([OTHER, SELECTED], SELECTED)


def test_the_selected_option_refused_even_alone():
    with pytest.raises(RecordFieldError):
        validate_alternatives([SELECTED], SELECTED)
