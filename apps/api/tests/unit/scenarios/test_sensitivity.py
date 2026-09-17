from decimal import Decimal
from uuid import UUID

from src.modules.scenarios.domain.sensitivity import RunPoints, compute_sensitivity

METRIC = UUID("00000000-0000-0000-0000-0000000000a1")
V = UUID("00000000-0000-0000-0000-0000000000b1")
W = UUID("00000000-0000-0000-0000-0000000000b2")
Z = UUID("00000000-0000-0000-0000-0000000000b3")
RUN_ONE = UUID("00000000-0000-0000-0000-0000000000c1")
RUN_TWO = UUID("00000000-0000-0000-0000-0000000000c2")
RUN_THREE = UUID("00000000-0000-0000-0000-0000000000c3")
RUN_INCOMPLETE = UUID("00000000-0000-0000-0000-0000000000c4")

THRESHOLD = Decimal("100")


def _run(run_id, values):
    return RunPoints(run_id=run_id, values=values)


def test_a_straddling_variable_reports_its_interval_and_crossing():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("3")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.variable_id == V
    assert found.status == "found"
    assert found.interval == (Decimal("1"), Decimal("3"))
    assert found.crossing == Decimal("2")
    assert found.crossings == 1
    assert found.slope_min == Decimal("50")
    assert found.slope_max == Decimal("50")


def test_a_variable_that_never_crosses_reports_beyond_its_range():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("90"), V: Decimal("3")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.status == "beyond_declared_range"
    assert found.interval is None
    assert found.crossing is None
    assert found.crossings == 0
    assert found.travel == "up"


def test_a_variable_whose_metric_falls_can_travel_down():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("300"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("3")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.status == "beyond_declared_range"
    assert found.travel == "down"


def test_the_below_direction_flips_the_reading():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="below",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("150"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("50"), V: Decimal("3")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.status == "found"
    assert found.interval == (Decimal("1"), Decimal("3"))
    assert found.crossing == Decimal("2")


def test_a_single_point_is_insufficient_and_not_ranked():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1"), Z: Decimal("9")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("3")}),
        ],
        variable_ids=[V, Z],
    )
    by_variable = {item.variable_id: item for item in report.ranked}
    assert by_variable[Z].status == "insufficient_points"
    assert by_variable[Z].interval is None
    assert by_variable[Z].slope_min is None
    assert {item.variable_id for item in report.ranked} == {V, Z}
    assert [item.variable_id for item in report.ranked] == [V, Z]


def test_several_crossings_report_the_narrowest_interval_and_the_count():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("2")}),
            _run(RUN_THREE, {METRIC: Decimal("50"), V: Decimal("4")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.status == "found"
    assert found.crossings == 2
    assert found.interval == (Decimal("1"), Decimal("2"))
    assert found.crossing == Decimal("1.5")
    assert found.slope_min == Decimal("-50")
    assert found.slope_max == Decimal("100")


def test_a_run_missing_the_metric_is_reported_incomplete_and_excluded():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("3")}),
            _run(RUN_INCOMPLETE, {V: Decimal("9")}),
        ],
        variable_ids=[V],
    )
    assert report.incomplete_run_ids == (RUN_INCOMPLETE,)
    found = report.ranked[0]
    assert found.interval == (Decimal("1"), Decimal("3"))


def test_variables_rank_by_absolute_implied_slope():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("1"), W: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("3"), W: Decimal("6")}),
        ],
        variable_ids=[V, W],
    )
    assert [item.variable_id for item in report.ranked] == [V, W]
    assert report.ranked[0].slope_min == Decimal("50")
    assert report.ranked[1].slope_min == Decimal("20")


def test_a_negative_slope_ranks_by_magnitude():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("150"), V: Decimal("1"), W: Decimal("1")}),
            _run(RUN_TWO, {METRIC: Decimal("50"), V: Decimal("3"), W: Decimal("2")}),
        ],
        variable_ids=[V, W],
    )
    assert [item.variable_id for item in report.ranked] == [W, V]
    assert report.ranked[0].slope_min == Decimal("-100")
    assert report.ranked[1].slope_min == Decimal("-50")


def test_a_flat_pair_does_not_break_the_slope():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[
            _run(RUN_ONE, {METRIC: Decimal("50"), V: Decimal("2")}),
            _run(RUN_TWO, {METRIC: Decimal("150"), V: Decimal("2")}),
        ],
        variable_ids=[V],
    )
    found = report.ranked[0]
    assert found.status == "found"
    assert found.interval == (Decimal("2"), Decimal("2"))
    assert found.crossing == Decimal("2")
    assert found.slope_min is None
    assert found.slope_max is None


def test_no_runs_gives_an_empty_ranking():
    report = compute_sensitivity(
        metric_variable_id=METRIC,
        direction="above",
        threshold=THRESHOLD,
        runs=[],
        variable_ids=[V],
    )
    assert report.ranked == ()
    assert report.incomplete_run_ids == ()
