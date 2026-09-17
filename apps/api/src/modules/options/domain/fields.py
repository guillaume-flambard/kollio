class OptionFieldError(ValueError):
    """Raised when an option field carries no usable content."""


def validate_title(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise OptionFieldError("An option needs a title")
    return cleaned


def validate_proposal(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise OptionFieldError("An option needs a proposal")
    return cleaned
