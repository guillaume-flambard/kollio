import pytest

from src.modules.ideas.domain.team import (
    BUSINESS_FUNCTIONS,
    DEFAULT_PARTICIPATION,
    GRANTABLE_PARTICIPATIONS,
    LEGACY_ROLE_TO_FUNCTION,
    PARTICIPATION_ROLES,
    TeamAuthorizationError,
    TeamRuleError,
    decide_addition,
    decide_application,
    decide_departure,
    validate_function,
    validate_grantable_participation,
)


def test_the_two_axes_are_closed_lists():
    assert PARTICIPATION_ROLES == frozenset({"owner", "decision_maker", "contributor", "observer"})
    assert len(BUSINESS_FUNCTIONS) == 12
    assert GRANTABLE_PARTICIPATIONS == PARTICIPATION_ROLES - {"owner"}
    assert DEFAULT_PARTICIPATION == "contributor"


def test_the_legacy_craft_roles_map_onto_the_function_axis():
    assert set(LEGACY_ROLE_TO_FUNCTION) == {
        "designer",
        "dev",
        "commercial",
        "growth",
        "data",
        "product",
        "owner",
    }
    assert set(LEGACY_ROLE_TO_FUNCTION.values()) <= BUSINESS_FUNCTIONS


def test_an_unknown_function_is_refused():
    with pytest.raises(TeamRuleError):
        validate_function("dev")


def test_the_owner_participation_cannot_be_granted():
    with pytest.raises(TeamRuleError):
        validate_grantable_participation("owner")


def test_a_member_applies_with_a_function_and_a_note():
    decision = decide_application(
        actor_is_owner=False,
        actor_is_member=True,
        function="engineering",
        note=" Ten years of frontend. ",
        already_pending=False,
    )
    assert decision.function == "engineering"
    assert decision.note == " Ten years of frontend. "


def test_the_owner_cannot_apply_to_their_own_initiative():
    with pytest.raises(TeamAuthorizationError):
        decide_application(
            actor_is_owner=True,
            actor_is_member=True,
            function="engineering",
            note="I made it.",
            already_pending=False,
        )


def test_an_outsider_cannot_apply():
    with pytest.raises(TeamAuthorizationError):
        decide_application(
            actor_is_owner=False,
            actor_is_member=False,
            function="engineering",
            note="Sneak in.",
            already_pending=False,
        )


def test_a_second_pending_application_is_refused():
    with pytest.raises(TeamRuleError):
        decide_application(
            actor_is_owner=False,
            actor_is_member=True,
            function="engineering",
            note="Again.",
            already_pending=True,
        )


def test_the_owner_adds_a_workspace_member_with_both_axes():
    decision = decide_addition(
        actor_is_owner=True,
        target_is_workspace_member=True,
        participation="decision_maker",
        function="finance",
    )
    assert decision.participation == "decision_maker"
    assert decision.function == "finance"


def test_only_the_owner_adds_a_participant():
    with pytest.raises(TeamAuthorizationError):
        decide_addition(
            actor_is_owner=False,
            target_is_workspace_member=True,
            participation="contributor",
            function="finance",
        )


def test_only_workspace_members_can_be_added():
    with pytest.raises(TeamRuleError):
        decide_addition(
            actor_is_owner=True,
            target_is_workspace_member=False,
            participation="contributor",
            function="finance",
        )


def test_a_departure_is_recorded():
    assert decide_departure(actor_is_owner=False, actor_is_member=True).record is True


def test_the_owner_cannot_be_removed_from_their_own_initiative():
    with pytest.raises(TeamAuthorizationError):
        decide_departure(actor_is_owner=True, actor_is_member=False)
