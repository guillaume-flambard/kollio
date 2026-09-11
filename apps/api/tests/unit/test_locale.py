import pytest

from src.platform.locale import resolve_locale


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("en;q=0.3,fr-FR;q=0.8", "fr"),
        ("en-GB", "en"),
        ("de", "fr"),
        ("en;q=0,fr;q=1", "fr"),
        ("en;q=invalid,fr", "fr"),
        ("", "fr"),
    ],
)
def test_locale_negotiation(header, expected):
    assert resolve_locale(header) == expected
