import json
from pathlib import Path

from src.main import create_app
from src.platform.config import Settings

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[4] / "contracts/openapi.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(create_app(Settings(_env_file=None)).openapi(), indent=2) + "\n")
