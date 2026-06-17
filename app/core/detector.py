"""EyeStrainDetector -- orchestrates the per-frame pipeline.

Framework-agnostic: imports nothing from FastAPI. The SAME class runs standalone
in an OpenCV window (`run_window`, Phase 1) and inside the API service layer
(`process_frame` returns a plain metrics object for the WebSocket to broadcast).
"""
import time
from collections import deque
from dataclasses import asdict, dataclass

import cv2
import numpy as np

from app.core.alerts import AlertManager
from app.core.blink import BlinkTracker
from app.core.calibration import Calibrator
from app.core.ear import LEFT_EYE_IDX, RIGHT_EYE_IDX, compute_ear
from app.core.landmarks import LandmarkDetector
from app.core.perclos import PerclosTracker
from app.core.proximity import estimate_proximity
from app.core.strain import StrainScorer

COL_GREEN = (0, 220, 80)
COL_YELLOW = (0, 220, 220)
COL_RED = (30, 30, 220)
COL_WHITE = (240, 240, 240)
COL_DARK = (20, 20, 20)
STRAIN_COL = {"low": COL_GREEN, "medium": COL_YELLOW, "high": COL_RED}


@dataclass
class FrameMetrics:
    avg_ear: float
    threshold: float
    blink_count: int
    blink_rate: float
    perclos: float
    proximity: str
    strain: str
    strain_score: float
    screen_time_min: float
    fps: float
    face_detected: bool

    def to_dict(self) -> dict:
        return asdict(self)


class EyeStrainDetector:
    def __init__(self, camera_index: int = 0, default_threshold: float = 0.21) -> None:
        self.camera_index = camera_index
        self.default_threshold = default_threshold
        self.landmarks = LandmarkDetector()
        self.blink = BlinkTracker()
        self.perclos = PerclosTracker()
        self.calibrator = Calibrator()
        self.scorer = StrainScorer()
        self.alerts = AlertManager()
        self.ear_history: deque[float] = deque(maxlen=90)
        self._fps: deque[float] = deque(maxlen=30)
        self._frame_idx = 0
        self._start = time.time()

    @property
    def threshold(self) -> float:
        return self.calibrator.threshold or self.default_threshold

    def start_calibration(self) -> None:
        self.calibrator.start()

    def process_frame(self, frame) -> FrameMetrics:
        """Run one BGR frame through the pipeline. No UI side effects."""
        t0 = time.perf_counter()
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        lm = self.landmarks.detect(rgb, self._frame_idx)
        self._frame_idx += 1
        now = time.time()

        avg_ear = 0.0
        proximity = "NO FACE"
        face = lm is not None
        if face:
            le = compute_ear(lm, LEFT_EYE_IDX, w, h)
            re = compute_ear(lm, RIGHT_EYE_IDX, w, h)
            avg_ear = (le + re) / 2.0
            self.ear_history.append(avg_ear)
            proximity = estimate_proximity(lm, w, h)

            if self.calibrator.calibrating:
                self.calibrator.update(avg_ear, now)
            else:
                thr = self.threshold
                self.blink.update(avg_ear, thr, now)
                self.perclos.update(avg_ear < thr, now)

        screen_min = (now - self._start) / 60.0
        blink_rate = self.blink.blinks_per_minute(now)
        perclos_val = self.perclos.value(now)
        strain = self.scorer.score(
            blink_rate=blink_rate,
            perclos=perclos_val,
            screen_time_min=screen_min,
            proximity=proximity if face else "OK",
        )

        self._fps.append(time.perf_counter() - t0)
        fps = 1.0 / (sum(self._fps) / len(self._fps) + 1e-9)

        return FrameMetrics(
            avg_ear=avg_ear,
            threshold=self.threshold,
            blink_count=self.blink.blink_count,
            blink_rate=blink_rate,
            perclos=perclos_val,
            proximity=proximity,
            strain=strain.level.value,
            strain_score=strain.score,
            screen_time_min=screen_min,
            fps=fps,
            face_detected=face,
        )

    # ------------------------- standalone window mode -------------------------
    def _draw_hud(self, frame, m: FrameMetrics) -> None:
        h, w = frame.shape[:2]
        f, fb = cv2.FONT_HERSHEY_SIMPLEX, cv2.FONT_HERSHEY_DUPLEX
        ov = frame.copy()
        cv2.rectangle(ov, (0, 0), (330, 190), COL_DARK, -1)
        cv2.addWeighted(ov, 0.55, frame, 0.45, 0, frame)

        cv2.putText(frame, "EYE STRAIN DETECTOR v2", (10, 24), fb, 0.55, COL_GREEN, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Blinks    : {m.blink_count}", (10, 52), f, 0.5, COL_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Rate      : {m.blink_rate:.0f}/min", (10, 74), f, 0.5, COL_WHITE, 1, cv2.LINE_AA)
        ecol = COL_RED if m.avg_ear < m.threshold else COL_WHITE
        cv2.putText(frame, f"EAR       : {m.avg_ear:.3f} (thr {m.threshold:.3f})", (10, 96), f, 0.45, ecol, 1, cv2.LINE_AA)
        cv2.putText(frame, f"PERCLOS   : {m.perclos*100:.0f}%", (10, 118), f, 0.5, COL_WHITE, 1, cv2.LINE_AA)
        pcol = COL_RED if m.proximity == "TOO CLOSE" else COL_GREEN
        cv2.putText(frame, f"Distance  : {m.proximity}", (10, 140), f, 0.5, pcol, 1, cv2.LINE_AA)
        scol = STRAIN_COL.get(m.strain, COL_WHITE)
        cv2.putText(frame, f"STRAIN    : {m.strain.upper()} ({m.strain_score:.0f})", (10, 164), fb, 0.55, scol, 1, cv2.LINE_AA)
        cv2.putText(frame, f"FPS {m.fps:.0f}", (270, 24), f, 0.45, COL_YELLOW, 1, cv2.LINE_AA)

        if self.calibrator.calibrating:
            cv2.putText(frame, f"CALIBRATING ... {self.calibrator.remaining():.1f}s",
                        (10, h - 40), fb, 0.65, COL_YELLOW, 2, cv2.LINE_AA)
        cv2.putText(frame, "[C] Calibrate   [ESC] Quit", (10, h - 12), f, 0.4, (160, 160, 160), 1, cv2.LINE_AA)

        if m.proximity == "TOO CLOSE":
            cv2.rectangle(frame, (0, h - 50), (w, h), (0, 0, 180), -1)
            cv2.putText(frame, " MOVE BACK FROM SCREEN ", (w // 2 - 195, h - 18), fb, 0.75, COL_WHITE, 2, cv2.LINE_AA)
        if m.strain == "high":
            cv2.rectangle(frame, (0, 0), (w, 6), COL_RED, -1)
            cv2.putText(frame, "TIME FOR A 20-20-20 BREAK", (w // 2 - 170, 30), fb, 0.6, COL_RED, 2, cv2.LINE_AA)

        # EAR sparkline (top-right)
        if len(self.ear_history) > 1:
            pts = list(self.ear_history)
            mn, mx = min(pts), max(pts)
            sx, sy, sw, sh = w - 170, 10, 160, 60
            cv2.rectangle(frame, (sx, sy), (sx + sw, sy + sh), (40, 40, 40), -1)
            for i in range(1, len(pts)):
                def sc(v, _mn=mn, _mx=mx):
                    return sy + sh // 2 if _mx == _mn else int(sy + sh - (v - _mn) / (_mx - _mn) * sh)
                x1 = sx + int((i - 1) / (len(pts) - 1) * sw)
                x2 = sx + int(i / (len(pts) - 1) * sw)
                cv2.line(frame, (x1, sc(pts[i - 1])), (x2, sc(pts[i])), COL_GREEN, 1, cv2.LINE_AA)

    def run_window(self) -> None:
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        if not cap.isOpened():
            raise RuntimeError("Cannot open camera.")
        print("Started. C = Calibrate | ESC = Quit")
        cv2.namedWindow("Digital Eye Strain Detection System", cv2.WINDOW_NORMAL)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                frame = cv2.flip(frame, 1)
                metrics = self.process_frame(frame)
                self.alerts.update(proximity=metrics.proximity, strain=metrics.strain, face_detected=metrics.face_detected)
                self._draw_hud(frame, metrics)
                cv2.imshow("Digital Eye Strain Detection System", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
                if key in (ord("c"), ord("C")):
                    self.start_calibration()
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.landmarks.close()
            print("Resources released. Goodbye.")



