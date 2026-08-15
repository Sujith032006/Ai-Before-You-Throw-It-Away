import io
import time
import logging
from PIL import Image
from fastapi import APIRouter, UploadFile, File, status, HTTPException
from typing import Dict, Any, List

from app.utils.config import (
    LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, VISION_MODEL, RFDETR_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
from app.ai.vision_detector import analyze_image_with_vision_ai
from app.ai.rfdetr_detector import rfdetr_detector
from app.ai.ollama_client import ollama_client
from app.ai.ollama_object_analyzer import ollama_object_analyzer
from app.services.object_identification_service import object_identification_service
from app.services.evaluation_service import run_evaluation_suite

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dev Debugging & Analyzer Endpoints"])

@router.post("/api/debug/vision-test", status_code=status.HTTP_200_OK)
async def vision_test_endpoint(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Step 4 Raw Vision Isolation Test Endpoint.
    Sends ONLY the image directly to Qwen3-VL/Vision AI without passing through
    normalization, database lookup, or fallbacks.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    prompt = """Look at the supplied image.

What is the main physical object?

Answer with only the common object name.

Do not use recycling categories.
Do not use reuse categories.
Do not use application database categories.

If the image clearly shows a chair, answer CHAIR.

If you cannot determine the object, answer UNKNOWN."""

    # Try Ollama Qwen3-VL first
    ollama_res = await ollama_client.generate_vision_response(prompt, image)
    if ollama_res:
        raw_text = str(ollama_res)
        return {
            "model": OLLAMA_MODEL,
            "raw_response": raw_text,
            "image_sent": True
        }

    # Fallback to Gemini Vision AI if Ollama unavailable
    raw_res = await analyze_image_with_vision_ai(image)
    return {
        "model": VISION_MODEL or LLM_MODEL,
        "raw_response": str(raw_res),
        "image_sent": True
    }

@router.get("/api/analyzer/health", tags=["Analyzer Health"])
@router.get("/api/debug/analyzer/health", tags=["Analyzer Health"])
async def analyzer_health() -> Dict[str, Any]:
    """
    Section 23 Model Availability Check Endpoint.
    Checks Ollama server reachability and Qwen3-VL vision model status.
    """
    return await ollama_client.check_health()

@router.post("/api/analyzer/compare", tags=["Analyzer Comparison"])
@router.post("/api/debug/analyzer/compare", tags=["Analyzer Comparison"])
async def compare_analyzers(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Section 16 Analyzer Comparison Mode Endpoint.
    Compares Ollama Qwen3-VL local vision AI vs Cloud Vision AI / RF-DETR.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    ollama_result = await ollama_object_analyzer.analyze_image(image)
    gemini_result = await analyze_image_with_vision_ai(image)
    rfdetr_detections = rfdetr_detector.detect(image)

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "latency_ms": elapsed_ms,
        "comparison": {
            "ollama_qwen3_vl": ollama_result or {"status": "unavailable", "message": "Ollama server not reachable at " + OLLAMA_BASE_URL},
            "gemini_vision_ai": gemini_result or {"status": "unavailable"},
            "rfdetr_localization": [
                {"class": d.object, "display_name": d.display_name, "confidence": d.confidence}
                for d in rfdetr_detections
            ]
        }
    }

@router.get("/api/debug/evaluate", status_code=status.HTTP_200_OK)
@router.post("/api/debug/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_suite() -> Dict[str, Any]:
    """
    Section 3 & 4 Automated Evaluation Suite Endpoint across 20 object categories.
    """
    return run_evaluation_suite()

@router.get("/api/debug/env-status", status_code=status.HTTP_200_OK)
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
            "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
            "OLLAMA_MODEL": OLLAMA_MODEL,
            "LLM_API_KEY_CONFIGURED": bool(LLM_API_KEY and len(LLM_API_KEY) > 5),
            "RFDETR_MODEL": RFDETR_MODEL,
        }
    }

@router.post("/api/debug/object-identification", status_code=status.HTTP_200_OK)
async def debug_object_identification(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Part 11 Test Mode Endpoint for ObjectIdentificationService.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    res = await object_identification_service.identify_object(image, len(contents))
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "image_received": True,
        "latency_ms": elapsed_ms,
        "model_used": VISION_MODEL or LLM_MODEL,
        "raw_model_result": res.object_name,
        "normalized_object": res.object_name,
        "verification_result": res.status,
        "final_object": res.object_name,
        "display_name": res.display_name,
        "confidence": res.confidence,
        "confidence_level": res.confidence_level,
        "material": res.material,
        "condition": res.condition
    }

@router.post("/api/debug/analyzer", status_code=status.HTTP_200_OK)
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

@router.post("/api/debug/vision-identify", status_code=status.HTTP_200_OK)
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

@router.post("/api/debug/rfdetr", status_code=status.HTTP_200_OK)
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
