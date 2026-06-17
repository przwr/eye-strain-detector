# eye-strain-detector
# Iris — Digital Eye Strain Monitoring System
 
A real-time desktop application that monitors digital eye strain through your webcam.
It tracks blink rate, eye-closure (PERCLOS), and screen proximity, fuses a trained CNN
with geometric eye analysis for robust blink detection, computes a live strain index,
and alerts you to take breaks (the 20-20-20 rule) — with a web dashboard and session history.
 
Built as an AI/ML capstone project. It extends a baseline EAR-only blink counter into a
full computer-vision + machine-learning + full-stack system.
 
---
 
## Why this exists
 
Baseline webcam eye-strain tools count blinks using only the Eye Aspect Ratio (EAR) — a
geometric formula that is brittle under glasses, poor lighting, and head tilts, and they
never compute an actual *strain* signal. This project addresses both gaps:
 
- **A trained CNN** (MobileNetV2 on the MRL Eye Dataset, **96.57% test accuracy**) is
  fused with EAR so a blink registers only when both the geometry and the model agree —
  removing false blinks that EAR alone produces.
- **Real strain logic** the baseline lacks: blinks-per-minute (the medical signal),
  PERCLOS (fatigue), continuous screen-time, and proximity → a Low/Medium/High strain index.
- **Out-of-window alerts**: an audible beep and a desktop notification that reach you even
  when the app is in the background.
- **Persistence + dashboard**: SQLite logging and a React dashboard with live and historical views.
---
 
## Key features
 
- Real-time face landmark tracking (MediaPipe, 468 points)
- EAR + CNN **fused** eye-state detection (robust to glasses / lighting)
- Personal calibration (per-user blink threshold)
- Blinks-per-minute, PERCLOS, screen-time, and proximity tracking
- Composite strain index with human-readable reasons
- 20-20-20 break alerts: beep + desktop notification (focus-independent)
- FastAPI backend streaming live metrics + annotated video over WebSocket
- React + TypeScript dashboard with a live "iris" strain gauge and blink-rate chart
- SQLite session logging and a history view
---
 
## Architecture
 
```
Webcam → Python CV + ML engine → FastAPI (WebSocket + REST) → SQLite + React dashboard
              │
              ├── MediaPipe 468 landmarks + EAR
              ├── CNN eye-state classifier (ONNX, the trained model)
              └── Strain scorer (blink-rate + PERCLOS + proximity)
```
 
The CV/ML engine is framework-agnostic: the same code runs standalone in an OpenCV window
(`run_local.py`) and inside the FastAPI service. Because the webcam is local hardware, the
backend runs on the user's machine (localhost); the browser receives the annotated video
stream and never accesses the camera directly.
 
---
 
## Machine learning
 
| | |
|---|---|
| **Task** | Binary eye-state classification (open vs closed) |
| **Dataset** | MRL Eye Dataset — ~84,898 labelled eye images |
| **Model** | MobileNetV2 (transfer learning), 96×96 RGB input |
| **Test accuracy** | **96.57%** |
| **Runtime** | ONNX via onnxruntime (CPU, real-time) |
| **Fusion** | Eye = closed only when EAR < threshold AND CNN P(open) < 0.5 |
 
Training is reproducible via the Colab notebook in `ml/` (`eye_state_training_v2.ipynb`):
download dataset → split → train → evaluate (accuracy, precision/recall/F1, confusion
matrix) → export to ONNX.
 
---
 
## Tech stack
 
**CV / ML:** Python, OpenCV, MediaPipe, TensorFlow/Keras (training), ONNX, onnxruntime
**Backend:** FastAPI, Uvicorn, SQLAlchemy, SQLite, WebSockets
**Frontend:** React, TypeScript, Vite, Recharts
**Alerts:** winsound / plyer
 
---
 
## Project structure
 
```
eye-strain-detector/
├── backend/
│   ├── app/
│   │   ├── core/        engine: landmarks, EAR, blink, PERCLOS, proximity,
│   │   │                calibration, strain, alerts, detector
│   │   ├── ml/          ONNX inference wrapper + trained model
│   │   ├── api/         REST routes + WebSocket
│   │   ├── db/          SQLite models + queries
│   │   └── services/    camera loop / session manager
│   ├── run_local.py     standalone OpenCV-window mode
│   └── requirements.txt
├── ml/                  Colab training notebook + pipeline
├── frontend/            React + Vite + TypeScript dashboard
└── docs/                report, screenshots, confusion matrix
```
 
---
 
## Setup
 
Run the **backend** and **frontend** in two terminals. (Windows shown; on macOS use
`source .venv/bin/activate` and `python3`.)
 
### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # serves http://localhost:8000
```
 
### Frontend
```bash
cd frontend
npm install
npm run dev                      # opens http://localhost:5173
```
 
Open the dashboard, click **Start monitoring**, then **Calibrate** (hold eyes open ~3s).
 
### Standalone mode (no web UI)
```bash
cd backend
python run_local.py             # C = calibrate, ESC = quit
```
 
> Requires Python 3.9–3.12 (MediaPipe does not support 3.13+). Only one process can use
> the webcam at a time.
 
---
 
## Results
 
- Eye-state CNN: **96.57%** test accuracy on held-out MRL data.
- Fused detection eliminates EAR false positives from head tilts and glasses glare.
- Real-time performance maintained on CPU via batched ONNX inference.
(Add screenshots of the dashboard and the confusion matrix to `docs/`.)
 
---
 
## Future enhancements
 
- Mobile companion app
- Posture detection (slouching / distance over time)
- Multi-user profiles with per-user baselines
- Cloud sync and cross-device history
- Low-light environment detection (poor lighting worsens strain)
- OS "do not disturb" / focus-mode integration
- Drowsiness vs strain distinction via temporal modelling
---
 
## License
 
MIT — see [LICENSE](LICENSE).
