import asyncio
import logging
import concurrent.futures
from PIL import Image, ImageOps
from typing import List, Optional, Dict, Any

from app.schemas.detection import (
    ScanResponse, DetectionItem, BoundingBox, BBoxNormalized,
    NormalizedObject, AnalyzerResult
)
from app.services.image_quality_service import evaluate_image_quality
from app.services.object_identification_service import object_identification_service, ObjectIdentificationResult

logger = logging.getLogger(__name__)

# Structured Upcycling Knowledge Base Classes
SUPPORTED_REUSE_CLASSES = {
    "plastic_bottle": ("Plastic Bottle", "plastic", "Household Container"),
    "glass_bottle": ("Glass Bottle", "glass", "Household Container"),
    "plastic_container": ("Plastic Food Container", "plastic", "Kitchen Storage"),
    "glass_jar": ("Glass Jar", "glass", "Pantry Storage"),
    "cardboard_box": ("Cardboard Box", "cardboard", "Packaging Waste"),
    "tin_can": ("Tin Can / Aluminum Can", "metal", "Kitchen Packaging"),
    "old_tshirt": ("Old T-Shirt", "cotton fabric", "Textiles & Clothing"),
    "jeans": ("Denim Jeans", "denim fabric", "Textiles & Clothing"),
    "egg_carton": ("Egg Carton", "molded pulp", "Biodegradable Packaging"),
    "shoe_box": ("Shoe Box", "cardboard", "Packaging Waste"),
    "remote_control": ("Remote Control", "plastic & electronics", "Electronic Waste"),
    "cell_phone": ("Cell Phone", "glass, metal & electronics", "Electronic Waste"),
    "book": ("Old Book", "paper & cardboard", "Paper & Publishing")
}

def check_reuse_database_support(base_obj: str, material: str) -> Dict[str, Any]:
    """
    Stage 2 Database Support Check:
    Checks if identified physical object + material is supported in structured reuse database.
    Does NOT modify physical object identity!
    """
    base_obj = base_obj.lower().strip().replace(" ", "_")
    mat = material.lower().strip() if material else "unknown"

    if "bottle" in base_obj:
        if "plastic" in mat or "pet" in mat:
            return {"name": "plastic_bottle", "display_name": "Plastic Bottle", "base_object": "bottle", "material": "plastic", "supported": True, "category": "Household Container"}
        elif "glass" in mat:
            return {"name": "glass_bottle", "display_name": "Glass Bottle", "base_object": "bottle", "material": "glass", "supported": True, "category": "Household Container"}
        elif "metal" in mat or "aluminum" in mat or "steel" in mat:
            return {"name": "tin_can", "display_name": "Metal Bottle / Can", "base_object": "bottle", "material": "metal", "supported": True, "category": "Kitchen Packaging"}
        else:
            return {"name": "bottle", "display_name": "Bottle", "base_object": "bottle", "material": "unknown", "supported": False, "category": "Containers"}

    if "jar" in base_obj or "vase" in base_obj:
        if "glass" in mat or "jar" in base_obj:
            return {"name": "glass_jar", "display_name": "Glass Jar", "base_object": "jar", "material": "glass", "supported": True, "category": "Pantry Storage"}

    if "box" in base_obj or "carton" in base_obj:
        if "shoe" in base_obj:
            return {"name": "shoe_box", "display_name": "Shoe Box", "base_object": "box", "material": "cardboard", "supported": True, "category": "Packaging Waste"}
        elif "egg" in base_obj or "pulp" in mat:
            return {"name": "egg_carton", "display_name": "Egg Carton", "base_object": "carton", "material": "molded pulp", "supported": True, "category": "Biodegradable Packaging"}
        elif "cardboard" in mat or "paper" in mat or "box" in base_obj:
            return {"name": "cardboard_box", "display_name": "Cardboard Box", "base_object": "box", "material": "cardboard", "supported": True, "category": "Packaging Waste"}

    if "can" in base_obj or "tin" in base_obj:
        return {"name": "tin_can", "display_name": "Tin Can", "base_object": "can", "material": "metal", "supported": True, "category": "Kitchen Packaging"}

    if "phone" in base_obj or "mobile" in base_obj or "smartphone" in base_obj:
        return {"name": "cell_phone", "display_name": "Cell Phone", "base_object": "smartphone", "material": mat if mat != "unknown" else "glass & electronics", "supported": True, "category": "Electronic Waste"}

    if "remote" in base_obj:
        return {"name": "remote_control", "display_name": "Remote Control", "base_object": "remote", "material": mat if mat != "unknown" else "plastic & electronics", "supported": True, "category": "Electronic Waste"}

    if "book" in base_obj or "notebook" in base_obj:
        return {"name": "book", "display_name": "Old Book", "base_object": "book", "material": "paper & cardboard", "supported": True, "category": "Paper & Publishing"}

    if "tshirt" in base_obj or "t-shirt" in base_obj or "shirt" in base_obj:
        return {"name": "old_tshirt", "display_name": "Old T-Shirt", "base_object": "tshirt", "material": "cotton fabric", "supported": True, "category": "Textiles & Clothing"}

    if "jeans" in base_obj or "denim" in base_obj:
        return {"name": "jeans", "display_name": "Denim Jeans", "base_object": "jeans", "material": "denim fabric", "supported": True, "category": "Textiles & Clothing"}

    # Unsupported Open-World Objects
    formatted_display = base_obj.replace("_", " ").title()
    category_map = {
        "chair": "Furniture", "stool": "Furniture", "bench": "Furniture", "couch": "Furniture", "sofa": "Furniture",
        "table": "Furniture", "desk": "Furniture",
        "laptop": "Electronics", "computer": "Electronics", "keyboard": "Electronics", "mouse": "Electronics", "monitor": "Electronics",
        "shoe": "Footwear", "bag": "Bags & Accessories", "backpack": "Bags & Accessories",
        "fan": "Appliances", "toy": "Toys & Recreation", "plant": "Plants & Gardening", "bicycle": "Vehicles & Transport"
    }

    return {
        "name": base_obj,
        "display_name": formatted_display,
        "base_object": base_obj,
        "material": mat,
        "supported": False,
        "category": category_map.get(base_obj, "Household Object")
    }

# Alias for backward compatibility
normalize_object_identity = check_reuse_database_support

def process_detection(image: Image.Image, file_size_bytes: int = 0) -> ScanResponse:
    # 1. EXIF Orientation Correction
    try:
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        logger.warning(f"[Detection Service] EXIF transpose error: {str(e)}")

    # 2. Stage 1: Physical Object Identification via Ollama Qwen3-VL
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            id_result: ObjectIdentificationResult = pool.submit(
                asyncio.run, object_identification_service.identify_object(image, file_size_bytes)
            ).result()
    else:
        id_result: ObjectIdentificationResult = asyncio.run(
            object_identification_service.identify_object(image, file_size_bytes)
        )

    # Unknown or Poor Quality image handling (STRICT: Unknown remains Unknown!)
    if id_result.status in ["poor_image_quality", "ambiguous", "unknown"] or id_result.object_name == "unknown":
        norm_obj = NormalizedObject(
            name="unknown",
            display_name="Unknown Object",
            base_object="unknown",
            material="unknown",
            condition="usable",
            category="Household Object",
            supported=False,
            confidence=0.0,
            confidence_level="unknown"
        )
        analyzer_res = AnalyzerResult(
            object=norm_obj,
            supported=False,
            confidence=0.0,
            confidence_level="unknown",
            source="ollama_qwen3_vl",
            status=id_result.status,
            verification="consistent",
            suggestions=[id_result.reason or "Please upload a clearer image showing the complete object."]
        )
        return ScanResponse(
            success=True,
            analysis=analyzer_res,
            message="Could not identify physical object confidently.",
            mode="ollama_qwen3_vl"
        )

    # 3. Stage 2: Reuse Database Support Lookup
    db_info = check_reuse_database_support(id_result.object_name, id_result.material)
    is_supported = db_info["supported"]
    status_str = "identified" if is_supported else "identified_but_unsupported"

    norm_obj = NormalizedObject(
        name=db_info["name"],
        display_name=db_info["display_name"],
        base_object=db_info["base_object"],
        material=id_result.material,
        condition=id_result.condition,
        category=db_info["category"],
        supported=is_supported,
        confidence=id_result.confidence,
        confidence_level=id_result.confidence_level
    )

    # Multi-object formatting if detected
    detected_norm_list: List[NormalizedObject] = []
    if id_result.status == "multiple_objects":
        status_str = "multiple_objects"
        for d_item in id_result.detected_objects:
            d_info = check_reuse_database_support(d_item["object_name"], d_item["material"])
            detected_norm_list.append(
                NormalizedObject(
                    name=d_info["name"],
                    display_name=d_info["display_name"],
                    base_object=d_info["base_object"],
                    material=d_item["material"],
                    condition=d_item.get("condition", "usable"),
                    category=d_info["category"],
                    supported=d_info["supported"],
                    confidence=d_item["confidence"],
                    confidence_level=d_item["confidence_level"]
                )
            )

    debug_data = {
        "model_used": "qwen3-vl:8b",
        "ollama_called": True,
        "raw_vision_object": id_result.object_name,
        "normalized_object": db_info["name"],
        "database_class": db_info["name"] if is_supported else "unsupported",
        "final_object": db_info["name"],
        "status": status_str,
        "supported": is_supported
    }

    analyzer_res = AnalyzerResult(
        object=norm_obj,
        supported=is_supported,
        confidence=id_result.confidence,
        confidence_level=id_result.confidence_level,
        source="ollama_qwen3_vl",
        status=status_str,
        verification="ollama_primary",
        bbox=None,
        detected_objects=detected_norm_list,
        debug_info=debug_data
    )

    msg = f"Identified {norm_obj.display_name} ({id_result.confidence_level.title()} Confidence)" if is_supported else f"Identified {norm_obj.display_name} (Outside Structured Reuse Database)"

    return ScanResponse(
        success=True,
        analysis=analyzer_res,
        primary_detection=None,
        detections=[],
        message=msg,
        mode="ollama_qwen3_vl"
    )
