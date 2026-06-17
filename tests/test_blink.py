"""Blink state-machine tests with synthetic EAR streams (no camera)."""
from app.core.blink import BlinkTracker


def test_single_blink_after_consecutive_low_frames():
    bt = BlinkTracker(consec_frames=3)
    thr = 0.2
    t = 0.0
    # 4 low frames then back open -> exactly one blink
    for ear in [0.30, 0.10, 0.10, 0.10, 0.10, 0.30]:
        bt.update(ear, thr, ts=t)
        t += 0.033
    assert bt.blink_count == 1


def test_short_dip_does_not_count():
    bt = BlinkTracker(consec_frames=3)
    thr = 0.2
    t = 0.0
    for ear in [0.30, 0.10, 0.10, 0.30]:  # only 2 low frames
        bt.update(ear, thr, ts=t)
        t += 0.033
    assert bt.blink_count == 0


def test_blinks_per_minute_window():
    bt = BlinkTracker(consec_frames=1, window_sec=60)
    # 10 blinks within the window
    for i in range(10):
        bt.update(0.05, 0.2, ts=i * 1.0)
        bt.update(0.30, 0.2, ts=i * 1.0 + 0.1)
    assert bt.blinks_per_minute(ts=10.0) == 10.0
