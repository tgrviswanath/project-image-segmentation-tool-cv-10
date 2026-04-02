from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Image Segmentation CV Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    YOLO_MODEL: str = "yolov8n-seg.pt"   # nano segmentation model, auto-downloaded
    CONFIDENCE_THRESHOLD: float = 0.4
    MAX_IMAGE_SIZE: int = 1280
    MASK_ALPHA: float = 0.4              # mask overlay transparency

    class Config:
        env_file = ".env"


settings = Settings()
