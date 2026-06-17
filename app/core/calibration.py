"""Personal baseline calibration.

Hold eyes open ~3s; records mean open-eye EAR and sets the per-user threshold at
70% of baseline. Eliminates the false positives that fixed thresholds cause.
"""
import time

import numpy as np


class Calibrator:
    def __init__(self, duration_sec: int = 3, threshold_pct: float = 0.70) -> None:
        self.duration_sec = duration_sec
        self.threshold_pct = threshold_pct
        self.calibrating = False
        self.baseline_ear: float | None = None
        self._samples: list[float] = []
        self._start = 0.0

    def start(self) -> None:
        self.calibrating = True
        self._samples = []
        self._start = time.time()
        print("[CALIB] Keep eyes open normally ...")

    def update(self, ear: float, ts: float | None = None) -> float | None:
        ts = time.time() if ts is None else ts
        if not self.calibrating:
            return None
        self._samples.append(ear)
        if ts - self._start >= self.duration_sec:
            if self._samples:
                self.baseline_ear = float(np.mean(self._samples))
            self.calibrating = False
            print(f"[CALIB] Baseline={self.baseline_ear:.4f} Threshold={self.threshold:.4f}")
            return self.threshold
        return None

    @property
    def threshold(self) -> float | None:
        if self.baseline_ear is None:
            return None
        return self.baseline_ear * self.threshold_pct

    def remaining(self, ts: float | None = None) -> float:
        ts = time.time() if ts is None else ts
        return max(0.0, self.duration_sec - (ts - self._start))
