from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (640, 480), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.segmentor._get_model")
def test_segment_no_masks(mock_model):
    mock_m = MagicMock()
    mock_result = MagicMock()
    mock_result.masks = None
    mock_result.boxes = []
    mock_m.return_value = [mock_result]
    mock_m.names = {0: "person"}
    mock_model.return_value = mock_m

    r = client.post("/api/v1/cv/segment",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["segment_count"] == 0
    assert "annotated_image" in data
    assert "mask_image" in data


def test_unsupported_format():
    r = client.post("/api/v1/cv/segment",
        files={"file": ("test.gif", b"GIF89a", "image/gif")})
    assert r.status_code == 400


def test_empty_file():
    r = client.post("/api/v1/cv/segment",
        files={"file": ("test.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
