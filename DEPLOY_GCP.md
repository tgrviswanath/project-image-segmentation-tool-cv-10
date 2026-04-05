# GCP Deployment Guide — Project CV-10 Image Segmentation Tool

---

## GCP Services for Image Segmentation

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Vision API**                 | Detect objects with bounding boxes — use as segmentation approximation       | When pixel-level masks are not required            |
| **Vertex AI**                        | Deploy YOLOv8-seg or SAM as managed endpoint on GPU                          | When you need pixel-level instance segmentation    |
| **Vertex AI AutoML Vision**          | Train custom segmentation model on your labelled dataset                     | When you need domain-specific segmentation         |

> For pixel-level instance segmentation, **Vertex AI with YOLOv8-seg or SAM** is the recommended managed option.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and segmentation mask results                       |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track segmentation latency, segment counts, request volume                |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Vertex AI Endpoint                 │
│ CV Service :8001  │    │ YOLOv8-seg or SAM                  │
│ YOLOv8-seg        │    │ Managed pixel-level segmentation   │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create imgseg-cv-project --name="Image Segmentation"
gcloud config set project imgseg-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com vision.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create imgseg-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/imgseg-cv-project/imgseg-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Vertex AI Endpoint with YOLOv8-seg

```python
from google.cloud import aiplatform
import base64, json

aiplatform.init(project="imgseg-cv-project", location="europe-west2")
endpoint = aiplatform.Endpoint("projects/imgseg-cv-project/locations/europe-west2/endpoints/<endpoint-id>")

def segment_image(image_bytes: bytes) -> dict:
    instances = [{"image": base64.b64encode(image_bytes).decode()}]
    prediction = endpoint.predict(instances=instances)
    result = prediction.predictions[0]
    return {
        "segments": result.get("segments", []),
        "mask_image": result.get("mask_image", ""),
        "total_segments": len(result.get("segments", []))
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Vertex AI Endpoint         | Pay per node hour     | ~$0.38/hour        |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$13–20/month + endpoint cost** |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete imgseg-repo --location=$GCP_REGION --quiet
gcloud projects delete imgseg-cv-project
```
