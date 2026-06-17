"""MediaPipe face-landmark wrapper.

Auto-detects the legacy `mp.solutions.face_mesh` API and falls back to the new
Tasks API (MediaPipe >= 0.10.30), auto-downloading the model if needed. Returns
the 468 normalised landmarks for the first detected face, or None.
"""
import os

os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import mediapipe as mp

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


class LandmarkDetector:
    def __init__(self) -> None:
        self._use_legacy = False
        try:
            fm = mp.solutions.face_mesh
            self._face_mesh = fm.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._use_legacy = True
            print("[INFO] Using legacy MediaPipe face_mesh API.")
        except AttributeError:
            print("[INFO] Legacy API unavailable -- using Tasks API.")
            self._init_tasks_api()

    def _init_tasks_api(self) -> None:
        import urllib.request
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python.vision import (
            FaceLandmarker,
            FaceLandmarkerOptions,
            RunningMode,
        )

        model_path = "face_landmarker.task"
        if not os.path.exists(model_path):
            print("[INFO] Downloading face_landmarker model (~6 MB) ...")
            urllib.request.urlretrieve(_MODEL_URL, model_path)
            print("[INFO] Download complete.")
        opts = FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = FaceLandmarker.create_from_options(opts)

    def detect(self, rgb_frame, frame_idx: int):
        if self._use_legacy:
            res = self._face_mesh.process(rgb_frame)
            if res.multi_face_landmarks:
                return res.multi_face_landmarks[0].landmark
            return None
        ts = int(frame_idx * (1000 / 30))
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        res = self._landmarker.detect_for_video(img, ts)
        if res.face_landmarks:
            return res.face_landmarks[0]
        return None

    def close(self) -> None:
        if self._use_legacy:
            self._face_mesh.close()
        else:
            self._landmarker.close()
