"""Comparative benchmark data: the initiatives and the arms being measured.

The claim under test (#77) is that better context plus memory plus systematic
contradiction beats a bare chat model. That must be measured on real work, not
asserted. This module is the pure data contract; the initiatives and the shared
company context live in a fixtures file so a later run can be compared against
recorded outputs without touching a provider.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Arm = Literal["A", "B", "C"]
ARMS: tuple[Arm, ...] = ("A", "B", "C")

# The seven blind dimensions the rater scores, 1 (weak) to 5 (strong).
DIMENSIONS: tuple[str, ...] = (
    "relevance",
    "depth",
    "novelty",
    "willingness_to_challenge",
    "company_knowledge",
    "actionability",
    "trust",
)

# The dimensions where memory is supposed to win. A product that cannot beat a
# bare model on these has not earned the claim.
DIFFERENTIATORS: frozenset[str] = frozenset(
    {"company_knowledge", "willingness_to_challenge", "trust"}
)


@dataclass(frozen=True)
class Initiative:
    id: str
    prompt: str
    title: str
    pitch: str


@dataclass(frozen=True)
class CompanyContext:
    profile: dict[str, object]
    objectives: list[dict[str, object]] = field(default_factory=list)
    constraints: list[dict[str, object]] = field(default_factory=list)
    learnings: list[dict[str, object]] = field(default_factory=list)


@dataclass(frozen=True)
class ArmOutput:
    initiative_id: str
    arm: Arm
    model: str
    text: str


@dataclass(frozen=True)
class BenchmarkFixture:
    context: CompanyContext
    initiatives: tuple[Initiative, ...]


def load_fixture(path: Path) -> BenchmarkFixture:
    raw = json.loads(path.read_text())
    context_raw = raw.get("company_context", {})
    context = CompanyContext(
        profile=dict(context_raw.get("profile", {})),
        objectives=list(context_raw.get("objectives", [])),
        constraints=list(context_raw.get("constraints", [])),
        learnings=list(context_raw.get("learnings", [])),
    )
    initiatives = tuple(
        Initiative(
            id=str(item["id"]),
            prompt=str(item["prompt"]),
            title=str(item["title"]),
            pitch=str(item["pitch"]),
        )
        for item in raw["initiatives"]
    )
    if not initiatives:
        raise ValueError("The benchmark fixture needs at least one initiative")
    return BenchmarkFixture(context=context, initiatives=initiatives)


def context_memory(context: CompanyContext) -> str:
    """The memory a bare model never has: the company facts, its active
    objectives and constraints, and what it already learned."""
    active_objectives = [
        str(item.get("title", ""))
        for item in context.objectives
        if item.get("state", "active") != "archived"
    ]
    active_constraints = [
        str(item.get("title", ""))
        for item in context.constraints
        if item.get("state", "active") != "archived"
    ]
    learnings = [str(item.get("text", "")) for item in context.learnings]
    parts = [
        f"Company profile: {context.profile.get('name', '')} - "
        f"{context.profile.get('description', '')}",
        "Active objectives: " + ("; ".join(active_objectives) or "none recorded"),
        "Active constraints: " + ("; ".join(active_constraints) or "none recorded"),
        "Confirmed learnings from past experiments: " + ("; ".join(learnings) or "none yet"),
    ]
    return "\n".join(parts)
