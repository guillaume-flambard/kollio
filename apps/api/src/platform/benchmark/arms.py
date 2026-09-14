"""The three arms, as request specifications plus a runner.

A is the objection made concrete: the same question to a bare model with only
Julie's prompt. B removes the variable the client cannot argue away - it gives
the visible-intelligence model the same task but no company memory. C is full
Kollio: the visible model, the company memory, and the instruction to separate
known, assumed and unknown and to contradict. The only difference across the arms
is what the model is given; the runner and the scoring stay identical.
"""

from __future__ import annotations

from typing import Protocol

from src.platform.benchmark.data import (
    Arm,
    ArmOutput,
    BenchmarkFixture,
    CompanyContext,
    Initiative,
    context_memory,
)


class BenchmarkModel(Protocol):
    bare_model: str
    visible_model: str

    async def complete(self, *, model: str, system: str, user: str) -> str: ...


BARE_SYSTEM = "You are a helpful analyst. Answer the question directly."
NO_MEMORY_SYSTEM = (
    "Assess the initiative for competition, build cost, time to market, "
    "defensibility and acquisition. Give an overall realism score from 0 to 100 "
    "and a short rationale."
)
FULL_SYSTEM = (
    "Assess the initiative for competition, build cost, time to market, "
    "defensibility and acquisition. For each factor state whether it is known, "
    "assumed or unknown; an unknown factor names the evidence that is missing and "
    "carries no score. Score known and assumed factors and the overall realism from "
    "0 to 100. Contradict the initiative explicitly where it collides with a stated "
    "objective or constraint. Use only the supplied memory; invent nothing."
)


def _user_prompt(initiative: Initiative) -> str:
    return f"Title: {initiative.title}\nPitch: {initiative.pitch}"


def arm_request(arm: Arm, initiative: Initiative, context: CompanyContext) -> tuple[str, str, bool]:
    """Return (system, user, uses_memory) for one arm."""
    if arm == "A":
        return BARE_SYSTEM, initiative.prompt, False
    if arm == "B":
        return NO_MEMORY_SYSTEM, _user_prompt(initiative), False
    memory = context_memory(context)
    return FULL_SYSTEM, f"{_user_prompt(initiative)}\n\n{memory}", True


def model_for(arm: Arm, client: BenchmarkModel) -> str:
    return client.bare_model if arm == "A" else client.visible_model


async def run_arms(
    client: BenchmarkModel, fixture: BenchmarkFixture, initiative: Initiative
) -> list[ArmOutput]:
    outputs: list[ArmOutput] = []
    for arm in ("A", "B", "C"):
        system, user, _uses_memory = arm_request(arm, initiative, fixture.context)
        model = model_for(arm, client)
        text = await client.complete(model=model, system=system, user=user)
        outputs.append(ArmOutput(initiative_id=initiative.id, arm=arm, model=model, text=text))
    return outputs


async def run_benchmark(client: BenchmarkModel, fixture: BenchmarkFixture) -> list[ArmOutput]:
    results: list[ArmOutput] = []
    for initiative in fixture.initiatives:
        results.extend(await run_arms(client, fixture, initiative))
    return results
