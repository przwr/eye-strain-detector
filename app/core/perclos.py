"""PERCLOS -- the fraction of time the eyes are closed over a rolling window.

A validated fatigue metric. Sustained high PERCLOS distinguishes drowsiness/strain
from ordinary blinking and feeds the strain score.
"""
import time
from collections import deque


class PerclosTracker:
    def __init__(self, window_sec: int = 60) -> None:
        self.window_sec = window_sec
        self._samples: deque[tuple[float, bool]] = deque()

    def _prune(self, ts: float) -> None:
        while self._samples and ts - self._samples[0][0] > self.window_sec:
            self._samples.popleft()

    def update(self, eye_closed: bool, ts: float | None = None) -> float:
        ts = time.time() if ts is None else ts
        self._samples.append((ts, bool(eye_closed)))
        self._prune(ts)
        return self.value(ts)

    def value(self, ts: float | None = None) -> float:
        ts = time.time() if ts is None else ts
        self._prune(ts)
        if not self._samples:
            return 0.0
        closed = sum(1 for _, c in self._samples if c)
        return closed / len(self._samples)
