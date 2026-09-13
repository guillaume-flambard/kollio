import pytest

from src.platform.seed_demo import demo_user_id, ensure_demo_data_allowed


def test_demo_user_ids_are_stable_and_distinct():
    assert demo_user_id("camille.l") == demo_user_id("camille.l")
    assert demo_user_id("camille.l") != demo_user_id("sofia.p")


def test_demo_seed_is_rejected_in_production():
    with pytest.raises(RuntimeError, match="disabled in production"):
        ensure_demo_data_allowed("production")
