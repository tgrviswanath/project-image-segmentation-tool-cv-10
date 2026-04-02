from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.service import segment_image
import httpx

router = APIRouter(prefix="/api/v1", tags=["segmentation"])


def _handle(e):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="CV service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/segment")
async def segment(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return await segment_image(file.filename, content, file.content_type or "image/jpeg")
    except Exception as e:
        _handle(e)
