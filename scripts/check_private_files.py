"""Reject tracked or staged secrets, private migration artifacts and operator infrastructure."""

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath

parser = argparse.ArgumentParser()
parser.add_argument("--tracked", action="store_true")
args = parser.parse_args()
if args.tracked:
    command = ["git", "ls-files", "-z"]
else:
    command = ["git", "diff", "--cached", "--name-only", "-z"]
paths = subprocess.check_output(command).decode().split("\0")
blocked = [
    path
    for path in paths
    if path
    and (
        (PurePosixPath(path).name.startswith(".env") and PurePosixPath(path).name != ".env.example")
        or PurePosixPath(path).suffix in {".pem", ".key", ".db", ".sqlite", ".sqlite3"}
        or "prospecteur-snapshot" in path
    )
]
if blocked:
    raise SystemExit("Private files must not be committed: " + ", ".join(blocked))

secret_pattern = re.compile(
    rb"(?im)^(?:OPENAI_API_KEY|BAI_API_KEY|LITELLM_MASTER_KEY|NUXT_LOGTO_APP_SECRET)="
    rb"(?!(?:|change-me|replace-me)$).+"
)
leaks = []
for path in paths:
    candidate = Path(path)
    if not path or not candidate.is_file() or candidate.name == ".env.example":
        continue
    try:
        if secret_pattern.search(candidate.read_bytes()):
            leaks.append(path)
    except OSError:
        continue
if leaks:
    raise SystemExit("Provider credentials found in tracked content: " + ", ".join(leaks))

infrastructure_pattern = re.compile(rb"(?i)memolabs\.dev|/Users/memo\b")
host_leaks = []
for path in paths:
    candidate = Path(path)
    if not path or not candidate.is_file() or path == "scripts/check_private_files.py":
        continue
    try:
        if infrastructure_pattern.search(candidate.read_bytes()):
            host_leaks.append(path)
    except OSError:
        continue
if host_leaks:
    raise SystemExit("Operator infrastructure found in tracked content: " + ", ".join(host_leaks))
