from uuid import UUID

import pytest

from src.modules.experiments.domain.links import ExperimentLinkError, validate_link

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")
SPACE = UUID("00000000-0000-0000-0000-0000000000a1")
OTHER_SPACE = UUID("00000000-0000-0000-0000-0000000000a2")


def test_no_link_is_accepted():
    validate_link(
        idea_workspace_id=WORKSPACE,
        space_id=None,
        space_workspace_id=None,
        option_id=None,
        option_space_id=None,
    )


def test_space_of_the_same_workspace_is_accepted():
    validate_link(
        idea_workspace_id=WORKSPACE,
        space_id=SPACE,
        space_workspace_id=WORKSPACE,
        option_id=None,
        option_space_id=None,
    )


def test_option_inside_the_linked_space_is_accepted():
    validate_link(
        idea_workspace_id=WORKSPACE,
        space_id=SPACE,
        space_workspace_id=WORKSPACE,
        option_id=OTHER_SPACE,
        option_space_id=SPACE,
    )


def test_space_of_another_workspace_is_refused():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=WORKSPACE,
            space_id=SPACE,
            space_workspace_id=OTHER_WORKSPACE,
            option_id=None,
            option_space_id=None,
        )


def test_unknown_space_is_refused():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=WORKSPACE,
            space_id=SPACE,
            space_workspace_id=None,
            option_id=None,
            option_space_id=None,
        )


def test_option_of_another_space_is_refused():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=WORKSPACE,
            space_id=SPACE,
            space_workspace_id=WORKSPACE,
            option_id=OTHER_SPACE,
            option_space_id=OTHER_SPACE,
        )


def test_option_without_a_space_is_refused():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=WORKSPACE,
            space_id=None,
            space_workspace_id=None,
            option_id=OTHER_SPACE,
            option_space_id=SPACE,
        )


def test_unknown_option_is_refused():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=WORKSPACE,
            space_id=SPACE,
            space_workspace_id=WORKSPACE,
            option_id=OTHER_SPACE,
            option_space_id=None,
        )


def test_a_public_idea_cannot_join_a_space():
    with pytest.raises(ExperimentLinkError):
        validate_link(
            idea_workspace_id=None,
            space_id=SPACE,
            space_workspace_id=WORKSPACE,
            option_id=None,
            option_space_id=None,
        )
