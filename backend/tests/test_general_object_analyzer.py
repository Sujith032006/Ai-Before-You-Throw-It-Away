import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.detection import ScanResponse, AnalyzerResult
from app.services.detection_service import process_detection, normalize_object_identity

client = TestClient(app)

def create_dummy_image(width=400, height=400, color=(100, 200, 100)) -> Image.Image:
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 350, 350], fill=(200, 100, 50))
    return img

def create_dummy_image_bytes(width=400, height=400, color=(100, 200, 100)) -> bytes:
    img = create_dummy_image(width, height, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_normalization_bottle_plastic():
    """Bottle + Plastic -> plastic_bottle (supported)."""
    norm = normalize_object_identity("bottle", "plastic")
    assert norm["name"] == "plastic_bottle"
    assert norm["supported"] is True

def test_normalization_bottle_glass():
    """Bottle + Glass -> glass_bottle (supported)."""
    norm = normalize_object_identity("bottle", "glass")
    assert norm["name"] == "glass_bottle"
    assert norm["supported"] is True

def test_normalization_bottle_unknown_material():
    """Bottle + Unknown Material -> bottle (unsupported - never guess plastic!)."""
    norm = normalize_object_identity("bottle", "unknown")
    assert norm["name"] == "bottle"
    assert norm["supported"] is False

def test_normalization_unsupported_chair():
    """Chair -> chair (unsupported - MUST NOT map to plastic_bottle)."""
    norm = normalize_object_identity("chair", "wood")
    assert norm["name"] == "chair"
    assert norm["base_object"] == "chair"
    assert norm["supported"] is False

def test_normalization_unsupported_laptop():
    """Laptop -> laptop (unsupported - MUST NOT map to plastic_bottle)."""
    norm = normalize_object_identity("laptop", "metal")
    assert norm["name"] == "laptop"
    assert norm["base_object"] == "laptop"
    assert norm["supported"] is False

def test_normalization_unsupported_table():
    """Table -> table (unsupported - MUST NOT map to plastic_bottle)."""
    norm = normalize_object_identity("table", "wood")
    assert norm["name"] == "table"
    assert norm["base_object"] == "table"
    assert norm["supported"] is False

def test_normalization_unsupported_shoe():
    """Shoe -> shoe (unsupported)."""
    norm = normalize_object_identity("shoe", "leather")
    assert norm["name"] == "shoe"
    assert norm["supported"] is False

def test_normalization_unsupported_keyboard():
    """Keyboard -> keyboard (unsupported)."""
    norm = normalize_object_identity("keyboard", "plastic")
    assert norm["name"] == "keyboard"
    assert norm["supported"] is False

def test_normalization_supported_cardboard_box():
    """Box + Cardboard -> cardboard_box (supported)."""
    norm = normalize_object_identity("box", "cardboard")
    assert norm["name"] == "cardboard_box"
    assert norm["supported"] is True

def test_normalization_supported_tin_can():
    """Can + Metal -> tin_can (supported)."""
    norm = normalize_object_identity("can", "metal")
    assert norm["name"] == "tin_can"
    assert norm["supported"] is True

def test_pipeline_return_schema():
    """Test process_detection pipeline returning Two-Stage AnalyzerResult."""
    img = create_dummy_image(400, 400)
    res = process_detection(img, file_size_bytes=5000)
    assert isinstance(res, ScanResponse)
    assert res.analysis is not None
    assert isinstance(res.analysis, AnalyzerResult)
    assert hasattr(res.analysis, "supported")
    assert hasattr(res.analysis, "verification")
    assert hasattr(res.analysis, "confidence_level")
    assert hasattr(res.analysis, "debug_info")

def test_api_general_ideas_endpoint():
    """Test POST /api/general-ideas for unsupported objects."""
    resp = client.post(
        "/api/general-ideas",
        json={"object_name": "chair", "material": "wood"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "ideas" in data
    assert len(data["ideas"]) > 0
    assert "disclaimer" in data
