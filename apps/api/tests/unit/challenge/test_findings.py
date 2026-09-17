import pytest

from src.modules.challenge.domain.findings import (
    FindingShapeError,
    arriving_status,
    validate_detail,
)
from src.modules.challenge.domain.vocabularies import ChallengeVocabularyError


def test_detail_is_trimmed_and_kept():
    assert validate_detail("  We assume demand  ") == "We assume demand"


@pytest.mark.parametrize("value", ["", "   ", "\n\t "])
def test_blank_detail_is_refused(value: str):
    with pytest.raises(FindingShapeError):
        validate_detail(value)


def test_a_human_finding_is_confirmed_on_arrival():
    assert arriving_status("human") == "confirmed"


def test_a_machine_finding_waits_as_proposed():
    assert arriving_status("critic") == "proposed"


def test_an_unknown_origin_is_refused():
    with pytest.raises(ChallengeVocabularyError):
        arriving_status("robot")
