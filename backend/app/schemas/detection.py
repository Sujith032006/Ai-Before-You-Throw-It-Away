from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class BBoxNormalized(BaseModel):
    x: float
    y: float
    width: float
    height: float

class NormalizedObject(BaseModel):
    name: str
    display_name: str
    material: str = "Reusable Material"
    condition: str = "good"
    category: str = "Household Object"

class DetectionItem(BaseModel):
    object: str
    display_name: str
    confidence: float
    material: Optional[str] = "Reusable Material"
    category: Optional[str] = "Household Object"
    bounding_box: Optional[BoundingBox] = None
    bbox_normalized: Optional[BBoxNormalized] = None

class AnalyzerResult(BaseModel):
    object: NormalizedObject
    confidence: float
    source: str  # "rf_detr", "vision_ai", "hybrid"
    status: str  # "high_confidence", "verified", "uncertain", "unknown", "poor_image_quality"
    bbox: Optional[BBoxNormalized] = None
    suggestions: List[str] = []

class ScanResponse(BaseModel):
    success: bool
    scan_id: Optional[str] = None
    analysis: Optional[AnalyzerResult] = None
    primary_detection: Optional[DetectionItem] = None
    detections: List[DetectionItem] = []
    message: Optional[str] = None
    mode: str = "rf_detr"
