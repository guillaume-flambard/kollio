import pytest

from src.modules.ideas.domain.team import (
    Role,
    decide_acceptance,
    decide_application,
    decide_departure,
    decide_rejection,
)


def test_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="role"):
        decide_application(
            actor_is_owner=False,
            actor_is_member=True,
            role="wizard",
            note="Magic.",
            already_pending=False,
        )


def test_owner_role_is_not_selectable():
    with pytest.raises(ValueError, match="role"):
        decide_application(
            actor_is_owner=False,
            actor_is_member=True,
            role="owner",
            note="I lead.",
            already_pending=False,
        )


def test_member_may_apply():
    decision = decide_application(
        actor_is_owner=False,
        actor_is_member=True,
        role="dev",
        note="Ten years of frontend.",
        already_pending=False,
    )
    assert decision.role == Role("dev")


def test_owner_cannot_apply():
    with pytest.raises(LookupError):
        decide_application(
            actor_is_owner=True,
            actor_is_member=True,
            role="dev",
            note="I made it.",
            already_pending=False,
        )


def test_outsider_may_not_apply():
    with pytest.raises(LookupError):
        decide_application(
            actor_is_owner=False,
            actor_is_member=False,
            role="dev",
            note="Sneak in.",
            already_pending=False,
        )


def test_empty_note_is_rejected():
    with pytest.raises(ValueError, match="note"):
        decide_application(
            actor_is_owner=False,
            actor_is_member=True,
            role="dev",
            note="   ",
            already_pending=False,
        )


def test_second_pending_application_is_rejected():
    with pytest.raises(ValueError, match="pending"):
        decide_application(
            actor_is_owner=False,
            actor_is_member=True,
            role="dev",
            note="Ten years of frontend.",
            already_pending=True,
        )


def test_only_owner_accepts():
    with pytest.raises(LookupError):
        decide_acceptance(is_owner=False, current_status="pending")


def test_only_pending_application_is_accepted():
    with pytest.raises(ValueError, match="pending"):
        decide_acceptance(is_owner=True, current_status="rejected")


def test_acceptance_records_role():
    decision = decide_acceptance(is_owner=True, current_status="pending")
    assert decision.status == "accepted"


def test_only_owner_rejects():
    with pytest.raises(LookupError):
        decide_rejection(is_owner=False, current_status="pending", rationale="Not now.")


def test_rejection_requires_rationale():
    with pytest.raises(ValueError, match="rationale"):
        decide_rejection(is_owner=True, current_status="pending", rationale="  ")


def test_rejection_records_status():
    decision = decide_rejection(is_owner=True, current_status="pending", rationale="Not now.")
    assert decision.status == "rejected"


def test_departure_is_always_recorded():
    decision = decide_departure(actor_is_owner=False, actor_is_member=True)
    assert decision.record is True


def test_only_owner_removes():
    with pytest.raises(LookupError):
        decide_departure(actor_is_owner=True, actor_is_member=False)
