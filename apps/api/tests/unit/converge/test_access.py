from uuid import UUID

import pytest

from src.modules.converge.domain.access import can_read_map, can_write_map
from src.modules.converge.domain.clusters import ClusterTitleError, validate_cluster_title

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
OWNER = UUID("00000000-0000-0000-0000-000000000041")
PARTICIPANT = UUID("00000000-0000-0000-0000-000000000042")
UNINVOLVED = UUID("00000000-0000-0000-0000-000000000043")


def test_member_reads_the_map():
    assert can_read_map(WORKSPACE, frozenset({WORKSPACE})) is True


def test_membership_elsewhere_does_not_grant_a_read():
    assert can_read_map(WORKSPACE, frozenset({OTHER_WORKSPACE})) is False


def test_non_member_cannot_read_the_map():
    assert can_read_map(WORKSPACE, frozenset()) is False


def test_owner_can_write_the_map():
    assert can_write_map(OWNER, frozenset({OWNER}), OWNER) is True


def test_participant_can_write_the_map():
    assert can_write_map(OWNER, frozenset({OWNER, PARTICIPANT}), PARTICIPANT) is True


def test_uninvolved_member_cannot_write_the_map():
    assert can_write_map(OWNER, frozenset({OWNER}), UNINVOLVED) is False


def test_validate_cluster_title_trims_and_keeps_content():
    assert validate_cluster_title("  Open questions  ") == "Open questions"


@pytest.mark.parametrize("value", ["", "   "])
def test_validate_cluster_title_refuses_blank_values(value: str):
    with pytest.raises(ClusterTitleError):
        validate_cluster_title(value)
