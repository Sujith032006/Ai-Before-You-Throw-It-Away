import io
import time
import logging
from PIL import Image
from fastapi import APIRouter, UploadFile, File, status, HTTPException
from typing import Dict, Any, List

from app.utils.config import (
    LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, VISION_MODEL, RFDETR_MODEL
)
from app.ai.vision_detector import analyze_image_with_vision_ai
from app.ai.rfdetr_detector import rfdetr_detector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debug", tags=["Dev Debugging Endpoints"])

@router.get("/env-status", status_code=status.HTTP_200_OK)
async def get_env_status() -> Dict[str, Any]:
    """
    Returns environment variable configuration status for debugging (safely, without exposing secret keys).
    """
    return {
        "status": "ok",
        "env_check": {
            "LLM_MODE": LLM_MODE,
            "LLM_PROVIDER": LLM_PROVIDER,
            "LLM_MODEL": LLM_MODEL,
            "VISION_MODEL": VISION_MODEL,
            "LLM_API_KEY_CONFIGURED": bool(LLM_API_KEY and len(LLM_API_KEY) > 5),
            "RFDETR_MODEL": RFDETR_MODEL,
        }
    }

@router.post("/analyzer", status_code=status.HTTP_200_OK)
async def debug_analyzer_raw(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Part 5 Bypassed Analyzer Debug Endpoint.
    Sends FULL UNCROPPED image directly to Gemini Vision without normalizer or database lookups.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    vision_raw_data = await analyze_image_with_vision_ai(image)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    if not vision_raw_data:
        return {
            "success": False,
            "latency_ms": elapsed_ms,
            "message": "Gemini Vision AI returned no result. Verify LLM_API_KEY.",
            "llm_api_key_configured": bool(LLM_API_KEY and len(LLM_API_KEY) > 5)
        }

    return {
        "success": True,
        "latency_ms": elapsed_ms,
        "raw_vision_response": vision_raw_data,
        "model_used": VISION_MODEL or LLM_MODEL
    }

@router.post("/vision-identify", status_code=status.HTTP_200_OK)
async def debug_vision_identify(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Independent test endpoint for Multimodal Vision AI.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    vision_item = await analyze_image_with_vision_ai(image)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    if not vision_item:
        return {
            "success": False,
            "latency_ms": elapsed_ms,
            "message": "Vision AI returned no result. Check if LLM_API_KEY is configured in backend/.env",
            "llm_api_key_configured": bool(LLM_API_KEY and len(LLM_API_KEY) > 5)
        }

    return {
        "success": True,
        "latency_ms": elapsed_ms,
        "vision_data": vision_item
    }

@router.post("/rfdetr", status_code=status.HTTP_200_OK)
async def debug_rfdetr(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Independent test endpoint for RF-DETR object detector.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    detections = rfdetr_detector.detect(image)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    det_list: List[Dict[str, Any]] = []
    for d in detections:
        bbox_dict = None
        if d.bounding_box:
            bbox_dict = {
                "x1": d.bounding_box.x1,
                "y1": d.bounding_box.y1,
                "x2": d.bounding_box.x2,
                "y2": d.bounding_box.y2
            }
        det_list.append({
            "class": d.object,
            "display_name": d.display_name,
            "confidence": d.confidence,
            "material": d.material,
            "category": d.category,
            "bbox": bbox_dict
        })

    return {
        "success": True,
        "latency_ms": elapsed_ms,
        "total_detections": len(det_list),
        "detections": det_list
    }
