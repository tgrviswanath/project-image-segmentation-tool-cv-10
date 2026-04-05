"""
YOLOv8 instance segmentation.
- Detects objects AND generates pixel-level masks per instance
- Draws colored semi-transparent masks over each object
- Returns: segments[], class_summary{}, annotated_image (base64), mask_image (base64)
"""
import cv2
import numpy as np
from PIL import Image
import io
import base64
from app.core.config import settings

_model = None

# Distinct colors for up to 20 classes
PALETTE = [
    (255, 56, 56), (255, 157, 151), (255, 112, 31), (255, 178, 29),
    (207, 210, 49), (72, 249, 10), (146, 204, 23), (61, 219, 134),
    (26, 147, 52), (0, 212, 187), (44, 153, 168), (0, 194, 255),
    (52, 69, 147), (100, 115, 255), (0, 24, 236), (132, 56, 255),
    (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199),
]


def _get_model():
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO
            _model = YOLO(settings.YOLO_MODEL)
        except Exception as e:
            raise FileNotFoundError(f"Segmentation model unavailable: {e}")
    return _model


def _load(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _to_base64(img: np.ndarray) -> str:
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buf).decode("utf-8")


def segment(image_bytes: bytes) -> dict:
    model = _get_model()
    img = _load(image_bytes)
    h, w = img.shape[:2]

    results = model(img, conf=settings.CONFIDENCE_THRESHOLD, verbose=False)[0]

    annotated = img.copy()
    mask_overlay = np.zeros_like(img)
    segments = []
    class_summary = {}

    if results.masks is not None:
        masks = results.masks.data.cpu().numpy()   # (N, H, W)
        boxes = results.boxes

        for i, (mask, box) in enumerate(zip(masks, boxes)):
            label = model.names[int(box.cls[0])]
            conf = round(float(box.conf[0]) * 100, 1)
            color = PALETTE[i % len(PALETTE)]

            # Resize mask to image size
            mask_resized = cv2.resize(mask, (w, h))
            mask_bool = mask_resized > 0.5

            # Apply colored mask
            mask_overlay[mask_bool] = color
            annotated[mask_bool] = (
                annotated[mask_bool] * (1 - settings.MASK_ALPHA) +
                np.array(color) * settings.MASK_ALPHA
            ).astype(np.uint8)

            # Draw bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, f"{label} {conf}%",
                        (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

            # Mask stats
            pixel_count = int(mask_bool.sum())
            coverage = round(pixel_count / (w * h) * 100, 2)

            segments.append({
                "id": i,
                "label": label,
                "confidence": conf,
                "x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1,
                "pixel_count": pixel_count,
                "coverage_pct": coverage,
                "color": list(color),
            })
            class_summary[label] = class_summary.get(label, 0) + 1

    return {
        "segment_count": len(segments),
        "segments": segments,
        "class_summary": class_summary,
        "image_width": w,
        "image_height": h,
        "annotated_image": _to_base64(annotated),
        "mask_image": _to_base64(mask_overlay),
        "model": settings.YOLO_MODEL,
    }
