import pytest

from src.modules.branches.domain.propose import (
    CONTRIBUTION_KINDS,
    CONTRIBUTION_STATUSES,
    ContributionKindError,
    ContributionProposalError,
    initial_status,
    validate_kind,
    validate_proposal_title,
)


def test_kinds_are_the_five_declared_ones():
    assert CONTRIBUTION_KINDS == frozenset({"idea", "claim", "evidence", "objection", "constraint"})


def test_statuses_are_suggested_and_confirmed():
    assert CONTRIBUTION_STATUSES == frozenset({"suggested", "confirmed"})


@pytest.mark.parametrize("kind", sorted(CONTRIBUTION_KINDS))
def test_validate_kind_accepts_the_closed_set(kind: str):
    assert validate_kind(kind) == kind


@pytest.mark.parametrize("value", ["", "fact", "IDEA", "note"])
def test_validate_kind_refuses_anything_outside_the_closed_set(value: str):
    with pytest.raises(ContributionKindError):
        validate_kind(value)


def test_validate_proposal_title_trims_and_keeps_content():
    assert validate_proposal_title("  A claim  ") == "A claim"


@pytest.mark.parametrize("value", ["", "   "])
def test_validate_proposal_title_refuses_blank_values(value: str):
    with pytest.raises(ContributionProposalError):
        validate_proposal_title(value)


def test_human_proposal_is_confirmed():
    assert initial_status(is_human=True) == "confirmed"


def test_ai_suggestion_waits_for_confirmation():
    assert initial_status(is_human=False) == "suggested"
