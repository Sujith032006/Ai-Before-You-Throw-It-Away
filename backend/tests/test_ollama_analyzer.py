import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.ai.ollama_client import ollama_client
from app.utils.object_normalization import normalize_object_name
from app.services.detection_service import check_reuse_database_support

client = TestClient(app)

def test_ollama_client_json_parsing():
    """Test safe JSON parsing in OllamaClient."""
    raw_response = '```json\n{"status": "identified", "object_name": "chair", "confidence": 0.95}\n```'
    parsed = ollama_client._parse_json_safely(raw_response)
    assert parsed is not None
    assert parsed["object_name"] == "chair"
    assert parsed["confidence"] == 0.95

def test_ollama_health_endpoint():
    """Test GET /api/analyzer/health endpoint (Section 17)."""
    resp = client.get("/api/analyzer/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "ollama"
    assert "model" in data
    assert "status" in data

def test_ollama_compare_endpoint():
    """Test POST /api/analyzer/compare endpoint."""
    img = Image.new("RGB", (300, 300), color=(120, 180, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    resp = client.post(
        "/api/analyzer/compare",
        files={"file": ("test_compare.jpg", img_bytes, "image/jpeg")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "analyzer" in data
    assert "ollama_qwen3_vl" in data["analyzer"]

def test_ollama_chair_never_cardboard_box_regression():
    """Critical Regression: Chair MUST NEVER become cardboard_box."""
    norm = normalize_object_name("chair")
    assert norm["object_name"] == "chair"
    db_res = check_reuse_database_support(norm["object_name"], "wood")
    assert db_res["base_object"] == "chair"
    assert db_res["name"] != "cardboard_box"
