"""Runtime CNN eye-state inference (ONNX + onnxruntime).

Loads the MobileNetV2 model trained in Phase 2 (eye_state_cnn.onnx), crops an eye
region from the MediaPipe landmarks, resizes to 96x96, and returns P(open) in [0,1].
Preprocessing (mobilenet preprocess_input) is baked into the ONNX graph, so we feed
raw 0-255 RGB pixels.

If the model file is missing or onnxruntime fails to load it, `available` is False
and the detector falls back to EAR-only -- the app still runs.
"""
import os

import cv2
import numpy as np

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "models", "eye_state_cnn.onnx")
INPUT_SIZE = 96  # must match the Phase 2 v2 model

# Landmark indices bounding each eye (corners + lids) for cropping the eye box.
LEFT_EYE_BOX = [33, 133, 160, 158, 153, 144, 145, 153]
RIGHT_EYE_BOX = [362, 263, 385, 387, 373, 380, 374, 386]


class EyeStateClassifier:
    def __init__(self, model_path: str = _DEFAULT_PATH) -> None:
        self.available = False
        self._session = None
        self._input_name = None
        try:
            import onnxruntime as ort

            if os.path.exists(model_path):
                self._session = ort.InferenceSession(
                    model_path, providers=["CPUExecutionProvider"]
                )
                self._input_name = self._session.get_inputs()[0].name
                self.available = True
                print(f"[INFO] Eye-state CNN loaded ({os.path.basename(model_path)}).")
            else:
                print(f"[WARN] Eye-state model not found at {model_path} -- EAR-only mode.")
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] Could not load eye-state CNN ({e}) -- EAR-only mode.")

    def _crop_eye(self, frame_rgb, landmarks, indices, w: int, h: int):
        xs = [landmarks[i].x * w for i in indices]
        ys = [landmarks[i].y * h for i in indices]
        x1, x2 = int(min(xs)), int(max(xs))
        y1, y2 = int(min(ys)), int(max(ys))
        # pad the box ~30% so the whole eye + lid is included
        pad_x = int((x2 - x1) * 0.3) + 2
        pad_y = int((y2 - y1) * 0.6) + 2
        x1 = max(0, x1 - pad_x); x2 = min(w, x2 + pad_x)
        y1 = max(0, y1 - pad_y); y2 = min(h, y2 + pad_y)
        if x2 <= x1 or y2 <= y1:
            return None
        return frame_rgb[y1:y2, x1:x2]

    def predict_open_prob(self, frame_rgb, landmarks, w: int, h: int) -> float | None:
        """Average P(open) across both eyes. Returns None if unavailable.

        Both eye crops are batched into a single inference call to stay fast on CPU.
        """
        if not self.available:
            return None
        crops = []
        for idx in (LEFT_EYE_BOX, RIGHT_EYE_BOX):
            crop = self._crop_eye(frame_rgb, landmarks, idx, w, h)
            if crop is None or crop.size == 0:
                continue
            crops.append(cv2.resize(crop, (INPUT_SIZE, INPUT_SIZE)).astype(np.float32))
        if not crops:
            return None
        batch = np.stack(crops, axis=0)  # (n_eyes, 96, 96, 3)
        out = self._session.run(None, {self._input_name: batch})
        probs = np.ravel(out[0])
        return float(np.mean(probs))
