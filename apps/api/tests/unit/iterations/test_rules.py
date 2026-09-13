from uuid import UUID

import pytest

from src.modules.iterations.domain.rules import (
    AuthorizationError,
    ConflictError,
    InvalidTransitionError,
    decide_acceptance,
    decide_creation,
    decide_rejection,
    decide_rollback,
)

HEAD = UUID("10000000-0000-0000-0000-000000000001")
STALE = UUID("10000000-0000-0000-0000-000000000002")


def test_owner_can_append_to_main_at_observed_head() -> None:
    decision = decide_creation(
        is_owner=True,
        branch="main",
        expected_parent_id=HEAD,
        current_branch_head_id=HEAD,
    )

    assert decision.parent_id == HEAD
    assert decision.proposal_status is None


def test_non_owner_main_write_is_rejected() -> None:
    with pytest.raises(AuthorizationError):
        decide_creation(
            is_owner=False,
            branch="main",
            expected_parent_id=HEAD,
            current_branch_head_id=HEAD,
        )


def test_member_proposal_is_pending() -> None:
    decision = decide_creation(
        is_owner=False,
        branch="proposal/research",
        expected_parent_id=HEAD,
        current_branch_head_id=HEAD,
    )

    assert decision.parent_id == HEAD
    assert decision.proposal_status == "pending"


def test_stale_parent_is_rejected() -> None:
    with pytest.raises(ConflictError):
        decide_creation(
            is_owner=True,
            branch="main",
            expected_parent_id=STALE,
            current_branch_head_id=HEAD,
        )


def test_only_owner_can_accept_pending_proposal() -> None:
    with pytest.raises(AuthorizationError):
        decide_acceptance(
            is_owner=False,
            branch="proposal/research",
            proposal_status="pending",
            expected_main_parent_id=HEAD,
            current_main_head_id=HEAD,
        )

    decision = decide_acceptance(
        is_owner=True,
        branch="proposal/research",
        proposal_status="pending",
        expected_main_parent_id=HEAD,
        current_main_head_id=HEAD,
    )
    assert decision.parent_id == HEAD
    assert decision.proposal_status == "accepted"


def test_resolved_or_main_iteration_cannot_be_resolved_again() -> None:
    with pytest.raises(InvalidTransitionError):
        decide_acceptance(
            is_owner=True,
            branch="proposal/research",
            proposal_status="accepted",
            expected_main_parent_id=HEAD,
            current_main_head_id=HEAD,
        )
    with pytest.raises(InvalidTransitionError):
        decide_rejection(is_owner=True, branch="main", proposal_status=None)


def test_rollback_is_an_owner_main_append() -> None:
    decision = decide_rollback(
        is_owner=True,
        expected_main_parent_id=HEAD,
        current_main_head_id=HEAD,
    )
    assert decision.parent_id == HEAD
    assert decision.proposal_status is None
