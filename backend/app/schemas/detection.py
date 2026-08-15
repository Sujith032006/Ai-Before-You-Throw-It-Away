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
    name: str  # e.g., "plastic_bottle", "glass_bottle", "chair", "laptop"
    display_name: str  # e.g., "Plastic Bottle", "Glass Bottle", "Chair"
    base_object: str = "object"  # e.g., "bottle", "chair", "laptop"
    material: str = "unknown"  # e.g., "plastic", "glass", "wood", "metal", "electronic"
    condition: str = "usable"  # e.g., "usable", "used", "damaged"
    category: str = "Household Object"
    supported: bool = False
    confidence: float = 0.0
    confidence_level: str = "none"  # "high", "medium", "low", "none"

class DetectionItem(BaseModel):
    object: str
    display_name: str
    confidence: float
    material: Optional[str] = "unknown"
    category: Optional[str] = "Household Object"
    bounding_box: Optional[BoundingBox] = None
    bbox_normalized: Optional[BBoxNormalized] = None

class AnalyzerResult(BaseModel):
    object: NormalizedObject
    supported: bool = False
    confidence: float = 0.0
    confidence_level: str = "none"  # "high", "medium", "low", "none"
    source: str = "ollama_qwen3_vl"
    status: str = "ambiguous"
    verification: str = "consistent"
    bbox: Optional[BBoxNormalized] = None
    detected_objects: List[NormalizedObject] = []
    suggestions: List[str] = []
    debug_info: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    success: bool
    scan_id: Optional[str] = None
    analysis: Optional[AnalyzerResult] = None
    primary_detection: Optional[DetectionItem] = None
    detections: List[DetectionItem] = []
    message: Optional[str] = None
    mode: str = "ollama_qwen3_vl"
    debug: Optional[Dict[str, Any]] = None
