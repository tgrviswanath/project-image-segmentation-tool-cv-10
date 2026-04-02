# Project 10 - Image Segmentation Tool (CV)

Instance segmentation using YOLOv8-seg. Detects objects AND generates pixel-level masks with colored overlays.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/YOLOv8-seg
```

## What's Different from P06 (Object Detection)

| | P06 Object Detection | P10 Segmentation |
|---|---|---|
| Model | yolov8n.pt | yolov8n-seg.pt |
| Output | Bounding boxes | Pixel-level masks + boxes |
| Extra | — | mask_image (base64), coverage_pct per segment |

## Local Run

```bash
# Terminal 1 - CV Service
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

## Docker
```bash
docker-compose up --build
```
