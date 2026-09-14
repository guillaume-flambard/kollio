"""Blind sheet generation and scoring for the comparative benchmark.

The rater must not know which arm produced which answer, or "willingness to
challenge" and "trust" become a vote for the tool that made them. So the three
answers per initiative are shuffled into anonymous positions with a seed the
rater never sees, and the arm behind each position is kept in a separate key.
Scoring is de-blinded only at aggregation, so the verdict is honest.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from src.platform.benchmark.data import (
    ARMS,
    DIMENSIONS,
    Arm,
    ArmOutput,
    BenchmarkFixture,
)


@dataclass(frozen=True)
class SheetItem:
    initiative_id: str
    prompt: str
    entries: list[dict[str, Any]]  # [{"position": int, "text": str}], no arm label


@dataclass(frozen=True)
class ScoringSheet:
    seed: int
    items: list[SheetItem]


def build_sheet(
    fixture: BenchmarkFixture, outputs: list[ArmOutput], *, seed: int
) -> tuple[ScoringSheet, dict[str, dict[int, Arm]]]:
    by_initiative: dict[str, dict[Arm, ArmOutput]] = defaultdict(dict)
    for output in outputs:
        by_initiative[output.initiative_id][output.arm] = output

    prompts = {initiative.id: initiative.prompt for initiative in fixture.initiatives}
    sheet_items: list[SheetItem] = []
    key: dict[str, dict[int, Arm]] = {}
    for index, initiative in enumerate(fixture.initiatives):
        arms = by_initiative.get(initiative.id, {})
        present = [arm for arm in ARMS if arm in arms]
        # Deterministic per (seed, initiative index) so the sheet is reproducible
        # yet reveals nothing about which position came from which arm.
        rng = random.Random(seed * 1_000_003 + index)
        rng.shuffle(present)
        key[initiative.id] = {position: arm for position, arm in enumerate(present, start=1)}
        sheet_items.append(
            SheetItem(
                initiative_id=initiative.id,
                prompt=prompts[initiative.id],
                entries=[
                    {"position": position, "text": arms[arm].text}
                    for position, arm in key[initiative.id].items()
                ],
            )
        )
    return ScoringSheet(seed=seed, items=sheet_items), key


def to_document(sheet: ScoringSheet) -> dict[str, Any]:
    """The artifact handed to a rater: no arm labels, no seed leakage of order."""
    return {
        "dimensions": list(DIMENSIONS),
        "items": [
            {
                "initiative_id": item.initiative_id,
                "prompt": item.prompt,
                "answers": item.entries,
            }
            for item in sheet.items
        ],
    }
