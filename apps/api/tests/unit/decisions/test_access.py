from uuid import UUID

from src.modules.decisions.domain.access import can_commit_decision, can_read_record

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
OWNER = UUID("00000000-0000-0000-0000-000000000011")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000012")
MEMBER = UUID("00000000-0000-0000-0000-000000000013")


def test_member_can_read():
    assert can_read_record(WORKSPACE, frozenset({WORKSPACE})) is True


def test_membership_in_another_workspace_does_not_grant_a_read():
    assert can_read_record(WORKSPACE, frozenset({OTHER_WORKSPACE})) is False


def test_non_member_cannot_read():
    assert can_read_record(WORKSPACE, frozenset()) is False


def test_owner_can_commit():
    assert can_commit_decision(OWNER, frozenset({OWNER}), OWNER) is True


def test_participant_can_commit():
    assert can_commit_decision(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_uninvolved_member_cannot_commit():
    assert can_commit_decision(OWNER, frozenset({OWNER}), MEMBER) is False
