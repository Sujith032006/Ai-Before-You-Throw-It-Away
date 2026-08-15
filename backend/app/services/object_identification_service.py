import logging
import httpx
from PIL import Image
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.utils.config import LLM_MODE, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT_SECONDS
from app.utils.object_normalization import normalize_object_name, derive_confidence_level
from app.ai.ollama_object_analyzer import ollama_object_analyzer
from app.ai.ollama_client import convert_pil_to_base64
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
    status: str            # "identified" | "multiple_objects" | "ambiguous" | "poor_image_quality" | "unknown"
    detected_objects: List[Dict[str, Any]] = []

async def analyze_image_with_cloud_gemini(image: Image.Image) -> Optional[Dict[str, Any]]:
    """
    Cloud Gemini Multimodal Vision AI Fallback for Cloud Deployments (Render / Vercel).
    Used when local Ollama is unreachable on cloud servers.
    """
    if not LLM_API_KEY:
        logger.warning("[Cloud Gemini Vision] No LLM_API_KEY configured for cloud fallback.")
        return None

    img_b64 = convert_pil_to_base64(image)
    model_name = LLM_MODEL if LLM_MODEL and "gemini" in LLM_MODEL else "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={LLM_API_KEY}"

    prompt = """Identify the real physical object visible in the supplied image.
Return ONLY valid JSON format:
{
  "status": "identified",
  "object_name": "chair",
  "display_name": "Chair",
  "material": "plastic",
  "condition": "used",
  "confidence": 0.95,
  "reason": "Visible four-legged chair."
}
If unclear, return status="unknown" and object_name="unknown".
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=float(LLM_TIMEOUT_SECONDS)) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                import json
                return json.loads(text)
    except Exception as e:
        logger.warning(f"[Cloud Gemini Vision] Error calling Gemini: {str(e)}")

    return None

class ObjectIdentificationService:
    """
    Central Physical Object Identification Service.
    Local Laptop Mode: Ollama + LLaVA.
    Cloud Render Mode: Gemini Vision API (when Ollama is not local to cloud container).
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

        # 2. Attempt Local Ollama LLaVA Vision AI (Laptop Mode)
        res = await ollama_object_analyzer.analyze_image(image)
        if res and res.get("status") != "unknown" and res.get("object_name") != "unknown":
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

        # 3. Cloud Deployment Fallback (Render Mode when Ollama is offline in cloud)
        cloud_res = await analyze_image_with_cloud_gemini(image)
        if cloud_res and isinstance(cloud_res, dict) and cloud_res.get("object_name"):
            norm = normalize_object_name(cloud_res.get("object_name", "unknown"))
            conf = float(cloud_res.get("confidence", 0.90))
            return ObjectIdentificationResult(
                object_name=norm["object_name"],
                display_name=norm["display_name"],
                confidence=conf,
                confidence_level=derive_confidence_level(conf),
                material=cloud_res.get("material", "unknown"),
                condition=cloud_res.get("condition", "usable"),
                reason=cloud_res.get("reason", "Identified by Cloud Vision AI"),
                status=cloud_res.get("status", "identified")
            )

        # Return clean unknown if neither returned valid match
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
