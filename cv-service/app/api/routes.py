from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.segmentor import segment

router = APIRouter(prefix="/api/v1/cv", tags=["segmentation"])
ALLOWED = {"jpg", "jpeg", "png", "bmp", "webp"}


def _validate(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")


@router.post("/segment")
async def segment_endpoint(file: UploadFile = File(...)):
    _validate(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return segment(content)
