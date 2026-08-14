import logging
from PIL import Image
from typing import Optional
from app.schemas.detection import BoundingBox

logger = logging.getLogger(__name__)

def crop_detection_box(image: Image.Image, bbox: Optional[BoundingBox], padding_percent: float = 0.05) -> Image.Image:
    """
    Crops the image to the specified bounding box coordinates with optional padding.
    If no valid bounding box is provided, returns the original image.
    """
    if not bbox:
        return image

    img_w, img_h = image.size
    
    # Calculate box width and height
    box_w = max(1.0, bbox.x2 - bbox.x1)
    box_h = max(1.0, bbox.y2 - bbox.y1)

    # Apply padding
    pad_w = box_w * padding_percent
    pad_h = box_h * padding_percent

    x1 = max(0.0, bbox.x1 - pad_w)
    y1 = max(0.0, bbox.y1 - pad_h)
    x2 = min(float(img_w), bbox.x2 + pad_w)
    y2 = min(float(img_h), bbox.y2 + pad_h)

    # Validate crop bounds
    if (x2 - x1) < 10 or (y2 - y1) < 10:
        return image

    try:
        cropped = image.crop((int(x1), int(y1), int(x2), int(y2)))
        return cropped
    except Exception as e:
        logger.warning(f"[Image Utils] Bounding box crop error: {str(e)}")
        return image
