# Azure Deployment Guide — Project CV-10 Image Segmentation Tool

---

## Azure Services for Image Segmentation

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Vision — Background Removal** | Remove or segment image background — pixel-level foreground extraction  | When you need background/foreground segmentation   |
| **Azure Machine Learning**           | Deploy YOLOv8-seg or SAM as managed endpoint on GPU compute                  | When you need pixel-level instance segmentation    |
| **Azure Custom Vision**              | Train custom object segmentation model via UI                                | When you need domain-specific segmentation         |

> For pixel-level instance segmentation, **Azure Machine Learning with YOLOv8-seg or SAM** is the recommended managed option.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and segmentation mask results                      |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track segmentation latency, segment counts, request volume           |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure ML Managed Endpoint          │
│ CV Service :8001  │    │ YOLOv8-seg or SAM                  │
│ YOLOv8-seg        │    │ Managed pixel-level segmentation   │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-img-segmentation --location uksouth
az extension add --name containerapp --upgrade
az extension add --name ml --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-img-segmentation --name imgsegacr --sku Basic --admin-enabled true
az acr login --name imgsegacr
ACR=imgsegacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name imgseg-env --resource-group rg-img-segmentation --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-img-segmentation \
  --environment imgseg-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-img-segmentation \
  --environment imgseg-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure AI Vision Background Removal

```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import base64

client = ImageAnalysisClient(
    endpoint=os.getenv("AZURE_VISION_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_VISION_KEY"))
)

def segment_image(image_bytes: bytes) -> dict:
    # Background removal (foreground segmentation)
    result = client.segment(image_data=image_bytes, mode="backgroundRemoval")
    mask_b64 = base64.b64encode(result).decode() if result else ""
    # Also get object detection for segment labels
    analysis = client.analyze(image_data=image_bytes, visual_features=[VisualFeatures.OBJECTS])
    segments = []
    if analysis.objects:
        for obj in analysis.objects.list:
            segments.append({
                "class": obj.tags[0].name if obj.tags else "object",
                "confidence": round(obj.tags[0].confidence * 100, 2) if obj.tags else 0
            })
    return {"segments": segments, "mask_image": mask_b64, "total_segments": len(segments)}
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure AI Vision          | S1 tier   | Pay per call      |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–25/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-img-segmentation --yes --no-wait
```
