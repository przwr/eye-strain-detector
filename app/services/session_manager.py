"""Owns the webcam capture loop in a background thread.

Runs each frame through EyeStrainDetector, keeps the latest metrics + annotated
JPEG for WebSocket clients to read, and persists ~1 sample/sec to SQLite. The
detector is imported lazily so the web app can load even where camera libraries
aren't installed -- it only fails when you actually start a session.
"""
import base64
import threading
import time


class SessionManager:
    def __init__(self) -> None:
        self._detector = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._latest: dict | None = None
        self._session_id: int | None = None
        self._last_sample = 0.0
        self._error: str | None = None
        self._glasses = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def session_id(self) -> int | None:
        return self._session_id

    def start(self, camera_index: int = 0) -> int:
        if self._running:
            return self._session_id
        from app.core.detector import EyeStrainDetector  # lazy
        from app.db import crud
        from app.db.database import SessionLocal

        self._error = None
        self._detector = EyeStrainDetector(camera_index=camera_index)
        self._detector.glasses_mode = self._glasses
        db = SessionLocal()
        try:
            self._session_id = crud.create_session(db).id
        finally:
            db.close()
        self._running = True
        self._thread = threading.Thread(target=self._loop, args=(camera_index,), daemon=True)
        self._thread.start()
        return self._session_id

    def calibrate(self) -> None:
        if self._detector:
            self._detector.start_calibration()

    @property
    def glasses(self) -> bool:
        return self._glasses

    def set_glasses(self, enabled: bool) -> None:
        # tinted lenses defeat the blink CNN; flag lives on the manager so it
        # survives monitoring restarts
        self._glasses = bool(enabled)
        if self._detector:
            self._detector.glasses_mode = self._glasses

    def stop(self) -> int | None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        self._thread = None
        sid = self._session_id
        if sid is not None:
            from app.db import crud
            from app.db.database import SessionLocal
            db = SessionLocal()
            try:
                crud.end_session(db, sid)
            finally:
                db.close()
        self._session_id = None
        self._detector = None
        with self._lock:
            self._latest = None
        return sid

    def _loop(self, camera_index: int) -> None:
        import cv2
        from app.db import crud
        from app.db.database import SessionLocal

        cap = cv2.VideoCapture(camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            self._error = "Could not open camera."
            self._running = False
            crud.end_session(db, self._session_id)
            self._session_id = None
            return
        try:
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    continue
                frame = cv2.flip(frame, 1)
                m = self._detector.process_frame(frame)
                self._detector.alerts.update(
                    proximity=m.proximity, strain=m.strain, face_detected=m.face_detected)
                self._detector._draw_hud(frame, m)
                ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                payload = m.to_dict()
                payload["frame"] = base64.b64encode(buf).decode("ascii") if ok else None
                payload["session_id"] = self._session_id
                payload["ts"] = time.time()
                with self._lock:
                    self._latest = payload
                if time.time() - self._last_sample >= 1.0:
                    self._last_sample = time.time()
                    db = SessionLocal()
                    try:
                        crud.add_sample(db, self._session_id, m, time.time())
                    finally:
                        db.close()
        finally:
            cap.release()
            if self._detector:
                self._detector.landmarks.close()

    def get_latest(self) -> dict | None:
        with self._lock:
            return self._latest


manager = SessionManager()
