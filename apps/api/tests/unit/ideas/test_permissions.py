from uuid import UUID

from src.modules.ideas.domain.permissions import can_read_idea


def test_non_member_cannot_read_workspace_idea():
    workspace = UUID("00000000-0000-0000-0000-000000000001")
    assert can_read_idea(workspace, frozenset()) is False


def test_member_can_read_own_workspace():
    workspace = UUID("00000000-0000-0000-0000-000000000001")
    assert can_read_idea(workspace, frozenset({workspace})) is True


def test_membership_in_other_workspace_does_not_grant_access():
    workspace = UUID("00000000-0000-0000-0000-000000000001")
    other = UUID("00000000-0000-0000-0000-000000000002")
    assert can_read_idea(workspace, frozenset({other})) is False
