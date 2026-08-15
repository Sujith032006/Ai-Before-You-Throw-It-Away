import logging
from PIL import Image
from typing import Dict, Any, Optional

from app.ai.ollama_client import ollama_client
from app.utils.object_normalization import normalize_object_name, derive_confidence_level

logger = logging.getLogger(__name__)

STRICT_OBJECT_IDENTIFICATION_PROMPT = """You are a GENERAL PHYSICAL OBJECT IDENTIFICATION ENGINE.

Your ONLY job is to identify the real physical object visible in the supplied image.

Ignore the application's reuse database.
Ignore recycling categories.
Ignore upcycling categories.
Ignore recommendation categories.
Ignore previous classifications.
Do not force the image into a predefined reuse class.

Identify the actual physical object.

Examples:
- chair -> chair
- plastic chair -> chair
- office chair -> chair
- wooden chair -> chair
- table -> table
- dining table -> table
- laptop -> laptop
- smartphone -> smartphone
- keyboard -> keyboard
- mouse -> mouse
- shoe -> shoe
- bag -> bag
- bottle -> bottle
- glass jar -> glass jar
- cardboard box -> cardboard box
- tin can -> tin can
- lamp -> lamp

The material is NOT the object name.
Example: plastic chair MUST produce:
object_name = "chair"
material = "plastic"

CRITICAL RULES:
1. If the image shows a CHAIR, object_name MUST be "chair". It must NEVER become "cardboard_box", "container", or "bottle".
2. Do not use the application's database to decide the object name.
3. If the object is unclear, return status = "unknown" and object_name = "unknown". Never invent an object.
4. If multiple distinct objects are clearly visible, return status = "multiple_objects" and list them in detected_objects.

Return ONLY valid JSON format:
{
  "status": "identified",
  "object_name": "chair",
  "display_name": "Chair",
  "material": "plastic",
  "condition": "used",
  "confidence": 0.95,
  "alternatives": [],
  "reason": "The image clearly shows a chair."
}
"""

class OllamaObjectAnalyzer:
    """
    Sole Local Vision AI Object Analyzer using Ollama + Qwen3-VL.
    Single Source of Truth for physical object identification.
    """

    async def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        raw_res = await ollama_client.generate_vision_response(STRICT_OBJECT_IDENTIFICATION_PROMPT, image)
        if not raw_res or not isinstance(raw_res, dict):
            logger.info("[Ollama Object Analyzer] Ollama returned no valid JSON response. Returning status=unknown.")
            return {
                "status": "unknown",
                "object_name": "unknown",
                "display_name": "Unknown Object",
                "material": "unknown",
                "condition": "unknown",
                "confidence": 0.0,
                "confidence_level": "unknown",
                "alternatives": [],
                "detected_objects": [],
                "reason": "Ollama server unreachable or image unparseable."
            }

        status = raw_res.get("status", "identified")
        raw_name = raw_res.get("object_name", "unknown")
        raw_mat = raw_res.get("material", "unknown")
        raw_cond = raw_res.get("condition", "used")
        confidence = float(raw_res.get("confidence", 0.90))

        norm = normalize_object_name(raw_name)

        return {
            "status": status,
            "object_name": norm["object_name"],
            "display_name": norm["display_name"],
            "material": raw_mat,
            "condition": raw_cond,
            "confidence": round(confidence, 4),
            "confidence_level": derive_confidence_level(confidence),
            "alternatives": raw_res.get("alternatives", []),
            "detected_objects": raw_res.get("detected_objects", []),
            "reason": raw_res.get("reason", f"Identified {norm['display_name']}.")
        }

# Singleton Instance
ollama_object_analyzer = OllamaObjectAnalyzer()
