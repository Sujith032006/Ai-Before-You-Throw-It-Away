from typing import List, Optional
from pydantic import BaseModel

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class DetectionItem(BaseModel):
    object: str
    display_name: str
    confidence: float
    material: Optional[str] = "Plastic / Metal"
    category: Optional[str] = "Household Item"
    bounding_box: Optional[BoundingBox] = None

class ScanResponse(BaseModel):
    success: bool
    scan_id: Optional[str] = None
    primary_detection: Optional[DetectionItem] = None
    detections: List[DetectionItem] = []
    message: Optional[str] = None
    mode: str = "real"
