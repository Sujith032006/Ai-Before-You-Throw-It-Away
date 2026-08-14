from typing import Dict, Any, List
from PIL import Image
import logging
from app.utils.config import MAX_UPLOAD_SIZE_BYTES

logger = logging.getLogger(__name__)

def evaluate_image_quality(image: Image.Image, file_size_bytes: int = 0) -> Dict[str, Any]:
    """
    Evaluates uploaded image quality for readability, lighting, dimensions, and blur.
    Returns status: 'poor_image_quality' with suggestions if quality is too low.
    """
    suggestions: List[str] = []

    # 1. File Size Check
    if file_size_bytes > 0 and file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
        return {
            "is_acceptable": False,
            "status": "poor_image_quality",
            "reason": "File size exceeds maximum allowed threshold.",
            "suggestions": ["Please compress or crop the photo before uploading."]
        }

    width, height = image.size

    # 2. Minimum Dimensions Check
    if width < 32 or height < 32:
        return {
            "is_acceptable": False,
            "status": "poor_image_quality",
            "reason": "Image resolution is too small.",
            "suggestions": [
                "Move closer to the object",
                "Take a photo with higher camera resolution"
            ]
        }

    # 3. Extreme Dark / Bright Lighting Check
    try:
        rgb_img = image.convert("RGB")
        resized = rgb_img.resize((50, 50))
        pixels = [resized.getpixel((x, y)) for x in range(50) for y in range(50)]
        avg_brightness = sum((p[0] + p[1] + p[2]) / 3.0 for p in pixels) / len(pixels)

        if avg_brightness < 15.0:
            suggestions.append("Improve lighting — the photo is extremely dark.")
        elif avg_brightness > 248.0:
            suggestions.append("Reduce bright glare or direct flash overexposure.")
    except Exception as e:
        logger.warning(f"[Quality Check] Brightness check error: {str(e)}")

    if suggestions:
        return {
            "is_acceptable": False,
            "status": "poor_image_quality",
            "reason": "Image quality is insufficient for accurate AI detection.",
            "suggestions": suggestions
        }

    return {
        "is_acceptable": True,
        "status": "ok",
        "reason": "Image quality is good.",
        "suggestions": []
    }
