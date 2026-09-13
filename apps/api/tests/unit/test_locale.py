import pytest

from src.platform.locale import UnsupportedLocaleError, language_name, resolve_locale


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


@pytest.mark.parametrize(("locale", "expected"), [("fr", "French"), ("en", "English")])
def test_supported_locales_resolve_to_a_language_name(locale, expected):
    assert language_name(locale) == expected


def test_unsupported_locale_fails_deterministically():
    with pytest.raises(UnsupportedLocaleError, match="de"):
        language_name("de")
