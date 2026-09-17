from uuid import UUID

import pytest

from src.modules.challenge.domain.brief import (
    BriefError,
    BriefEvidence,
    BriefOption,
    build_brief,
)

FOR = UUID("00000000-0000-0000-0000-0000000000f1")
AGAINST = UUID("00000000-0000-0000-0000-0000000000f2")

QUESTION = "Should we raise prices by 20%?"


def _option(**overrides):
    values = {"title": "Raise prices", "proposal": "Add 20% to every plan."}
    values.update(overrides)
    return BriefOption(**values)


def test_the_brief_carries_the_question_and_the_option():
    brief = build_brief(question=QUESTION, option=_option(), evidence=[])
    assert brief.payload["question"] == QUESTION
    option = brief.payload["option"]
    assert isinstance(option, dict)
    assert option["title"] == "Raise prices"
    assert option["proposal"] == "Add 20% to every plan."


def test_a_narrative_field_that_is_present_is_carried():
    brief = build_brief(
        question=QUESTION, option=_option(mechanism="A one-time uplift."), evidence=[]
    )
    option = brief.payload["option"]
    assert isinstance(option, dict)
    assert option["mechanism"] == "A one-time uplift."


def test_a_narrative_field_that_is_absent_is_omitted():
    brief = build_brief(question=QUESTION, option=_option(), evidence=[])
    option = brief.payload["option"]
    assert isinstance(option, dict)
    assert "mechanism" not in option
    assert "success_metrics" not in option


def test_a_blank_narrative_field_is_read_as_absent():
    brief = build_brief(question=QUESTION, option=_option(risks="   ", cost=""), evidence=[])
    option = brief.payload["option"]
    assert isinstance(option, dict)
    assert "risks" not in option
    assert "cost" not in option


def test_every_narrative_field_is_carried_when_present():
    brief = build_brief(
        question=QUESTION,
        option=_option(
            mechanism="m",
            upside="u",
            cost="c",
            risks="r",
            critical_assumptions="a",
            success_metrics="s",
        ),
        evidence=[],
    )
    option = brief.payload["option"]
    assert isinstance(option, dict)
    assert set(option) == {
        "title",
        "proposal",
        "mechanism",
        "upside",
        "cost",
        "risks",
        "critical_assumptions",
        "success_metrics",
    }


def test_the_evidence_carries_both_sides_with_their_identifiers():
    brief = build_brief(
        question=QUESTION,
        option=_option(),
        evidence=[
            BriefEvidence(contribution_id=FOR, side="for", title="Retention holds", body="Note"),
            BriefEvidence(contribution_id=AGAINST, side="against", title="Churn risk"),
        ],
    )
    evidence = brief.payload["evidence"]
    assert isinstance(evidence, list)
    assert evidence[0] == {
        "contribution_id": str(FOR),
        "side": "for",
        "title": "Retention holds",
        "body": "Note",
    }
    assert evidence[1]["side"] == "against"
    assert evidence[1]["body"] is None


def test_the_citable_ids_are_the_evidence_that_was_sent():
    brief = build_brief(
        question=QUESTION,
        option=_option(),
        evidence=[BriefEvidence(contribution_id=FOR, side="for", title="One")],
    )
    assert brief.contribution_ids == frozenset({FOR})


def test_no_evidence_means_nothing_is_citable():
    brief = build_brief(question=QUESTION, option=_option(), evidence=[])
    assert brief.contribution_ids == frozenset()
    assert brief.payload["evidence"] == []


def test_the_question_is_trimmed():
    brief = build_brief(question=f"  {QUESTION}  ", option=_option(), evidence=[])
    assert brief.payload["question"] == QUESTION


@pytest.mark.parametrize("question", ["", "   "])
def test_a_blank_question_is_refused(question: str):
    with pytest.raises(BriefError):
        build_brief(question=question, option=_option(), evidence=[])
