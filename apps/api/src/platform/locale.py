import json
from pathlib import Path
from typing import Literal

Locale = Literal["fr", "en"]
MESSAGES = {
    locale: json.loads((Path(__file__).parent.parent / "locales" / f"{locale}.json").read_text())
    for locale in ("fr", "en")
}


def resolve_locale(header: str) -> Locale:
    candidates = []
    for position, item in enumerate(header.split(",")):
        parts = item.strip().split(";")
        language = parts[0].lower().split("-")[0]
        quality = 1.0
        try:
            for parameter in parts[1:]:
                if parameter.strip().startswith("q="):
                    quality = float(parameter.strip()[2:])
        except ValueError:
            continue
        if language in ("fr", "en") and 0 < quality <= 1:
            candidates.append((quality, -position, language))
    return max(candidates)[2] if candidates else "fr"
