import pytest

from src.modules.options.domain.fields import OptionFieldError, validate_proposal, validate_title


def test_title_is_trimmed_and_kept():
    assert validate_title("  Buy the smaller competitor  ") == "Buy the smaller competitor"


def test_proposal_is_trimmed_and_kept():
    assert validate_proposal("  Ship a narrow vertical slice  ") == "Ship a narrow vertical slice"


@pytest.mark.parametrize("value", ["", "   ", "\n\t "])
def test_blank_title_is_refused(value: str):
    with pytest.raises(OptionFieldError):
        validate_title(value)


@pytest.mark.parametrize("value", ["", "   ", "\n\t "])
def test_blank_proposal_is_refused(value: str):
    with pytest.raises(OptionFieldError):
        validate_proposal(value)
