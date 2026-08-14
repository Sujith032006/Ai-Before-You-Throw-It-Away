import asyncio
import logging
from PIL import Image, ImageOps
from typing import List, Optional

from app.utils.config import (
    AI_MODE, RFDETR_MODEL, HIGH_CONFIDENCE_THRESHOLD, LOW_CONFIDENCE_THRESHOLD
)
from app.schemas.detection import (
    ScanResponse, DetectionItem, BoundingBox, BBoxNormalized,
    NormalizedObject, AnalyzerResult
)
from app.services.image_quality_service import evaluate_image_quality

logger = logging.getLogger(__name__)

# Allowed object classes aligned with recommendation database
SUPPORTED_OBJECT_CLASSES = {
    "plastic_bottle": ("Plastic Bottle", "plastic", "Household Container"),
    "glass_bottle": ("Glass Bottle", "glass", "Household Container"),
    "plastic_container": ("Plastic Container", "plastic", "Kitchen Storage"),
    "glass_jar": ("Glass Jar", "glass", "Pantry Storage"),
    "cardboard_box": ("Cardboard Box", "cardboard", "Packaging Waste"),
    "tin_can": ("Tin Can", "metal", "Kitchen Packaging"),
    "old_tshirt": ("Old T-Shirt", "cotton fabric", "Textiles & Clothing"),
    "jeans": ("Denim Jeans", "denim fabric", "Textiles & Clothing"),
    "egg_carton": ("Egg Carton", "molded pulp", "Biodegradable Packaging"),
    "shoe_box": ("Shoe Box", "cardboard", "Packaging Waste"),
    "remote_control": ("Remote Control", "plastic & electronics", "Electronic Waste"),
    "cell_phone": ("Cell Phone", "glass, metal & electronics", "Electronic Waste"),
    "e_waste": ("Electronic Appliance", "plastic & metal", "Electronic Waste"),
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

def process_detection(image: Image.Image, file_size_bytes: int = 0) -> ScanResponse:
    # 1. Correct Image Orientation from EXIF
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
            material="unknown",
            condition="unknown",
            category="quality_warning"
        )
        analyzer_res = AnalyzerResult(
            object=poor_obj,
            confidence=0.0,
            source="quality_check",
            status="poor_image_quality",
            suggestions=quality_res.get("suggestions", [])
        )
        return ScanResponse(
            success=False,
            analysis=analyzer_res,
            message=quality_res["reason"],
            mode="quality_check"
        )

    # 3. Primary Engine: RF-DETR Object Detector
    rfdetr_detections: List[DetectionItem] = []
    try:
        from app.ai.rfdetr_detector import rfdetr_detector
        rfdetr_detections = rfdetr_detector.detect(image)
    except Exception as e:
        logger.error(f"[Detection Service] RF-DETR detection error: {str(e)}")

    # 4. Multi-Object Filtering & Bounding Box Area Strategy
    img_area = float(img_w * img_h)
    filtered_detections: List[DetectionItem] = []

    for d in rfdetr_detections:
        if d.bounding_box:
            box_area = (d.bounding_box.x2 - d.bounding_box.x1) * (d.bounding_box.y2 - d.bounding_box.y1)
            # Filter out tiny spurious bounding boxes (< 1.0% of total image area)
            if box_area < (img_area * 0.01) and len(rfdetr_detections) > 1:
                continue
            d.bbox_normalized = convert_to_normalized_bbox(d.bounding_box, img_w, img_h)
        filtered_detections.append(d)

    top_detection = filtered_detections[0] if filtered_detections else None

    # 5. High-Confidence Decision
    if top_detection and top_detection.confidence >= HIGH_CONFIDENCE_THRESHOLD and top_detection.object in SUPPORTED_OBJECT_CLASSES:
        disp_name, mat, cat = SUPPORTED_OBJECT_CLASSES[top_detection.object]
        norm_obj = NormalizedObject(
            name=top_detection.object,
            display_name=disp_name,
            material=mat,
            condition="usable",
            category=cat
        )
        analysis_res = AnalyzerResult(
            object=norm_obj,
            confidence=round(top_detection.confidence, 4),
            source="rf_detr",
            status="high_confidence",
            bbox=top_detection.bbox_normalized
        )
        return ScanResponse(
            success=True,
            analysis=analysis_res,
            primary_detection=top_detection,
            detections=filtered_detections,
            message=f"Identified {disp_name} with {int(top_detection.confidence*100)}% RF-DETR confidence.",
            mode="rf_detr"
        )

    # 6. Vision AI Verification Fallback (for low confidence or obscure objects)
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
            vision_item = loop.run_until_complete(analyze_image_with_vision_ai(image))
    except Exception as vision_err:
        logger.warning(f"[Detection Service] Vision AI verification skipped: {str(vision_err)}")

    if vision_item and vision_item.object != "unknown":
        obj_key = vision_item.object
        if obj_key in SUPPORTED_OBJECT_CLASSES:
            disp_name, mat, cat = SUPPORTED_OBJECT_CLASSES[obj_key]
        else:
            disp_name = vision_item.display_name
            mat = vision_item.material or "Reusable Material"
            cat = vision_item.category or "Household Object"

        norm_obj = NormalizedObject(
            name=obj_key,
            display_name=disp_name,
            material=mat,
            condition="usable",
            category=cat
        )
        bbox_norm = convert_to_normalized_bbox(vision_item.bounding_box, img_w, img_h)
        analysis_res = AnalyzerResult(
            object=norm_obj,
            confidence=round(vision_item.confidence, 4),
            source="vision_ai",
            status="verified",
            bbox=bbox_norm
        )
        return ScanResponse(
            success=True,
            analysis=analysis_res,
            primary_detection=vision_item,
            detections=[vision_item] + filtered_detections,
            message=f"Verified {disp_name} using Multimodal Vision AI with {int(vision_item.confidence*100)}% confidence.",
            mode="vision_ai"
        )

    # 7. RF-DETR Detection Return
    if top_detection:
        obj_key = top_detection.object
        if obj_key in SUPPORTED_OBJECT_CLASSES:
            disp_name, mat, cat = SUPPORTED_OBJECT_CLASSES[obj_key]
        else:
            disp_name = top_detection.display_name
            mat = top_detection.material or "Reusable Material"
            cat = top_detection.category or "Household Object"

        status_str = "high_confidence" if top_detection.confidence >= HIGH_CONFIDENCE_THRESHOLD else ("verified" if top_detection.confidence >= LOW_CONFIDENCE_THRESHOLD else "uncertain")
        norm_obj = NormalizedObject(
            name=obj_key,
            display_name=disp_name,
            material=mat,
            condition="usable",
            category=cat
        )
        analysis_res = AnalyzerResult(
            object=norm_obj,
            confidence=round(top_detection.confidence, 4),
            source="rf_detr",
            status=status_str,
            bbox=top_detection.bbox_normalized
        )
        return ScanResponse(
            success=True,
            analysis=analysis_res,
            primary_detection=top_detection,
            detections=filtered_detections,
            message=f"Identified {disp_name} with {int(top_detection.confidence*100)}% confidence.",
            mode="rf_detr"
        )

    # 8. Unknown Object Safeguard
    unknown_obj = NormalizedObject(
        name="unknown",
        display_name="Unknown Object",
        material="unknown",
        condition="unknown",
        category="unknown"
    )
    analysis_res = AnalyzerResult(
        object=unknown_obj,
        confidence=0.0,
        source="hybrid",
        status="unknown",
        suggestions=[
            "Move closer to the main object.",
            "Ensure good lighting and avoid shadows.",
            "Keep the object centered in the frame."
        ]
    )
    return ScanResponse(
        success=False,
        analysis=analysis_res,
        message="Could not confidently identify the object.",
        mode="hybrid"
    )
