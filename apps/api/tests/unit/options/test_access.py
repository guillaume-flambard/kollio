from uuid import UUID

from src.modules.options.domain.access import can_read_options, can_write_options

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
OWNER = UUID("00000000-0000-0000-0000-000000000041")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000042")
UNINVOLVED = UUID("00000000-0000-0000-0000-000000000043")


def test_member_can_read_options():
    assert can_read_options(WORKSPACE, frozenset({WORKSPACE})) is True


def test_non_member_cannot_read_options():
    assert can_read_options(WORKSPACE, frozenset()) is False


def test_membership_in_another_workspace_does_not_grant_a_read():
    assert can_read_options(WORKSPACE, frozenset({OTHER_WORKSPACE})) is False


def test_owner_can_write_options():
    assert can_write_options(OWNER, frozenset({OWNER}), OWNER) is True


def test_participant_can_write_options():
    assert can_write_options(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_uninvolved_member_cannot_write_options():
    assert can_write_options(OWNER, frozenset({OWNER}), UNINVOLVED) is False
