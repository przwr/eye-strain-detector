"""Screen-proximity estimation from face width relative to frame width."""

FACE_W_LANDMARKS = (234, 454)
DIST_THRESHOLD = 0.28


def estimate_proximity(landmarks, w: int, h: int, threshold: float = DIST_THRESHOLD) -> str:
    lx = landmarks[FACE_W_LANDMARKS[0]].x * w
    rx = landmarks[FACE_W_LANDMARKS[1]].x * w
    return "TOO CLOSE" if abs(rx - lx) / w > threshold else "OK"
