from uuid import UUID

from src.modules.decision_spaces.domain.access import (
    can_manage_participants,
    can_read_space,
    can_remove_participant,
    can_transition_space,
)

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
OWNER = UUID("00000000-0000-0000-0000-000000000011")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000012")
UNINVOLVED_MEMBER = UUID("00000000-0000-0000-0000-000000000013")


def test_member_can_read_space():
    assert can_read_space(WORKSPACE, frozenset({WORKSPACE})) is True


def test_membership_in_another_workspace_does_not_grant_a_read():
    assert can_read_space(WORKSPACE, frozenset({OTHER_WORKSPACE})) is False


def test_non_member_cannot_read_space():
    assert can_read_space(WORKSPACE, frozenset()) is False


def test_owner_can_transition_space():
    assert can_transition_space(OWNER, frozenset({OWNER}), OWNER) is True


def test_participant_can_transition_space():
    assert can_transition_space(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_uninvolved_member_cannot_transition_space():
    assert can_transition_space(OWNER, frozenset({OWNER}), UNINVOLVED_MEMBER) is False


def test_owner_can_manage_participants():
    assert can_manage_participants(OWNER, OWNER) is True


def test_participant_who_is_not_owner_cannot_manage_participants():
    assert can_manage_participants(OWNER, PARTICIPANT) is False


def test_uninvolved_member_cannot_manage_participants():
    assert can_manage_participants(OWNER, UNINVOLVED_MEMBER) is False


def test_owner_cannot_be_removed_from_their_own_space():
    assert can_remove_participant(OWNER, OWNER) is False


def test_owner_can_remove_another_participant():
    assert can_remove_participant(OWNER, PARTICIPANT) is True
