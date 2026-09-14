"""Tests for the comparative benchmark harness (#77), fully offline."""

import random

from src.platform.benchmark.arms import arm_request, run_arms
from src.platform.benchmark.blinding import build_sheet, to_document
from src.platform.benchmark.data import (
    DIMENSIONS,
    ArmOutput,
    BenchmarkFixture,
    CompanyContext,
    Initiative,
    load_fixture,
)
from src.platform.benchmark.scoring import score_rated_ratings

CONTEXT = CompanyContext(
    profile={"name": "Faktus", "description": "self-serve B2B"},
    objectives=[{"id": "objective:p", "title": "Five pilots", "state": "active"}],
    constraints=[{"id": "constraint:h", "title": "No hiring", "state": "active"}],
    learnings=[{"id": "learning:x", "text": "Offline sessions completed"}],
)
INITIATIVE = Initiative(
    id="i1",
    prompt="Should we build offline?",
    title="Offline app",
    pitch="Works no signal",
)
FIXTURE = BenchmarkFixture(context=CONTEXT, initiatives=(INITIATIVE,))


class ScriptedModel:
    bare_model = "bare-model"
    visible_model = "premium-model"

    async def complete(self, *, model: str, system: str, user: str) -> str:
        return f"{model}::{user}"


async def test_arms_differ_by_memory_and_tier() -> None:
    outputs = await run_arms(ScriptedModel(), FIXTURE, INITIATIVE)
    by_arm = {output.arm: output for output in outputs}
    assert by_arm["A"].model == "bare-model"  # objectionable claim: bare model
    assert by_arm["B"].model == "premium-model"
    assert by_arm["C"].model == "premium-model"
    assert "Five pilots" not in by_arm["A"].text  # A: only Julie's prompt
    assert "Five pilots" not in by_arm["B"].text  # B: no company memory
    assert "Five pilots" in by_arm["C"].text  # C: full Kollio memory in the prompt
    assert "Offline sessions completed" in by_arm["C"].text


def test_arm_request_marks_memory_usage() -> None:
    assert arm_request("A", INITIATIVE, CONTEXT)[2] is False
    assert arm_request("B", INITIATIVE, CONTEXT)[2] is False
    assert arm_request("C", INITIATIVE, CONTEXT)[2] is True


async def test_blind_sheet_hides_arms_and_is_reversible() -> None:
    outputs = await run_arms(ScriptedModel(), FIXTURE, INITIATIVE)
    sheet, key = build_sheet(FIXTURE, outputs, seed=7)
    document = to_document(sheet)
    for item in document["items"]:
        for entry in item["answers"]:
            assert "arm" not in entry  # the rater never sees the arm
    assert set(key["i1"].values()) == {"A", "B", "C"}

    again, key_again = build_sheet(FIXTURE, outputs, seed=7)
    assert key_again == key  # deterministic for a given seed


async def test_a_different_seed_reblinds() -> None:
    outputs = await run_arms(ScriptedModel(), FIXTURE, INITIATIVE)
    _, key_a = build_sheet(FIXTURE, outputs, seed=1)
    _, key_b = build_sheet(FIXTURE, outputs, seed=999)
    # Same set of arms, but a different position mapping (probabilistic).
    assert set(key_a["i1"].values()) == set(key_b["i1"].values()) == {"A", "B", "C"}


def _full_ratings(position_to_arm: dict[int, str], c: int, a: int) -> list[dict]:
    scores_by_arm = {"A": a, "B": 3, "C": c}
    return [
        {
            "initiative_id": "i1",
            "position": position,
            "scores": {dimension: scores_by_arm[arm] for dimension in DIMENSIONS},
        }
        for position, arm in position_to_arm.items()
    ]


async def test_verdict_wins_when_memory_pays_off() -> None:
    outputs = await run_arms(ScriptedModel(), FIXTURE, INITIATIVE)
    _, key = build_sheet(FIXTURE, outputs, seed=7)
    ratings = _full_ratings({p: a for p, a in key["i1"].items()}, c=5, a=2)
    aggr, verdict = score_rated_ratings(ratings, key)
    assert verdict.wins is True
    assert aggr.overall["C"] > aggr.overall["A"]


async def test_verdict_flags_a_product_problem_when_memory_does_not_help() -> None:
    outputs = await run_arms(ScriptedModel(), FIXTURE, INITIATIVE)
    _, key = build_sheet(FIXTURE, outputs, seed=7)
    ratings = _full_ratings({p: a for p, a in key["i1"].items()}, c=3, a=3)
    _, verdict = score_rated_ratings(ratings, key)
    assert verdict.wins is False
    assert "Product problem" in verdict.summary


def test_missing_ratings_cannot_claim_a_win() -> None:
    empty_key: dict = {"i1": {1: "C"}}
    aggr, verdict = score_rated_ratings([], empty_key)
    assert verdict.wins is False


def test_shipped_fixture_loads_with_the_company_memory() -> None:
    from src.platform.benchmark import __main__ as cli

    fixture = load_fixture(cli.DEFAULT_FIXTURES)
    assert len(fixture.initiatives) >= 10
    assert fixture.context.objectives and fixture.context.learnings


def test_blinding_is_shuffled_not_sequential() -> None:
    random.seed(0)  # sanity: shuffling actually permutes for most seeds
    outputs = [
        ArmOutput(initiative_id="i1", arm=arm, model="m", text=f"{arm} answer")
        for arm in ("A", "B", "C")
    ]
    positions = {build_sheet(FIXTURE, outputs, seed=seed)[1]["i1"][1] for seed in range(24)}
    assert len(positions) == 3  # position 1 was not always the same arm
