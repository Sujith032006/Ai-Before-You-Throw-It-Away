import logging
import asyncio
from PIL import Image
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.utils.config import LLM_MODE, LLM_API_KEY, VISION_MODEL, LLM_MODEL
from app.ai.vision_detector import analyze_image_with_vision_ai
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
    status: str            # "identified" | "multiple_objects" | "ambiguous" | "poor_image_quality" | "analysis_error"
    detected_objects: List[Dict[str, Any]] = []

def derive_confidence_level(score: float) -> str:
    if score >= 0.85:
        return "high"
    elif score >= 0.65:
        return "medium"
    elif score >= 0.40:
        return "low"
    return "unknown"

def normalize_object_name(raw_name: str) -> Dict[str, str]:
    """
    Standardizes equivalent physical object names.
    NEVER converts an unknown or unsupported item into a reuse class!
    """
    clean = raw_name.lower().strip().replace("-", "_").replace(" ", "_")

    # Safe equivalencies
    mappings = {
        "cell_phone": ("smartphone", "Smartphone"),
        "mobile_phone": ("smartphone", "Smartphone"),
        "phone": ("smartphone", "Smartphone"),
        "dining_table": ("table", "Table"),
        "desk": ("table", "Desk / Table"),
        "computer_keyboard": ("keyboard", "Keyboard"),
        "computer_monitor": ("monitor", "Monitor / Screen"),
        "tv": ("monitor", "Monitor / Screen"),
        "backpack": ("backpack", "Backpack"),
        "handbag": ("bag", "Bag / Handbag"),
        "suitcase": ("bag", "Luggage / Bag"),
        "cardboard_container": ("cardboard_box", "Cardboard Box"),
        "shipping_box": ("cardboard_box", "Cardboard Box"),
        "aluminum_can": ("tin_can", "Tin Can / Aluminum Can"),
        "metal_can": ("tin_can", "Tin Can"),
        "glass_vase": ("glass_jar", "Glass Jar / Vase"),
    }

    if clean in mappings:
        n, d = mappings[clean]
        return {"object_name": n, "display_name": d}

    # Default clean format
    display = clean.replace("_", " ").title()
    return {"object_name": clean, "display_name": display}

class ObjectIdentificationService:
    """
    Central Service responsible ONLY for physical object identification.
    Separated from reuse database lookup and recommendations.
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

        # 2. Pass 1: Primary Gemini Vision Multimodal Identification
        raw_res1 = await analyze_image_with_vision_ai(image)

        if not raw_res1 or not isinstance(raw_res1, dict):
            logger.warning("[Object Identification Service] Vision AI returned no response.")
            return ObjectIdentificationResult(
                object_name="unknown",
                display_name="Unknown Object",
                confidence=0.0,
                confidence_level="unknown",
                material="unknown",
                condition="unknown",
                reason="Vision AI unavailable or image unparseable.",
                status="ambiguous"
            )

        status1 = raw_res1.get("status", "identified")
        objects1 = raw_res1.get("objects", [])
        reasoning = raw_res1.get("reasoning_summary", "")

        if status1 == "ambiguous" or not objects1:
            return ObjectIdentificationResult(
                object_name="unknown",
                display_name="Unknown Object",
                confidence=0.0,
                confidence_level="unknown",
                material="unknown",
                condition="unknown",
                reason=reasoning or "Could not identify object with high certainty.",
                status="ambiguous"
            )

        # Handle Multiple Objects
        if len(objects1) > 1 and status1 == "multiple_objects":
            formatted_list = []
            for item in objects1:
                norm_item = normalize_object_name(item.get("object_name", "unknown"))
                conf_item = float(item.get("confidence", 0.85))
                formatted_list.append({
                    "object_name": norm_item["object_name"],
                    "display_name": norm_item["display_name"],
                    "confidence": conf_item,
                    "confidence_level": item.get("confidence_level", derive_confidence_level(conf_item)),
                    "material": item.get("material", "unknown"),
                    "condition": item.get("condition", "usable")
                })
            return ObjectIdentificationResult(
                object_name=formatted_list[0]["object_name"],
                display_name=formatted_list[0]["display_name"],
                confidence=formatted_list[0]["confidence"],
                confidence_level=formatted_list[0]["confidence_level"],
                material=formatted_list[0]["material"],
                condition=formatted_list[0]["condition"],
                reason="Multiple distinct objects detected.",
                status="multiple_objects",
                detected_objects=formatted_list
            )

        # Primary Single Object
        p_obj = objects1[0]
        raw_name = p_obj.get("object_name", "unknown")
        raw_mat = p_obj.get("material", "unknown")
        raw_cond = p_obj.get("condition", "usable")
        raw_conf = float(p_obj.get("confidence", 0.90))

        norm = normalize_object_name(raw_name)

        # 3. Pass 2: Second-Pass Verification for Medium/Low Confidence (< 0.85)
        final_conf = raw_conf
        final_status = "identified"

        if raw_conf < 0.85 and LLM_MODE == "real":
            logger.info(f"[Object Identification Service] Pass 1 confidence {raw_conf} < 0.85. Executing Pass 2 Verification...")
            raw_res2 = await analyze_image_with_vision_ai(image)
            if raw_res2 and isinstance(raw_res2, dict) and raw_res2.get("objects"):
                p_obj2 = raw_res2["objects"][0]
                norm2 = normalize_object_name(p_obj2.get("object_name", "unknown"))
                if norm["object_name"] == norm2["object_name"]:
                    final_conf = min(0.95, max(raw_conf, float(p_obj2.get("confidence", 0.85))))
                    logger.info(f"[Object Identification Service] Pass 2 verified {norm['object_name']}. Conf updated to {final_conf}")
                else:
                    logger.warning(f"[Object Identification Service] Pass 1 ({norm['object_name']}) disagreed with Pass 2 ({norm2['object_name']}). Setting status to ambiguous.")
                    return ObjectIdentificationResult(
                        object_name="unknown",
                        display_name="Ambiguous Object",
                        confidence=0.0,
                        confidence_level="unknown",
                        material="unknown",
                        condition="unknown",
                        reason=f"Verification disagreement between {norm['object_name']} and {norm2['object_name']}.",
                        status="ambiguous"
                    )

        conf_level = derive_confidence_level(final_conf)

        return ObjectIdentificationResult(
            object_name=norm["object_name"],
            display_name=norm["display_name"],
            confidence=round(final_conf, 4),
            confidence_level=conf_level,
            material=raw_mat,
            condition=raw_cond,
            reason=reasoning or f"Identified physical object as {norm['display_name']}.",
            status=final_status
        )

# Singleton Instance
object_identification_service = ObjectIdentificationService()
