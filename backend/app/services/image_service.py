from PIL import Image
import io
from fastapi import HTTPException, status
from app.utils.config import MAX_UPLOAD_SIZE_BYTES

ALLOWED_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

def validate_and_load_image(file_bytes: bytes, content_type: str) -> Image.Image:
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image file size exceeds maximum limit of {MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
        )

    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed formats: JPEG, PNG, WEBP."
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verify that it is a valid image
        # Re-open after verify() because Pillow docs state verify() corrupts image instance
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        return image
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or unreadable image file."
        )
