"""EAR computation tests using fake landmark objects."""
from types import SimpleNamespace
from app.core.ear import compute_ear


def _lm(coords):
    # build a dict-like list addressable by index with .x/.y in normalised units
    pts = {}
    for idx, (x, y) in coords.items():
        pts[idx] = SimpleNamespace(x=x, y=y)
    return pts


def test_open_eye_higher_than_closed():
    idx = [0, 1, 2, 3, 4, 5]
    # open: tall eye
    open_eye = _lm({0: (0.0, 0.5), 3: (1.0, 0.5),
                    1: (0.3, 0.2), 5: (0.3, 0.8),
                    2: (0.7, 0.2), 4: (0.7, 0.8)})
    # closed: flat eye
    closed_eye = _lm({0: (0.0, 0.5), 3: (1.0, 0.5),
                      1: (0.3, 0.48), 5: (0.3, 0.52),
                      2: (0.7, 0.48), 4: (0.7, 0.52)})
    ear_open = compute_ear(open_eye, idx, 100, 100)
    ear_closed = compute_ear(closed_eye, idx, 100, 100)
    assert ear_open > ear_closed
    assert ear_closed < 0.1
