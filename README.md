# Project CV-10 - Image Segmentation Tool

Microservice CV system that performs instance segmentation using YOLOv8-seg. Detects objects AND generates pixel-level masks with colored overlays.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/segment                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/segment  →  calls cv-service         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  YOLOv8-seg inference → pixel masks + bounding boxes        │
│  Returns { segments[], mask_image, annotated_image }        │
└─────────────────────────────────────────────────────────────┘
```

---

## What's Different from Object Detection (CV-06)

| | CV-06 Object Detection | CV-10 Segmentation |
|---|---|---|
| Model | yolov8n.pt | yolov8n-seg.pt |
| Output | Bounding boxes only | Pixel-level masks + boxes |
| Extra | — | mask_image (base64), coverage_pct per segment |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | Ultralytics YOLOv8-seg, OpenCV, NumPy |
| Model | yolov8n-seg.pt (auto-downloaded ~7MB) |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
# YOLOv8-seg model auto-downloaded on first request (~7MB)
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Image Segmentation API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `cv-service/.env`

```
MODEL_NAME=yolov8n-seg.pt
CONFIDENCE_THRESHOLD=0.4
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-image-segmentation-tool-cv-10/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/segmentor.py    ← YOLOv8-seg inference + mask overlay
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/segment
Body:     { "image": "<base64>", "confidence": 0.4 }
Response: {
  "segments": [{ "class": "person", "confidence": 91.2, "coverage_pct": 18.5, "bounding_box": {...} }],
  "mask_image": "<base64>",
  "annotated_image": "<base64>",
  "total_segments": 3
}
```
