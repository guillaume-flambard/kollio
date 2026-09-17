import pytest

from src.modules.options.domain.evidence import (
    EVIDENCE_SIDES,
    EvidenceSideError,
    validate_side,
)


def test_sides_are_for_and_against():
    assert EVIDENCE_SIDES == frozenset({"for", "against"})


@pytest.mark.parametrize("side", sorted(EVIDENCE_SIDES))
def test_validate_side_accepts_the_closed_set(side: str):
    assert validate_side(side) == side


@pytest.mark.parametrize("value", ["", "FOR", "support", "contre", "neutral"])
def test_validate_side_refuses_anything_outside_the_closed_set(value: str):
    with pytest.raises(EvidenceSideError):
        validate_side(value)
