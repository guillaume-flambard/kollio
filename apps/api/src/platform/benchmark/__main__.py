"""Comparative benchmark command line (#77).

One command walks the three arms over the fixture set, then produces a blind
scoring sheet, then turns returned ratings into a written verdict. Provider calls
are opt-in (--live) and budgeted through the same guard the evals use; without
them the command works entirely from recorded outputs, so the comparison can be
re-run against a saved set without a key. This records the runs and the sheet;
the actual scoring still needs a human rater to read each answer blind.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path

import httpx

from src.platform.benchmark.arms import run_benchmark
from src.platform.benchmark.blinding import build_sheet, to_document
from src.platform.benchmark.data import ArmOutput, load_fixture
from src.platform.benchmark.scoring import DIMENSIONS, score_rated_ratings
from src.platform.config import Settings, get_settings
from src.platform.evaluation import LiveEvaluationGuard
from src.platform.task_class import TaskClass, resolve_model

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
DEFAULT_FIXTURES = _HERE / "fixtures" / "initiatives.json"
DEFAULT_OUTPUTS = _REPO_ROOT / "artifacts" / "benchmark" / "outputs.json"
DEFAULT_SHEET = _REPO_ROOT / "artifacts" / "benchmark" / "sheet.json"


class LiteLLMBenchmarkModel:
    """A plain-text chat model for the benchmark, bare and visible tiers from the
    task-class routing (#75). Kept separate from the analysis gateway: the
    benchmark measures what the model is given, not the structured pipeline."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bare_model = settings.llm_model
        self.visible_model = resolve_model(settings, TaskClass.REASONING)

    async def complete(self, *, model: str, system: str, user: str) -> str:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 900,
        }
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key.get_secret_value()}"}
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{self.settings.llm_base_url}/chat/completions", json=payload, headers=headers
            )
            response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])


class GuardedBenchmarkModel:
    """Wraps a benchmark model so every provider call goes through the live
    evaluation budget and rate guard before a single request leaves."""

    def __init__(self, inner: LiteLLMBenchmarkModel, guard: LiveEvaluationGuard) -> None:
        self._inner = inner
        self._guard = guard
        self.bare_model = inner.bare_model
        self.visible_model = inner.visible_model

    async def complete(self, *, model: str, system: str, user: str) -> str:
        remaining = self._guard.max_cases - self._guard.attempted_cases
        await self._guard.authorize(incomplete_cases=remaining)
        return await self._inner.complete(model=model, system=system, user=user)


def _write_outputs(outputs: list[ArmOutput], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(item) for item in outputs], ensure_ascii=False, indent=2))


def _read_outputs(path: Path) -> list[ArmOutput]:
    return [
        ArmOutput(
            initiative_id=item["initiative_id"],
            arm=item["arm"],
            model=item["model"],
            text=item["text"],
        )
        for item in json.loads(path.read_text())
    ]


async def _cmd_run(args: argparse.Namespace) -> int:
    fixture = load_fixture(Path(args.fixtures))
    outputs_path = Path(args.outputs)
    if not args.live:
        if await asyncio.to_thread(outputs_path.exists):
            print(f"Recorded: {len(_read_outputs(outputs_path))} outputs at {outputs_path}")
            return 0
        print("No recorded outputs and --live not set; run with --live once.", file=sys.stderr)
        return 2
    guard = LiveEvaluationGuard.from_environment()
    model = GuardedBenchmarkModel(LiteLLMBenchmarkModel(get_settings()), guard)
    outputs = await run_benchmark(model, fixture)
    await asyncio.to_thread(_write_outputs, outputs, outputs_path)
    print(
        f"Ran {len(outputs)} outputs across {len(fixture.initiatives)} initiatives "
        f"into {outputs_path}"
    )
    return 0


def _cmd_sheet(args: argparse.Namespace) -> int:
    fixture = load_fixture(Path(args.fixtures))
    outputs_path = Path(args.outputs)
    if not outputs_path.exists():
        print(f"No outputs to score; run first ({outputs_path} missing).", file=sys.stderr)
        return 2
    outputs = _read_outputs(outputs_path)
    sheet, key = build_sheet(fixture, outputs, seed=args.seed)
    document = to_document(sheet)
    path = Path(args.sheet)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialised_key = {k: {str(p): a for p, a in v.items()} for k, v in key.items()}
    path.write_text(
        json.dumps(
            {"seed": sheet.seed, "document": document, "key": serialised_key},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"Blind sheet for {len(sheet.items)} initiatives -> {path}")
    print(f"Score each answer 1-5 on: {', '.join(DIMENSIONS)}. The rater must not open the 'key'.")
    return 0


def _cmd_score(args: argparse.Namespace) -> int:
    sheet_path = Path(args.sheet)
    if not sheet_path.exists():
        print("No sheet; run the sheet step first.", file=sys.stderr)
        return 2
    sheet_json = json.loads(sheet_path.read_text())
    key = {k: {int(p): a for p, a in v.items()} for k, v in sheet_json["key"].items()}
    ratings = json.loads(Path(args.ratings).read_text())
    aggr, verdict = score_rated_ratings(ratings, key)
    for arm in ("A", "B", "C"):
        row = ", ".join(f"{d}={aggr.means[arm][d]:.1f}" for d in DIMENSIONS)
        print(f"Arm {arm}: overall {aggr.overall[arm]:.2f} | {row}")
    print(verdict.summary)
    return 0 if verdict.wins else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="benchmark", description=__doc__)
    parser.add_argument("--fixtures", default=str(DEFAULT_FIXTURES))
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the three arms over the fixture set")
    run.add_argument("--live", action="store_true")
    run.add_argument("--outputs", default=str(DEFAULT_OUTPUTS))
    sheet = sub.add_parser("sheet", help="emit a blind scoring sheet from the outputs")
    sheet.add_argument("--outputs", default=str(DEFAULT_OUTPUTS))
    sheet.add_argument("--sheet", default=str(DEFAULT_SHEET))
    sheet.add_argument("--seed", type=int, default=7)
    score = sub.add_parser("score", help="de-blind ratings into a written verdict")
    score.add_argument("--sheet", default=str(DEFAULT_SHEET))
    score.add_argument("--ratings", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return asyncio.run(_cmd_run(args))
    if args.command == "sheet":
        return _cmd_sheet(args)
    if args.command == "score":
        return _cmd_score(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
