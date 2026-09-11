"""Import the Logto quick-start environment block without printing secrets."""

import os
import sys
from pathlib import Path

ALLOWED_KEYS = {
    "NUXT_LOGTO_ENDPOINT",
    "NUXT_LOGTO_APP_ID",
    "NUXT_LOGTO_APP_SECRET",
    "NUXT_LOGTO_COOKIE_ENCRYPTION_KEY",
}


def parse_input(raw: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().split(" #", 1)[0]
        if key in ALLOWED_KEYS:
            values[key] = value
    if values.keys() != ALLOWED_KEYS:
        missing = sorted(ALLOWED_KEYS - values.keys())
        raise ValueError(f"Incomplete Logto environment block; missing: {', '.join(missing)}")
    if any(not value or "\n" in value or "\r" in value for value in values.values()):
        raise ValueError("Invalid Logto environment value")
    return values


def update_env(path: Path, values: dict[str, str]) -> None:
    lines = path.read_text().splitlines() if path.exists() else []
    retained = [line for line in lines if line.split("=", 1)[0] not in ALLOWED_KEYS]
    retained.extend(f"{key}='{values[key]}'" for key in sorted(ALLOWED_KEYS))
    path.write_text("\n".join(retained) + "\n")
    os.chmod(path, 0o600)


if __name__ == "__main__":
    update_env(Path(sys.argv[1]), parse_input(sys.stdin.read()))
    print("Logto configuration imported; values suppressed.")
