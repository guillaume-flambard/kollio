from uuid import UUID

from src.modules.company_context.domain.access import can_access_context

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER = UUID("00000000-0000-0000-0000-000000000002")


def test_member_can_access_context():
    assert can_access_context(WORKSPACE, frozenset({WORKSPACE})) is True


def test_outsider_cannot_access_context():
    assert can_access_context(WORKSPACE, frozenset()) is False


def test_membership_in_another_workspace_does_not_grant_access():
    assert can_access_context(WORKSPACE, frozenset({OTHER})) is False
