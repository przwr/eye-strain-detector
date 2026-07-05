"""Blink detection state machine + blinks-per-minute tracking.

A blink registers only after EAR stays below threshold for `consec_frames`
consecutive frames (noise filter). Blink timestamps are kept in a rolling window
so we can report blinks/minute -- the real medical strain signal.
"""
import time
from collections import deque


class BlinkTracker:
    def __init__(self, consec_frames: int = 3, window_sec: int = 60) -> None:
        self.consec_frames = consec_frames
        self.window_sec = window_sec
        self.blink_count = 0
        self._consec_below = 0
        self._blink_times: deque[float] = deque()

    def update(self, ear: float, threshold: float, ts: float | None = None) -> bool:
        """Feed one frame via the EAR-vs-threshold rule (EAR-only path)."""
        return self.update_closed(ear < threshold, ts)

    def update_closed(self, is_closed: bool, ts: float | None = None) -> bool:
        """Feed one frame with an already-decided closed state (fusion path).

        Returns True on the frame a blink completes.
        """
        ts = time.time() if ts is None else ts
        blinked = False
        if is_closed:
            self._consec_below += 1
        else:
            if self._consec_below >= self.consec_frames:
                self.blink_count += 1
                self._blink_times.append(ts)
                blinked = True
            self._consec_below = 0
        self._prune(ts)
        return blinked

    def _prune(self, ts: float) -> None:
        while self._blink_times and ts - self._blink_times[0] > self.window_sec:
            self._blink_times.popleft()

    def blinks_per_minute(self, ts: float | None = None) -> float:
        """Blinks in the rolling window, scaled to per-minute.

        Stabilises after the first full window (~60s); before that it is a
        running estimate.
        """
        ts = time.time() if ts is None else ts
        self._prune(ts)
        return len(self._blink_times) * (60.0 / self.window_sec)
