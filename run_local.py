"""Phase 1 entry point: run the engine standalone in an OpenCV window.

No FastAPI, no database -- just the core detector with a HUD. This proves the
engine works in isolation (the same engine is later wrapped by the API).

    python run_local.py        # C = calibrate, ESC = quit
"""
from app.core.detector import EyeStrainDetector


def main() -> None:
    EyeStrainDetector(camera_index=0).run_window()


if __name__ == "__main__":
    main()
