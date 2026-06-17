"""Eye Aspect Ratio (EAR) computation.

EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
using 6 MediaPipe landmarks per eye. EAR drops sharply during a blink.
"""
import numpy as np

LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]


def _dist(a, b) -> float:
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))


def compute_ear(landmarks, indices, w: int, h: int) -> float:
    """Compute EAR for one eye. `landmarks` are normalised (have .x, .y)."""
    pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in indices]
    p1, p2, p3, p4, p5, p6 = pts
    horiz = _dist(p1, p4)
    if horiz < 1e-6:
        return 0.0
    return (_dist(p2, p6) + _dist(p3, p5)) / (2.0 * horiz)
