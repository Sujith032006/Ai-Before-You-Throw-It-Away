import logging
from PIL import Image
from typing import Dict, Any, Optional

from app.ai.ollama_client import ollama_client
from app.utils.object_normalization import normalize_object_name, derive_confidence_level

logger = logging.getLogger(__name__)

SYSTEM_VISION_PROMPT = """You are a GENERAL PHYSICAL OBJECT IDENTIFICATION SYSTEM.

Your job is to identify what physical object is actually visible in the supplied image.

IMPORTANT RULES:
1. Identify the real-world physical object.
2. Do NOT classify the image according to recycling, waste, or packaging categories.
3. Do NOT use the application's reuse database.
4. Do NOT force the object into a predefined list.
5. Do NOT guess when the image is unclear.
6. If multiple distinct objects are visible, set status="multiple_objects" and list detected_objects.
7. If the main object cannot be identified confidently, return "unknown".
8. Prefer a specific common object name.

Examples:
- Chair -> chair
- Dining Table -> table
- Laptop computer -> laptop
- Smartphone -> smartphone
- Drinking bottle -> bottle
- Glass container -> glass jar
- Cardboard shipping box -> cardboard box

CRITICAL REGRESSION RULE:
If the image contains a CHAIR:
object_name MUST be "chair"
It must NEVER become "cardboard_box", "container", or "plastic_waste".

If uncertain between objects, set status = "ambiguous".

Return ONLY valid JSON format:
{
  "status": "identified",
  "object_name": "chair",
  "display_name": "Chair",
  "material": "plastic",
  "condition": "used",
  "confidence": 0.94,
  "alternatives": [],
  "reason": "The image clearly shows a chair."
}
"""

class OllamaObjectAnalyzer:
    """
    Local Vision AI Object Analyzer using Ollama + Qwen3-VL.
    Independent from recommendation engine and reuse database.
    """

    async def analyze_image(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        raw_res = await ollama_client.generate_vision_response(SYSTEM_VISION_PROMPT, image)
        if not raw_res or not isinstance(raw_res, dict):
            logger.info("[Ollama Analyzer] No valid response from local Qwen3-VL model.")
            return None

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
