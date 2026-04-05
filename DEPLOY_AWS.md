# AWS Deployment Guide — Project CV-10 Image Segmentation Tool

---

## AWS Services for Image Segmentation

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition**     | Detect objects with bounding boxes — use as segmentation approximation       | When pixel-level masks are not required            |
| **AWS SageMaker**          | Deploy YOLOv8-seg or SAM (Segment Anything Model) as managed endpoint        | When you need pixel-level segmentation at scale    |
| **Amazon Bedrock**         | Claude Vision for semantic segmentation description via prompt               | When you need AI-described segmentation regions    |

> For pixel-level instance segmentation, **AWS SageMaker with YOLOv8-seg or SAM** is the recommended managed option. SAM (Segment Anything Model) from Meta provides zero-shot segmentation.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Train and Manage Your Model

| Service                         | What it does                                                        | When to use                                           |
|---------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS SageMaker**               | Fine-tune YOLOv8-seg on custom datasets, deploy managed endpoints   | When you need domain-specific segmentation            |
| **SageMaker Managed Endpoints** | Serve your segmentation model as a REST endpoint                    | Replace cv-service with a managed inference endpoint  |

### 4. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 5. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and segmentation mask results                       |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track segmentation latency, segment counts, request volume                |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ SageMaker Endpoint                 │
│ CV Service :8001  │    │ YOLOv8-seg or SAM                  │
│ YOLOv8-seg        │    │ Managed pixel-level segmentation   │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name imgseg/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name imgseg/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/imgseg/cv-service:latest ./cv-service
docker push $ECR/imgseg/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/imgseg/backend:latest ./backend
docker push $ECR/imgseg/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name imgseg-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/imgseg/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use SageMaker with YOLOv8-seg

```python
import boto3, json, base64

sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="eu-west-2")

def segment_image(image_bytes: bytes) -> dict:
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName="yolov8-seg-endpoint",
        ContentType="application/octet-stream",
        Body=image_bytes
    )
    result = json.loads(response["Body"].read())
    return {
        "segments": result.get("segments", []),
        "mask_image": result.get("mask_image", ""),
        "total_segments": len(result.get("segments", []))
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| SageMaker (ml.m5.large)    | Per hour          | ~$0.115/hour       |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$23–32/month + endpoint cost** |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name imgseg/backend --force
aws ecr delete-repository --repository-name imgseg/cv-service --force
```
