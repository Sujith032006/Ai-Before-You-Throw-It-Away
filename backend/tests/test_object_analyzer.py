import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.detection import ScanResponse, AnalyzerResult
from app.services.detection_service import process_detection, normalize_object_identity

client = TestClient(app)

def create_dummy_image(width=400, height=400, color=(120, 180, 120)) -> Image.Image:
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([60, 60, 340, 340], fill=(180, 120, 60))
    return img

def create_dummy_image_bytes(width=400, height=400, color=(120, 180, 120)) -> bytes:
    img = create_dummy_image(width, height, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

# ----------------------------------------------------
# 1. MANDATORY CHAIR TEST (Zero Forced Classification)
# ----------------------------------------------------
def test_chair_identification_zero_forced_fallback():
    """A chair MUST remain a chair! MUST NOT return cardboard_box or plastic_bottle."""
    norm = normalize_object_identity("chair", "wood")
    assert norm["name"] == "chair"
    assert norm["base_object"] == "chair"
    assert norm["supported"] is False
    assert norm["name"] != "cardboard_box"
    assert norm["name"] != "plastic_bottle"
    assert norm["name"] != "container"
    assert norm["name"] != "packaging_waste"

def test_laptop_identification():
    """A laptop MUST remain a laptop! Unsupported object."""
    norm = normalize_object_identity("laptop", "metal")
    assert norm["name"] == "laptop"
    assert norm["base_object"] == "laptop"
    assert norm["supported"] is False
    assert norm["name"] != "cardboard_box"
    assert norm["name"] != "plastic_bottle"

def test_table_identification():
    """A table MUST remain a table! Unsupported object."""
    norm = normalize_object_identity("table", "wood")
    assert norm["name"] == "table"
    assert norm["supported"] is False

def test_smartphone_identification():
    """Smartphone -> cell_phone (supported)."""
    norm = normalize_object_identity("smartphone", "glass & electronics")
    assert norm["name"] == "cell_phone"
    assert norm["supported"] is True

def test_keyboard_identification():
    """Keyboard -> keyboard (unsupported)."""
    norm = normalize_object_identity("keyboard", "plastic")
    assert norm["name"] == "keyboard"
    assert norm["supported"] is False

def test_monitor_identification():
    """Monitor -> monitor (unsupported)."""
    norm = normalize_object_identity("monitor", "plastic & glass")
    assert norm["name"] == "monitor"
    assert norm["supported"] is False

def test_shoe_identification():
    """Shoe -> shoe (unsupported)."""
    norm = normalize_object_identity("shoe", "leather")
    assert norm["name"] == "shoe"
    assert norm["supported"] is False

def test_bag_identification():
    """Bag -> bag (unsupported)."""
    norm = normalize_object_identity("bag", "fabric")
    assert norm["name"] == "bag"
    assert norm["supported"] is False

def test_book_identification():
    """Book -> book (supported)."""
    norm = normalize_object_identity("book", "paper")
    assert norm["name"] == "book"
    assert norm["supported"] is True

def test_fan_identification():
    """Fan -> fan (unsupported)."""
    norm = normalize_object_identity("fan", "plastic & metal")
    assert norm["name"] == "fan"
    assert norm["supported"] is False

def test_toy_identification():
    """Toy -> toy (unsupported)."""
    norm = normalize_object_identity("toy", "plastic")
    assert norm["name"] == "toy"
    assert norm["supported"] is False

def test_bicycle_identification():
    """Bicycle -> bicycle (unsupported)."""
    norm = normalize_object_identity("bicycle", "metal")
    assert norm["name"] == "bicycle"
    assert norm["supported"] is False

# ----------------------------------------------------
# 2. SEPARATE OBJECT IDENTITY FROM MATERIAL
# ----------------------------------------------------
def test_bottle_plastic_material():
    """Bottle + Plastic -> plastic_bottle."""
    norm = normalize_object_identity("bottle", "plastic")
    assert norm["name"] == "plastic_bottle"
    assert norm["supported"] is True

def test_bottle_glass_material():
    """Bottle + Glass -> glass_bottle (Must NOT be plastic_bottle!)."""
    norm = normalize_object_identity("bottle", "glass")
    assert norm["name"] == "glass_bottle"
    assert norm["supported"] is True
    assert norm["name"] != "plastic_bottle"

def test_bottle_unknown_material():
    """Bottle + Unknown Material -> bottle (unsupported - never guess plastic!)."""
    norm = normalize_object_identity("bottle", "unknown")
    assert norm["name"] == "bottle"
    assert norm["supported"] is False
    assert norm["name"] != "plastic_bottle"

def test_cardboard_box():
    """Box + Cardboard -> cardboard_box (supported)."""
    norm = normalize_object_identity("box", "cardboard")
    assert norm["name"] == "cardboard_box"
    assert norm["supported"] is True

def test_tin_can():
    """Can + Metal -> tin_can (supported)."""
    norm = normalize_object_identity("can", "metal")
    assert norm["name"] == "tin_can"
    assert norm["supported"] is True

# ----------------------------------------------------
# 3. REACTIVE AI ASSISTANT ENDPOINT TEST
# ----------------------------------------------------
def test_api_assistant_chat_endpoint():
    """Test POST /api/assistant/chat reactive assistant endpoint."""
    resp = client.post(
        "/api/assistant/chat",
        json={
            "message": "I don't have glue.",
            "context": {
                "object": "plastic_bottle",
                "material": "plastic",
                "tools": ["scissors"],
                "materials": ["soil", "string"]
            }
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "answer" in data
    assert len(data["answer"]) > 0
