from uuid import UUID

from src.modules.branches.domain.mapping import is_mappable

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
IDEA = UUID("00000000-0000-0000-0000-000000000021")


def test_workspace_idea_without_a_branch_is_mappable():
    assert is_mappable(workspace_id=WORKSPACE, source_idea_id=None) is True


def test_public_idea_without_a_workspace_is_not_mappable():
    assert is_mappable(workspace_id=None, source_idea_id=None) is False


def test_already_mapped_idea_is_skipped():
    assert is_mappable(workspace_id=WORKSPACE, source_idea_id=IDEA) is False


def test_public_and_mapped_idea_is_not_mappable():
    assert is_mappable(workspace_id=None, source_idea_id=IDEA) is False
