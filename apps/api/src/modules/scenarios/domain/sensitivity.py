from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
from uuid import UUID

SensitivityStatus = Literal["found", "beyond_declared_range", "insufficient_points"]
Travel = Literal["up", "down", "flat"]
Direction = Literal["above", "below"]


@dataclass(frozen=True)
class RunPoints:
    """One run's declared values, keyed by variable id."""

    run_id: UUID
    values: Mapping[UUID, Decimal]


@dataclass(frozen=True)
class VariableSensitivity:
    variable_id: UUID
    status: SensitivityStatus
    interval: tuple[Decimal, Decimal] | None
    crossing: Decimal | None
    crossings: int
    slope_min: Decimal | None
    slope_max: Decimal | None
    travel: Travel | None


@dataclass(frozen=True)
class SensitivityReport:
    ranked: tuple[VariableSensitivity, ...]
    incomplete_run_ids: tuple[UUID, ...]


def _criterion(metric: Decimal, threshold: Decimal, direction: Direction) -> Decimal:
    return metric - threshold if direction == "above" else threshold - metric


def _analyse(
    variable_id: UUID,
    points: list[tuple[Decimal, Decimal]],
    direction: Direction,
    threshold: Decimal,
) -> VariableSensitivity:
    if len(points) < 2:
        return VariableSensitivity(
            variable_id, "insufficient_points", None, None, 0, None, None, None
        )

    slopes = [
        (metric_b - metric_a) / (variable_b - variable_a)
        for (variable_a, metric_a), (variable_b, metric_b) in zip(points, points[1:], strict=False)
        if variable_b != variable_a
    ]

    crossings: list[tuple[tuple[Decimal, Decimal], Decimal]] = []
    for (variable_a, metric_a), (variable_b, metric_b) in zip(points, points[1:], strict=False):
        criterion_a = _criterion(metric_a, threshold, direction)
        criterion_b = _criterion(metric_b, threshold, direction)
        if (criterion_a > 0) != (criterion_b > 0):
            ratio = (Decimal(0) - criterion_a) / (criterion_b - criterion_a)
            crossing = variable_a + (variable_b - variable_a) * ratio
            crossings.append(((variable_a, variable_b), crossing))

    slope_min = min(slopes) if slopes else None
    slope_max = max(slopes) if slopes else None

    if not crossings:
        first_metric = points[0][1]
        last_metric = points[-1][1]
        if last_metric > first_metric:
            travel: Travel = "up"
        elif last_metric < first_metric:
            travel = "down"
        else:
            travel = "flat"
        return VariableSensitivity(
            variable_id,
            "beyond_declared_range",
            None,
            None,
            0,
            slope_min,
            slope_max,
            travel,
        )

    narrowest = min(crossings, key=lambda item: (item[0][1] - item[0][0], item[0][0]))
    return VariableSensitivity(
        variable_id,
        "found",
        narrowest[0],
        narrowest[1],
        len(crossings),
        slope_min,
        slope_max,
        None,
    )


def _rank_key(entry: VariableSensitivity) -> tuple[int, Decimal, str]:
    magnitudes = [abs(slope) for slope in (entry.slope_min, entry.slope_max) if slope is not None]
    if not magnitudes:
        return (1, Decimal(0), str(entry.variable_id))
    return (0, -max(magnitudes), str(entry.variable_id))


def compute_sensitivity(
    *,
    metric_variable_id: UUID,
    direction: Direction,
    threshold: Decimal,
    runs: Sequence[RunPoints],
    variable_ids: Sequence[UUID],
) -> SensitivityReport:
    """What would change the preference, from the declared points alone.

    The slope is an implied slope across declared points, not a fitted model,
    and a flip is reported as an interval: this never returns a predicted value.
    """
    incomplete_run_ids = tuple(
        sorted(
            (run.run_id for run in runs if metric_variable_id not in run.values),
            key=str,
        )
    )

    analysed: list[VariableSensitivity] = []
    for variable_id in variable_ids:
        if variable_id == metric_variable_id:
            continue
        points = sorted(
            (
                (run.values[variable_id], run.values[metric_variable_id])
                for run in runs
                if variable_id in run.values and metric_variable_id in run.values
            ),
            key=lambda pair: pair[0],
        )
        if not points:
            continue
        analysed.append(_analyse(variable_id, points, direction, threshold))

    return SensitivityReport(
        ranked=tuple(sorted(analysed, key=_rank_key)),
        incomplete_run_ids=incomplete_run_ids,
    )
