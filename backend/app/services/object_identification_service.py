import logging
from PIL import Image
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.utils.object_normalization import normalize_object_name, derive_confidence_level
from app.ai.ollama_object_analyzer import ollama_object_analyzer
from app.services.image_quality_service import evaluate_image_quality

logger = logging.getLogger(__name__)

class ObjectIdentificationResult(BaseModel):
    object_name: str
    display_name: str
    confidence: float
    confidence_level: str  # "high" | "medium" | "low" | "unknown"
    material: str
    condition: str
    reason: Optional[str] = None
    status: str            # "identified" | "multiple_objects" | "ambiguous" | "poor_image_quality" | "unknown" | "analyzer_unavailable"
    detected_objects: List[Dict[str, Any]] = []

class ObjectIdentificationService:
    """
    Central Physical Object Identification Service.
    Ollama Vision AI (LLaVA) is the SOLE physical object analyzer.
    """

    async def identify_object(self, image: Image.Image, file_size_bytes: int = 0) -> ObjectIdentificationResult:
        # 1. Image Quality Pre-Check
        quality_res = evaluate_image_quality(image, file_size_bytes)
        if not quality_res["is_acceptable"]:
            logger.warning(f"[Object Identification Service] Quality failed: {quality_res['reason']}")
            return ObjectIdentificationResult(
                object_name="unknown",
                display_name="Poor Quality Photo",
                confidence=0.0,
                confidence_level="unknown",
                material="unknown",
                condition="unknown",
                reason=quality_res["reason"],
                status="poor_image_quality"
            )

        # 2. Execute Sole Physical Object Analyzer: Ollama LLaVA Vision AI
        res = await ollama_object_analyzer.analyze_image(image)

        if not res or res.get("status") == "analyzer_unavailable":
            return ObjectIdentificationResult(
                object_name="unknown",
                display_name="Unknown Object",
                confidence=0.0,
                confidence_level="unknown",
                material="unknown",
                condition="unknown",
                reason="Local Ollama AI analyzer is currently unavailable.",
                status="analyzer_unavailable"
            )

        return ObjectIdentificationResult(
            object_name=res["object_name"],
            display_name=res["display_name"],
            confidence=res["confidence"],
            confidence_level=res["confidence_level"],
            material=res["material"],
            condition=res["condition"],
            reason=res["reason"],
            status=res["status"],
            detected_objects=res.get("detected_objects", [])
        )

# Singleton Instance
object_identification_service = ObjectIdentificationService()
