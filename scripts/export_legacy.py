"""Export a consistent read-only snapshot; never invoke legacy agents."""

import argparse
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path

REMOTE = r"""
import sqlite3,json,hashlib
from datetime import datetime,timezone
c=sqlite3.connect('file:/data/prospecteur.db?mode=ro',uri=True)
c.row_factory=sqlite3.Row
c.execute('BEGIN')
tables={}
for name in ['idee','occupant','fusion','correction','envoi','graine','battement']:
    tables[name]=[dict(row) for row in c.execute('SELECT * FROM '+name)]
result={'source':'prospecteur','source_timezone':'Europe/Paris',
        'exported_at':datetime.now(timezone.utc).isoformat(),'tables':tables}
print(json.dumps(result,ensure_ascii=False))
c.rollback()
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="memo-labs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = "docker exec prospecteur python -c " + shlex.quote(REMOTE)
    data = subprocess.check_output(["ssh", args.host, command])
    parsed = json.loads(data)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as target:
        target.write(data)
    print(
        json.dumps(
            {
                "sha256": hashlib.sha256(data).hexdigest(),
                "counts": {k: len(v) for k, v in parsed["tables"].items()},
            }
        )
    )
