from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "segment_count": 2,
    "segments": [
        {"id": 0, "label": "person", "confidence": 88.5, "x": 50, "y": 30,
         "width": 200, "height": 300, "pixel_count": 12000, "coverage_pct": 3.9, "color": [255, 56, 56]},
    ],
    "class_summary": {"person": 2},
    "image_width": 640, "image_height": 480,
    "annotated_image": "base64string",
    "mask_image": "base64string",
    "model": "yolov8n-seg.pt",
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.segment_image", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_segment_endpoint(mock_seg):
    r = client.post("/api/v1/segment",
        files={"file": ("test.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["segment_count"] == 2
    assert "mask_image" in r.json()
