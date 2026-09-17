import pytest

from src.modules.converge.domain.relations import (
    RELATION_TYPES,
    RelationLinkError,
    RelationTypeError,
    validate_relation_ends,
    validate_relation_type,
)


def test_types_are_the_eight_declared_ones():
    assert RELATION_TYPES == frozenset(
        {
            "SUPPORTS",
            "CONTRADICTS",
            "DUPLICATES",
            "ALTERNATIVE_TO",
            "DERIVED_FROM",
            "SUPERSEDES",
            "EVIDENCE_FOR",
            "EVIDENCE_AGAINST",
        }
    )


@pytest.mark.parametrize(
    "relation_type",
    sorted(
        [
            "SUPPORTS",
            "CONTRADICTS",
            "DUPLICATES",
            "ALTERNATIVE_TO",
            "DERIVED_FROM",
            "SUPERSEDES",
            "EVIDENCE_FOR",
            "EVIDENCE_AGAINST",
        ]
    ),
)
def test_validate_type_accepts_the_closed_set(relation_type: str):
    assert validate_relation_type(relation_type) == relation_type


@pytest.mark.parametrize("value", ["", "supports", "AGREES_WITH", "RELATED"])
def test_validate_type_refuses_anything_outside_the_closed_set(value: str):
    with pytest.raises(RelationTypeError):
        validate_relation_type(value)


def test_validate_ends_accepts_two_distinct_contributions():
    assert validate_relation_ends("aaa", "bbb") == ("aaa", "bbb")


def test_validate_ends_refuses_a_self_relation():
    with pytest.raises(RelationLinkError):
        validate_relation_ends("aaa", "aaa")
