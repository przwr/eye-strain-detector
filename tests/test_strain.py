"""Strain scorer tests."""
from app.core.strain import StrainScorer, StrainLevel


def test_healthy_usage_is_low():
    s = StrainScorer()
    r = s.score(blink_rate=18, perclos=0.05, screen_time_min=5, proximity="OK")
    assert r.level == StrainLevel.LOW


def test_low_blink_and_high_perclos_is_high():
    s = StrainScorer()
    r = s.score(blink_rate=2, perclos=0.6, screen_time_min=40, proximity="TOO CLOSE")
    assert r.level == StrainLevel.HIGH
    assert r.score >= 60
    assert any("blink" in reason for reason in r.reasons)


def test_break_due():
    s = StrainScorer(break_interval_min=20)
    assert s.break_due(screen_time_min=25, last_break_min=0) is True
    assert s.break_due(screen_time_min=10, last_break_min=0) is False
