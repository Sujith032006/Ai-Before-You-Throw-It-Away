import os
import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.detection import ScanResponse, AnalyzerResult
from app.services.detection_service import process_detection
from app.services.image_quality_service import evaluate_image_quality
from app.ai.rfdetr_detector import rfdetr_detector

client = TestClient(app)

def create_dummy_image(width=400, height=400, color=(100, 200, 100)) -> Image.Image:
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, max(51, width-50), max(51, height-50)], fill=(200, 100, 50))
    return img

def create_dummy_image_bytes(width=400, height=400, color=(100, 200, 100)) -> bytes:
    img = create_dummy_image(width, height, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_rfdetr_model_loaded_once():
    """Verify RF-DETR model loads successfully and singleton is initialized."""
    rfdetr_detector.load_model()
    assert rfdetr_detector.model is not None

def test_image_quality_evaluator():
    """Test image quality pre-checker with dark and micro images."""
    good_img = create_dummy_image(400, 400, (120, 120, 120))
    res_good = evaluate_image_quality(good_img, 5000)
    assert res_good["is_acceptable"] is True
    assert res_good["status"] == "ok"

    tiny_img = create_dummy_image(20, 20, (120, 120, 120))
    res_tiny = evaluate_image_quality(tiny_img, 500)
    assert res_tiny["is_acceptable"] is False
    assert res_tiny["status"] == "poor_image_quality"

    dark_img = Image.new("RGB", (400, 400), color=(5, 5, 5))
    res_dark = evaluate_image_quality(dark_img, 5000)
    assert res_dark["is_acceptable"] is False
    assert res_dark["status"] == "poor_image_quality"

def test_process_detection_pipeline():
    """Test full hybrid detection pipeline returning normalized AnalyzerResult."""
    img = create_dummy_image(500, 500, (150, 150, 150))
    scan_res = process_detection(img, file_size_bytes=10000)
    assert isinstance(scan_res, ScanResponse)
    assert scan_res.analysis is not None
    assert isinstance(scan_res.analysis, AnalyzerResult)
    assert scan_res.analysis.source in ["rf_detr", "vision_ai", "hybrid", "quality_check"]

def test_api_scan_and_analyze_endpoints():
    """Test API POST /api/scan and /api/analyze endpoints."""
    img_bytes = create_dummy_image_bytes(400, 400)
    
    # Test POST /api/analyze
    resp_analyze = client.post(
        "/api/analyze",
        files={"file": ("test_item.jpg", img_bytes, "image/jpeg")}
    )
    assert resp_analyze.status_code == 200
    data_a = resp_analyze.json()
    assert data_a["success"] is True
    assert "analysis" in data_a
    assert "object" in data_a["analysis"]

    # Test POST /api/scan
    resp_scan = client.post(
        "/api/scan",
        files={"file": ("test_item.jpg", img_bytes, "image/jpeg")}
    )
    assert resp_scan.status_code == 200
    data_s = resp_scan.json()
    assert data_s["success"] is True
