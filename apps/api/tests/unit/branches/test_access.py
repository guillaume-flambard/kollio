from uuid import UUID

from src.modules.branches.domain.access import can_read_branch, can_write_branch

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
CREATOR = UUID("00000000-0000-0000-0000-000000000031")
MEMBER = UUID("00000000-0000-0000-0000-000000000032")
OWNER = UUID("00000000-0000-0000-0000-000000000033")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000034")


def test_creator_reads_their_private_branch():
    assert (
        can_read_branch(
            visibility="private",
            workspace_id=WORKSPACE,
            memberships=frozenset({WORKSPACE}),
            creator_id=CREATOR,
            actor_id=CREATOR,
        )
        is True
    )


def test_other_member_cannot_read_a_private_branch():
    assert (
        can_read_branch(
            visibility="private",
            workspace_id=WORKSPACE,
            memberships=frozenset({WORKSPACE}),
            creator_id=CREATOR,
            actor_id=MEMBER,
        )
        is False
    )


def test_non_member_cannot_read_a_private_branch():
    assert (
        can_read_branch(
            visibility="private",
            workspace_id=WORKSPACE,
            memberships=frozenset(),
            creator_id=CREATOR,
            actor_id=MEMBER,
        )
        is False
    )


def test_member_reads_a_shared_branch():
    assert (
        can_read_branch(
            visibility="shared",
            workspace_id=WORKSPACE,
            memberships=frozenset({WORKSPACE}),
            creator_id=CREATOR,
            actor_id=MEMBER,
        )
        is True
    )


def test_non_member_cannot_read_a_shared_branch():
    assert (
        can_read_branch(
            visibility="shared",
            workspace_id=WORKSPACE,
            memberships=frozenset({OTHER_WORKSPACE}),
            creator_id=CREATOR,
            actor_id=MEMBER,
        )
        is False
    )


def test_owner_can_write():
    assert can_write_branch(OWNER, frozenset({OWNER}), OWNER) is True


def test_participant_can_write():
    assert can_write_branch(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_uninvolved_member_cannot_write():
    assert can_write_branch(OWNER, frozenset({OWNER}), MEMBER) is False
