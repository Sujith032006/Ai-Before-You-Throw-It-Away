import io
import time
import logging
from PIL import Image
from fastapi import APIRouter, UploadFile, File, status, HTTPException
from typing import Dict, Any, List

from app.utils.config import (
    LLM_MODE, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
from app.ai.ollama_client import ollama_client
from app.ai.ollama_object_analyzer import ollama_object_analyzer
from app.services.object_identification_service import object_identification_service
from app.services.evaluation_service import run_evaluation_suite

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dev Debugging & Analyzer Endpoints"])

@router.get("/api/analyzer/health", tags=["Analyzer Health"])
@router.get("/api/debug/analyzer/health", tags=["Analyzer Health"])
async def analyzer_health() -> Dict[str, Any]:
    """
    Section 17 Model Availability Check Endpoint.
    Checks Ollama server reachability and Qwen3-VL vision model status.
    """
    return await ollama_client.check_health()

@router.post("/api/analyzer/compare", tags=["Analyzer Comparison"])
@router.post("/api/debug/analyzer/compare", tags=["Analyzer Comparison"])
async def compare_analyzers(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Section 16 Analyzer Endpoint.
    Executes Ollama Qwen3-VL local vision AI.
    """
    start_time = time.time()
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    ollama_result = await ollama_object_analyzer.analyze_image(image)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "latency_ms": elapsed_ms,
        "analyzer": {
            "ollama_qwen3_vl": ollama_result or {"status": "unavailable", "message": "Ollama server not reachable at " + OLLAMA_BASE_URL}
        }
    }

@router.get("/api/debug/evaluate", status_code=status.HTTP_200_OK)
@router.post("/api/debug/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_suite() -> Dict[str, Any]:
    """
    Automated Evaluation Suite Endpoint across 20 object categories.
    """
    return run_evaluation_suite()

@router.get("/api/debug/env-status", status_code=status.HTTP_200_OK)
async def get_env_status() -> Dict[str, Any]:
    """
    Returns environment variable configuration status for debugging.
    """
    return {
        "status": "ok",
        "env_check": {
            "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
            "OLLAMA_MODEL": OLLAMA_MODEL,
            "LLM_MODE": LLM_MODE,
            "LLM_PROVIDER": LLM_PROVIDER,
            "LLM_MODEL": LLM_MODEL,
        }
    }

@router.post("/api/debug/object-identification", status_code=status.HTTP_200_OK)
async def debug_object_identification(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Test Mode Endpoint for ObjectIdentificationService.
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
        "model_used": OLLAMA_MODEL,
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
