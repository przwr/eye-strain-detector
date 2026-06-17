"""PERCLOS tests."""
from app.core.perclos import PerclosTracker


def test_half_closed():
    p = PerclosTracker(window_sec=60)
    t = 0.0
    for i in range(10):
        p.update(eye_closed=(i % 2 == 0), ts=t)
        t += 1.0
    assert abs(p.value(ts=9.0) - 0.5) < 1e-6


def test_window_prunes_old_samples():
    p = PerclosTracker(window_sec=5)
    p.update(eye_closed=True, ts=0.0)
    p.update(eye_closed=False, ts=10.0)  # old sample pruned
    assert p.value(ts=10.0) == 0.0
