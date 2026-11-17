"""Blink detection state machine + blinks-per-minute tracking.

A blink registers when the eyes stay closed for `min_closed_sec` seconds of
wall time (a real blink lasts ~100-400 ms; landmark noise flickers are far
shorter). Duration-based on purpose: a frame-count rule undercounts badly at
low processing FPS (a 200 ms blink is only 2-3 frames at ~12 fps).
"""
import time
from collections import deque


class BlinkTracker:
    def __init__(self, min_closed_sec: float = 0.09, window_sec: int = 60) -> None:
        self.min_closed_sec = min_closed_sec
        self.window_sec = window_sec
        self.blink_count = 0
        self._below_since: float | None = None
        self._blink_times: deque[float] = deque()

    def update(self, ear: float, threshold: float, ts: float | None = None) -> bool:
        """Feed one frame via the EAR-vs-threshold rule (EAR-only path)."""
        return self.update_closed(ear < threshold, ts)

    def update_closed(self, is_closed: bool, ts: float | None = None) -> bool:
        """Feed one frame with an already-decided closed state.

        Returns True on the frame a blink completes.
        """
        ts = time.time() if ts is None else ts
        blinked = False
        if is_closed:
            if self._below_since is None:
                self._below_since = ts
        else:
            if self._below_since is not None:
                if ts - self._below_since >= self.min_closed_sec:
                    self.blink_count += 1
                    self._blink_times.append(ts)
                    blinked = True
                self._below_since = None
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
