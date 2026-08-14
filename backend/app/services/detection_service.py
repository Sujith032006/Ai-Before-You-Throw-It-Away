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
    return "none"

def normalize_object_identity(base_obj: str, material: str) -> Dict[str, Any]:
    """
    Normalizes open-world physical object + material into structured object item.
    Only normalizes to a supported reuse class when material is verified!
    """
    base_obj = base_obj.lower().strip().replace(" ", "_")
    mat = material.lower().strip() if material else "unknown"

    # 1. Bottle Handling (Never guess material!)
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
            # Material unknown — do not force plastic_bottle!
            return {
                "name": "bottle",
                "display_name": "Bottle",
                "base_object": "bottle",
                "material": "unknown",
                "supported": False,
                "category": "Containers"
            }

    # 2. Jar / Glassware
    if "jar" in base_obj or "vase" in base_obj:
        if "glass" in mat or "vase" in base_obj or "jar" in base_obj:
            return {
                "name": "glass_jar",
                "display_name": "Glass Jar",
                "base_object": "jar",
                "material": "glass",
                "supported": True,
                "category": "Pantry Storage"
            }

    # 3. Box / Cardboard
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
        else:
            return {
                "name": "cardboard_box",
                "display_name": "Cardboard Box",
                "base_object": "box",
                "material": "cardboard",
                "supported": True,
                "category": "Packaging Waste"
            }

    # 4. Can / Beverage Container
    if "can" in base_obj or "cup" in base_obj or "mug" in base_obj:
        if "metal" in mat or "aluminum" in mat or "steel" in mat or "can" in base_obj:
            return {
                "name": "tin_can",
                "display_name": "Tin Can",
                "base_object": "can",
                "material": "metal",
                "supported": True,
                "category": "Kitchen Packaging"
            }

    # 5. Cell Phone / Smartphone
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

    # 8. Clothing / T-Shirt / Jeans
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
            confidence_level="none"
        )
        analyzer_res = AnalyzerResult(
            object=poor_obj,
            supported=False,
            confidence=0.0,
            confidence_level="none",
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

    # 3. Stage 1: RF-DETR Primary Inference & Bounding Box Extraction
    rfdetr_detections: List[DetectionItem] = []
    try:
        from app.ai.rfdetr_detector import rfdetr_detector
        rfdetr_detections = rfdetr_detector.detect(image)
    except Exception as e:
        logger.error(f"[Detection Service] RF-DETR detection error: {str(e)}")

    # Bounding box area filter
    img_area = float(img_w * img_h)
    filtered_detections: List[DetectionItem] = []
    for d in rfdetr_detections:
        if d.bounding_box:
            box_area = (d.bounding_box.x2 - d.bounding_box.x1) * (d.bounding_box.y2 - d.bounding_box.y1)
            if box_area < (img_area * 0.01) and len(rfdetr_detections) > 1:
                continue
            d.bbox_normalized = convert_to_normalized_bbox(d.bounding_box, img_w, img_h)
        filtered_detections.append(d)

    rf_top = filtered_detections[0] if filtered_detections else None

    # 4. Bounding Box Crop & Vision AI Open-World Analysis
    cropped_img = image
    if rf_top and rf_top.bounding_box:
        cropped_img = crop_detection_box(image, rf_top.bounding_box)

    vision_item = None
    try:
        from app.ai.vision_detector import analyze_image_with_vision_ai
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop and not loop.is_running():
            vision_item = loop.run_until_complete(analyze_image_with_vision_ai(cropped_img))
    except Exception as vision_err:
        logger.warning(f"[Detection Service] Vision AI verification skipped: {str(vision_err)}")

    # 5. Evidence & Consistency Verification Analysis
    rf_obj = rf_top.object.lower() if rf_top else "unknown"
    rf_conf = rf_top.confidence if rf_top else 0.0

    vi_obj = vision_item.object.lower() if vision_item else "unknown"
    vi_conf = vision_item.confidence if vision_item else 0.0
    vi_mat = vision_item.material if vision_item else "unknown"

    verification_status = "consistent"
    chosen_base_obj = "unknown"
    chosen_material = "unknown"
    final_confidence = 0.0
    source_engine = "hybrid"

    # Evaluate Evidence
    if vi_obj != "unknown":
        if rf_obj != "unknown" and rf_obj != vi_obj and rf_conf >= 0.80 and vi_conf >= 0.80:
            # CONFLICT UNRESOLVED: RF-DETR says bottle 0.92, Vision AI says chair 0.96 with blur/glare
            logger.warning(f"[Detection Service] UNRESOLVED CONFLICT: RF-DETR ({rf_obj}={rf_conf}) vs Vision AI ({vi_obj}={vi_conf})")
            verification_status = "conflict_unresolved"
            unknown_obj = NormalizedObject(
                name="unknown",
                display_name="Ambiguous Object",
                base_object="unknown",
                material="unknown",
                condition="unknown",
                category="unknown",
                supported=False,
                confidence=0.0,
                confidence_level="none"
            )
            analyzer_res = AnalyzerResult(
                object=unknown_obj,
                supported=False,
                confidence=0.0,
                confidence_level="none",
                source="hybrid",
                status="ambiguous",
                verification="conflict_unresolved",
                suggestions=[
                    "Hold device steady and center the object.",
                    "Ensure clear lighting without heavy glare.",
                    "Avoid cluttered backgrounds with multiple conflicting items."
                ],
                debug_info={
                    "rfdetr_object": rf_obj, "rfdetr_conf": rf_conf,
                    "vision_object": vi_obj, "vision_conf": vi_conf,
                    "conflict": "unresolved"
                }
            )
            return ScanResponse(
                success=False,
                analysis=analyzer_res,
                message="Conflicting detection signals. Please retake photo with clearer lighting.",
                mode="hybrid"
            )

        chosen_base_obj = vi_obj
        chosen_material = vi_mat
        final_confidence = max(vi_conf, rf_conf)
        verification_status = "consistent" if (rf_obj == vi_obj or rf_obj == "unknown") else "vision_ai_primary"
        source_engine = "vision_ai" if verification_status == "vision_ai_primary" else "hybrid"

    elif rf_top and rf_conf > 0.15:
        chosen_base_obj = rf_obj
        chosen_material = rf_top.material if rf_top.material != "unknown" else vi_mat
        final_confidence = rf_conf
        verification_status = "rf_detr_primary"
        source_engine = "rf_detr"

    else:
        # Absolute unknown safeguard
        unknown_obj = NormalizedObject(
            name="unknown",
            display_name="Unknown Object",
            base_object="unknown",
            material="unknown",
            condition="unknown",
            category="unknown",
            supported=False,
            confidence=0.0,
            confidence_level="none"
        )
        analyzer_res = AnalyzerResult(
            object=unknown_obj,
            supported=False,
            confidence=0.0,
            confidence_level="none",
            source="hybrid",
            status="ambiguous",
            verification="consistent",
            suggestions=[
                "Move closer to the main object.",
                "Ensure bright, even lighting.",
                "Keep the object centered in the frame."
            ]
        )
        return ScanResponse(
            success=False,
            analysis=analyzer_res,
            message="Could not confidently identify the physical object.",
            mode="hybrid"
        )

    # 6. Normalize Object Identity (Stage 1 Output)
    normalized_data = normalize_object_identity(chosen_base_obj, chosen_material)
    conf_level = get_confidence_level(final_confidence)

    norm_obj = NormalizedObject(
        name=normalized_data["name"],
        display_name=normalized_data["display_name"],
        base_object=normalized_data["base_object"],
        material=normalized_data["material"],
        condition=vision_item.condition if vision_item and hasattr(vision_item, 'condition') else "usable",
        category=normalized_data["category"],
        supported=normalized_data["supported"],
        confidence=round(final_confidence, 4),
        confidence_level=conf_level
    )

    # 7. Check Stage 2 Supported Status
    is_supported = normalized_data["supported"]
    status_str = "identified" if is_supported else "identified_but_unsupported"

    # Multi-object check: If more than 1 distinct high-confidence object detected
    detected_norm_list: List[NormalizedObject] = []
    if len(filtered_detections) > 1 and filtered_detections[1].confidence >= 0.55:
        status_str = "multiple_objects"
        for det in filtered_detections[:4]:
            d_norm = normalize_object_identity(det.object, det.material or "unknown")
            detected_norm_list.append(
                NormalizedObject(
                    name=d_norm["name"],
                    display_name=d_norm["display_name"],
                    base_object=d_norm["base_object"],
                    material=d_norm["material"],
                    category=d_norm["category"],
                    supported=d_norm["supported"],
                    confidence=round(det.confidence, 4),
                    confidence_level=get_confidence_level(det.confidence)
                )
            )

    top_bbox = rf_top.bbox_normalized if rf_top else None

    debug_data = {
        "rfdetr_object": rf_obj,
        "rfdetr_confidence": rf_conf,
        "vision_ai_object": vi_obj,
        "vision_ai_confidence": vi_conf,
        "extracted_material": chosen_material,
        "verification_status": verification_status,
        "normalized_name": normalized_data["name"],
        "supported_database_status": is_supported
    }

    analyzer_res = AnalyzerResult(
        object=norm_obj,
        supported=is_supported,
        confidence=round(final_confidence, 4),
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
