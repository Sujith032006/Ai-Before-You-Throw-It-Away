import asyncio
import logging
from PIL import Image, ImageOps
from typing import List, Optional, Dict, Any

from app.utils.config import (
    AI_MODE, RFDETR_MODEL, HIGH_CONFIDENCE_THRESHOLD, LOW_CONFIDENCE_THRESHOLD
)
from app.schemas.detection import (
    ScanResponse, DetectionItem, BoundingBox, BBoxNormalized,
    NormalizedObject, AnalyzerResult
)
from app.services.image_quality_service import evaluate_image_quality
from app.utils.image_utils import crop_detection_box

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

def convert_to_normalized_bbox(bbox: Optional[BoundingBox], img_w: int, img_h: int) -> Optional[BBoxNormalized]:
    if not bbox:
        return None
    w = max(1.0, bbox.x2 - bbox.x1)
    h = max(1.0, bbox.y2 - bbox.y1)
    return BBoxNormalized(
        x=round(bbox.x1, 2),
        y=round(bbox.y1, 2),
        width=round(w, 2),
        height=round(h, 2)
    )

def get_confidence_level(score: float) -> str:
    if score >= 0.85:
        return "high"
    elif score >= 0.65:
        return "medium"
    elif score > 0.0:
        return "low"
    return "unknown"

def normalize_object_identity(base_obj: str, material: str) -> Dict[str, Any]:
    """
    Maps base physical object + material to structured object item.
    Crucial: Material is separated from base object identity!
    Only normalizes to a supported reuse class when material is verified!
    """
    base_obj = base_obj.lower().strip().replace(" ", "_")
    mat = material.lower().strip() if material else "unknown"

    # 1. Bottle Handling (Never guess material from word "bottle" alone!)
    if "bottle" in base_obj:
        if "plastic" in mat or "pet" in mat:
            return {
                "name": "plastic_bottle",
                "display_name": "Plastic Bottle",
                "base_object": "bottle",
                "material": "plastic",
                "supported": True,
                "category": "Household Container"
            }
        elif "glass" in mat:
            return {
                "name": "glass_bottle",
                "display_name": "Glass Bottle",
                "base_object": "bottle",
                "material": "glass",
                "supported": True,
                "category": "Household Container"
            }
        elif "metal" in mat or "aluminum" in mat or "steel" in mat:
            return {
                "name": "tin_can",
                "display_name": "Metal Bottle / Can",
                "base_object": "bottle",
                "material": "metal",
                "supported": True,
                "category": "Kitchen Packaging"
            }
        else:
            # Material unknown — bottle remains unsupported generic bottle!
            return {
                "name": "bottle",
                "display_name": "Bottle",
                "base_object": "bottle",
                "material": "unknown",
                "supported": False,
                "category": "Containers"
            }

    # 2. Glass Jar / Food Jar
    if "jar" in base_obj or "vase" in base_obj:
        if "glass" in mat or "jar" in base_obj:
            return {
                "name": "glass_jar",
                "display_name": "Glass Jar",
                "base_object": "jar",
                "material": "glass",
                "supported": True,
                "category": "Pantry Storage"
            }

    # 3. Box / Cardboard Container
    if "box" in base_obj or "carton" in base_obj:
        if "shoe" in base_obj:
            return {
                "name": "shoe_box",
                "display_name": "Shoe Box",
                "base_object": "box",
                "material": "cardboard",
                "supported": True,
                "category": "Packaging Waste"
            }
        elif "egg" in base_obj or "pulp" in mat:
            return {
                "name": "egg_carton",
                "display_name": "Egg Carton",
                "base_object": "carton",
                "material": "molded pulp",
                "supported": True,
                "category": "Biodegradable Packaging"
            }
        elif "cardboard" in mat or "paper" in mat or "box" in base_obj:
            return {
                "name": "cardboard_box",
                "display_name": "Cardboard Box",
                "base_object": "box",
                "material": "cardboard",
                "supported": True,
                "category": "Packaging Waste"
            }

    # 4. Tin Can / Food Can
    if "can" in base_obj or "tin" in base_obj:
        return {
            "name": "tin_can",
            "display_name": "Tin Can",
            "base_object": "can",
            "material": "metal",
            "supported": True,
            "category": "Kitchen Packaging"
        }

    # 5. Smartphone / Cell Phone
    if "phone" in base_obj or "mobile" in base_obj or "smartphone" in base_obj:
        return {
            "name": "cell_phone",
            "display_name": "Cell Phone",
            "base_object": "smartphone",
            "material": mat if mat != "unknown" else "glass & electronics",
            "supported": True,
            "category": "Electronic Waste"
        }

    # 6. Remote Control
    if "remote" in base_obj:
        return {
            "name": "remote_control",
            "display_name": "Remote Control",
            "base_object": "remote",
            "material": mat if mat != "unknown" else "plastic & electronics",
            "supported": True,
            "category": "Electronic Waste"
        }

    # 7. Books & Media
    if "book" in base_obj or "notebook" in base_obj:
        return {
            "name": "book",
            "display_name": "Old Book",
            "base_object": "book",
            "material": "paper & cardboard",
            "supported": True,
            "category": "Paper & Publishing"
        }

    # 8. Textiles (T-Shirt, Jeans)
    if "tshirt" in base_obj or "t-shirt" in base_obj or "shirt" in base_obj:
        return {
            "name": "old_tshirt",
            "display_name": "Old T-Shirt",
            "base_object": "tshirt",
            "material": "cotton fabric",
            "supported": True,
            "category": "Textiles & Clothing"
        }
    if "jeans" in base_obj or "denim" in base_obj:
        return {
            "name": "jeans",
            "display_name": "Denim Jeans",
            "base_object": "jeans",
            "material": "denim fabric",
            "supported": True,
            "category": "Textiles & Clothing"
        }

    # 9. Unsupported Open-World Objects (A Chair MUST remain a Chair! A Laptop MUST remain a Laptop!)
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

def process_detection(image: Image.Image, file_size_bytes: int = 0) -> ScanResponse:
    # 1. EXIF Orientation Correction
    try:
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        logger.warning(f"[Detection Service] EXIF transpose error: {str(e)}")

    img_w, img_h = image.size

    # 2. Image Quality Pre-Checker
    quality_res = evaluate_image_quality(image, file_size_bytes)
    if not quality_res["is_acceptable"]:
        logger.warning(f"[Detection Service] Quality check failed: {quality_res['reason']}")
        poor_obj = NormalizedObject(
            name="unknown",
            display_name="Poor Quality Photo",
            base_object="unknown",
            material="unknown",
            condition="unknown",
            category="quality_warning",
            supported=False,
            confidence=0.0,
            confidence_level="unknown"
        )
        analyzer_res = AnalyzerResult(
            object=poor_obj,
            supported=False,
            confidence=0.0,
            confidence_level="unknown",
            source="quality_check",
            status="poor_image_quality",
            verification="consistent",
            suggestions=quality_res.get("suggestions", [])
        )
        return ScanResponse(
            success=False,
            analysis=analyzer_res,
            message=quality_res["reason"],
            mode="quality_check"
        )

    # 3. Bounding Box Localization (RF-DETR optional localization layer)
    rfdetr_detections: List[DetectionItem] = []
    try:
        from app.ai.rfdetr_detector import rfdetr_detector
        rfdetr_detections = rfdetr_detector.detect(image)
    except Exception as e:
        logger.error(f"[Detection Service] RF-DETR localization error: {str(e)}")

    filtered_detections: List[DetectionItem] = []
    img_area = float(img_w * img_h)
    for d in rfdetr_detections:
        if d.bounding_box:
            box_area = (d.bounding_box.x2 - d.bounding_box.x1) * (d.bounding_box.y2 - d.bounding_box.y1)
            if box_area < (img_area * 0.01) and len(rfdetr_detections) > 1:
                continue
            d.bbox_normalized = convert_to_normalized_bbox(d.bounding_box, img_w, img_h)
        filtered_detections.append(d)

    rf_top = filtered_detections[0] if filtered_detections else None

    # 4. Primary Gemini Multimodal Vision Analyzer Execution
    cropped_img = image
    if rf_top and rf_top.bounding_box:
        cropped_img = crop_detection_box(image, rf_top.bounding_box)

    vision_raw_data = None
    try:
        from app.ai.vision_detector import analyze_image_with_vision_ai
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop and not loop.is_running():
            vision_raw_data = loop.run_until_complete(analyze_image_with_vision_ai(image))
    except Exception as vision_err:
        logger.warning(f"[Detection Service] Gemini Vision AI call error: {str(vision_err)}")

    # 5. Extract Objects & Evidence from Gemini Vision Response
    objects_found: List[Dict[str, Any]] = []
    primary_object_dict: Optional[Dict[str, Any]] = None
    vi_status = "ambiguous"

    if vision_raw_data and isinstance(vision_raw_data, dict):
        vi_status = vision_raw_data.get("status", "identified")
        objects_found = vision_raw_data.get("objects", [])
        p_idx = vision_raw_data.get("primary_object_index", 0)
        if objects_found and p_idx < len(objects_found):
            primary_object_dict = objects_found[p_idx]
        elif objects_found:
            primary_object_dict = objects_found[0]

    # Check for Ambiguous / Low Quality Vision Result
    if vi_status == "ambiguous" or not primary_object_dict or primary_object_dict.get("object_name", "unknown") == "unknown":
        # Fallback to RF-DETR localization if available, but NEVER force a fake object!
        if rf_top and rf_top.confidence >= 0.15 and rf_top.object != "unknown":
            chosen_base = rf_top.object
            chosen_mat = rf_top.material or "unknown"
            chosen_conf = rf_top.confidence
            source_engine = "rf_detr"
            verification_status = "rf_detr_primary"
        else:
            unknown_obj = NormalizedObject(
                name="unknown",
                display_name="Unknown Object",
                base_object="unknown",
                material="unknown",
                condition="unknown",
                category="unknown",
                supported=False,
                confidence=0.0,
                confidence_level="unknown"
            )
            analyzer_res = AnalyzerResult(
                object=unknown_obj,
                supported=False,
                confidence=0.0,
                confidence_level="unknown",
                source="hybrid",
                status="ambiguous",
                verification="consistent",
                suggestions=[
                    "Please take another photo with the object clearly visible.",
                    "Ensure bright lighting without heavy background glare.",
                    "Keep the object centered in the camera frame."
                ]
            )
            return ScanResponse(
                success=False,
                analysis=analyzer_res,
                message="Object could not be identified reliably. Please retake photo.",
                mode="hybrid"
            )
    else:
        chosen_base = primary_object_dict.get("object_name", "unknown")
        chosen_mat = primary_object_dict.get("material", "unknown")
        chosen_conf = float(primary_object_dict.get("confidence", 0.90))
        source_engine = "vision_ai"
        verification_status = "vision_ai_primary"

    # 6. Normalize Object Identity (Stage 1 Output)
    norm_info = normalize_object_identity(chosen_base, chosen_mat)
    conf_level = primary_object_dict.get("confidence_level") if primary_object_dict else get_confidence_level(chosen_conf)
    if not conf_level or conf_level not in ["high", "medium", "low", "unknown"]:
        conf_level = get_confidence_level(chosen_conf)

    norm_obj = NormalizedObject(
        name=norm_info["name"],
        display_name=norm_info["display_name"],
        base_object=norm_info["base_object"],
        material=norm_info["material"],
        condition=primary_object_dict.get("condition", "usable") if primary_object_dict else "usable",
        category=norm_info["category"],
        supported=norm_info["supported"],
        confidence=round(chosen_conf, 4),
        confidence_level=conf_level
    )

    # 7. Check Stage 2 Supported Reuse Status
    is_supported = norm_info["supported"]
    status_str = "identified" if is_supported else "identified_but_unsupported"

    # Multi-Object Handling
    detected_norm_list: List[NormalizedObject] = []
    if len(objects_found) > 1:
        status_str = "multiple_objects"
        for obj_item in objects_found:
            b_name = obj_item.get("object_name", "unknown")
            b_mat = obj_item.get("material", "unknown")
            d_norm = normalize_object_identity(b_name, b_mat)
            d_conf = float(obj_item.get("confidence", 0.85))
            detected_norm_list.append(
                NormalizedObject(
                    name=d_norm["name"],
                    display_name=d_norm["display_name"],
                    base_object=d_norm["base_object"],
                    material=d_norm["material"],
                    condition=obj_item.get("condition", "usable"),
                    category=d_norm["category"],
                    supported=d_norm["supported"],
                    confidence=round(d_conf, 4),
                    confidence_level=obj_item.get("confidence_level", get_confidence_level(d_conf))
                )
            )

    top_bbox = rf_top.bbox_normalized if rf_top else None

    debug_data = {
        "gemini_vision_status": vi_status,
        "chosen_base_object": chosen_base,
        "chosen_material": chosen_mat,
        "final_confidence": chosen_conf,
        "normalized_name": norm_info["name"],
        "supported": is_supported
    }

    analyzer_res = AnalyzerResult(
        object=norm_obj,
        supported=is_supported,
        confidence=round(chosen_conf, 4),
        confidence_level=conf_level,
        source=source_engine,
        status=status_str,
        verification=verification_status,
        bbox=top_bbox,
        detected_objects=detected_norm_list,
        debug_info=debug_data
    )

    msg = f"Identified {norm_obj.display_name} ({conf_level.title()} Confidence)" if is_supported else f"Identified {norm_obj.display_name} (Outside Structured Reuse Database)"

    return ScanResponse(
        success=True,
        analysis=analyzer_res,
        primary_detection=rf_top,
        detections=filtered_detections,
        message=msg,
        mode=source_engine
    )
