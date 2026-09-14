"""Aggregation and the written verdict.

Each rating is a rater's per-dimension score for one anonymous position on one
initiative. De-blind with the key, average per arm and dimension, then answer the
one question the pilot makes: does full Kollio (C) clearly beat a bare model (A)?
If it does not - especially on the dimensions memory is supposed to win - the
result is a product problem, not a scoring accident, and the verdict says so.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from src.platform.benchmark.data import (
    DIFFERENTIATORS,
    DIMENSIONS,
    Arm,
)


@dataclass(frozen=True)
class Rating:
    initiative_id: str
    position: int
    scores: dict[str, int]

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> Rating:
        return cls(
            initiative_id=str(raw["initiative_id"]),
            position=int(raw["position"]),
            scores={str(k): int(v) for k, v in raw["scores"].items()},
        )


Key = dict[str, dict[int, Arm]]


@dataclass(frozen=True)
class Aggregate:
    means: dict[Arm, dict[str, float]]
    overall: dict[Arm, float]


def aggregate(ratings: list[Rating], key: Key) -> Aggregate:
    buckets: dict[tuple[Arm, str], list[int]] = defaultdict(list)
    for rating in ratings:
        arm = key.get(rating.initiative_id, {}).get(rating.position)
        if arm is None:
            continue
        for dimension, score in rating.scores.items():
            buckets[(arm, dimension)].append(score)

    means: dict[Arm, dict[str, float]] = {}
    for arm in ("A", "B", "C"):
        means[arm] = {}
        for dimension in DIMENSIONS:
            values = buckets.get((arm, dimension), [])
            means[arm][dimension] = sum(values) / len(values) if values else 0.0
    overall = {
        arm: sum(arm_means.values()) / len(arm_means) if arm_means else 0.0
        for arm, arm_means in means.items()
    }
    return Aggregate(means=means, overall=overall)


@dataclass(frozen=True)
class Verdict:
    wins: bool
    margins: dict[str, float]
    summary: str


def judge(aggr: Aggregate, *, min_margin: float = 0.5) -> Verdict:
    if "A" not in aggr.overall or "C" not in aggr.overall:
        return Verdict(False, {}, "Not enough ratings to judge: arm A or C has no scores.")

    margins = {
        dimension: aggr.means["C"][dimension] - aggr.means["A"][dimension]
        for dimension in ("company_knowledge", "willingness_to_challenge", "trust")
    }
    overall_margin = aggr.overall["C"] - aggr.overall["A"]
    wins = overall_margin >= min_margin and all(
        margins[dimension] >= min_margin for dimension in DIFFERENTIATORS
    )
    if wins:
        summary = (
            f"Full Kollio (C) clearly beats the bare model (A): overall +{overall_margin:.2f}, "
            f"company knowledge +{margins['company_knowledge']:.2f}, "
            f"challenge +{margins['willingness_to_challenge']:.2f}, "
            f"trust +{margins['trust']:.2f}."
        )
    else:
        summary = (
            f"Product problem: C does not clearly beat A. overall +{overall_margin:.2f} "
            f"(need +{min_margin}), company knowledge +{margins['company_knowledge']:.2f}, "
            f"challenge +{margins['willingness_to_challenge']:.2f}, "
            f"trust +{margins['trust']:.2f}. The memory is not paying off on screen."
        )
    return Verdict(wins, margins, summary)


def score_rated_ratings(
    raw_ratings: list[dict[str, Any]], key: Key, *, min_margin: float = 0.5
) -> tuple[Aggregate, Verdict]:
    aggr = aggregate([Rating.parse(item) for item in raw_ratings], key)
    return aggr, judge(aggr, min_margin=min_margin)
