import pytest

from src.modules.decisions.domain.triggers import (
    TRIGGER_DIRECTIONS,
    TriggerShapeError,
    validate_triggers,
)


def test_directions_are_above_and_below():
    assert TRIGGER_DIRECTIONS == frozenset({"above", "below"})


def test_absent_triggers_are_allowed():
    assert validate_triggers(None) == []
    assert validate_triggers([]) == []


def test_metric_only_trigger_is_allowed():
    assert validate_triggers([{"metric": "CTR"}]) == [
        {"metric": "CTR", "direction": None, "threshold": None, "note": None}
    ]


def test_full_trigger_round_trips():
    assert validate_triggers(
        [
            {
                "metric": "  CTR  ",
                "direction": "above",
                "threshold": " 2.5% ",
                "note": "campaign B becomes preferable",
            }
        ]
    ) == [
        {
            "metric": "CTR",
            "direction": "above",
            "threshold": "2.5%",
            "note": "campaign B becomes preferable",
        }
    ]


@pytest.mark.parametrize("metric", ["", "   "])
def test_trigger_without_a_metric_is_refused(metric: str):
    with pytest.raises(TriggerShapeError):
        validate_triggers([{"metric": metric}])


def test_trigger_without_the_metric_key_is_refused():
    with pytest.raises(TriggerShapeError):
        validate_triggers([{"threshold": "2.5%"}])


def test_unknown_direction_is_refused():
    with pytest.raises(TriggerShapeError):
        validate_triggers([{"metric": "CTR", "direction": "sideways"}])


@pytest.mark.parametrize("direction", ["above", "below"])
def test_both_declared_directions_are_accepted(direction: str):
    assert (
        validate_triggers([{"metric": "CTR", "direction": direction}])[0]["direction"] == direction
    )


def test_blank_threshold_is_refused():
    with pytest.raises(TriggerShapeError):
        validate_triggers([{"metric": "CTR", "threshold": "  "}])


def test_a_trigger_that_is_not_an_object_is_refused():
    with pytest.raises(TriggerShapeError):
        validate_triggers(["CTR"])
