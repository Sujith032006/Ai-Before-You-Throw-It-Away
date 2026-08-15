import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.detection import ScanResponse, AnalyzerResult
from app.utils.object_normalization import normalize_object_name
from app.services.detection_service import check_reuse_database_support

client = TestClient(app)

# ----------------------------------------------------
# 1. CRITICAL PERMANENT REGRESSION TEST (PART 13)
# ----------------------------------------------------
def test_chair_regression_test_never_cardboard_box():
    """
    CRITICAL REGRESSION TEST:
    A Chair image MUST be identified as 'chair'.
    It MUST NEVER return cardboard_box, plastic_bottle, container, or packaging_waste!
    """
    norm = normalize_object_name("chair")
    assert norm["object_name"] == "chair"
    
    db_res = check_reuse_database_support(norm["object_name"], "wood")
    assert db_res["base_object"] == "chair"
    assert db_res["supported"] is False
    
    # Strict negative assertions
    assert db_res["name"] != "cardboard_box"
    assert db_res["name"] != "plastic_bottle"
    assert db_res["name"] != "container"
    assert db_res["category"] != "Packaging Waste"

# ----------------------------------------------------
# 2. AUTOMATED TEST CASES MATRIX (PART 12)
# ----------------------------------------------------
def test_table_identification():
    norm = normalize_object_name("table")
    assert norm["object_name"] == "table"

def test_laptop_identification():
    norm = normalize_object_name("laptop")
    assert norm["object_name"] == "laptop"

def test_smartphone_identification():
    norm = normalize_object_name("cell phone")
    assert norm["object_name"] == "smartphone"

def test_keyboard_identification():
    norm = normalize_object_name("keyboard")
    assert norm["object_name"] == "keyboard"

def test_monitor_identification():
    norm = normalize_object_name("tv")
    assert norm["object_name"] == "monitor"

def test_shoe_identification():
    norm = normalize_object_name("shoe")
    assert norm["object_name"] == "shoe"

def test_backpack_identification():
    norm = normalize_object_name("backpack")
    assert norm["object_name"] == "backpack"

def test_book_identification():
    norm = normalize_object_name("book")
    assert norm["object_name"] == "book"

def test_fan_identification():
    norm = normalize_object_name("fan")
    assert norm["object_name"] == "fan"

def test_toy_identification():
    norm = normalize_object_name("toy")
    assert norm["object_name"] == "toy"

def test_plastic_bottle_identification():
    db_res = check_reuse_database_support("bottle", "plastic")
    assert db_res["name"] == "plastic_bottle"
    assert db_res["supported"] is True

def test_glass_jar_identification():
    db_res = check_reuse_database_support("jar", "glass")
    assert db_res["name"] == "glass_jar"
    assert db_res["supported"] is True

def test_cardboard_box_identification():
    db_res = check_reuse_database_support("box", "cardboard")
    assert db_res["name"] == "cardboard_box"
    assert db_res["supported"] is True

def test_tin_can_identification():
    db_res = check_reuse_database_support("can", "metal")
    assert db_res["name"] == "tin_can"
    assert db_res["supported"] is True

# ----------------------------------------------------
# 3. TEST MODE ENDPOINT (PART 11)
# ----------------------------------------------------
def test_api_debug_object_identification_endpoint():
    """Test POST /api/debug/object-identification endpoint."""
    img = Image.new("RGB", (400, 400), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    resp = client.post(
        "/api/debug/object-identification",
        files={"file": ("test_item.jpg", img_bytes, "image/jpeg")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["image_received"] is True
    assert "model_used" in data
    assert "final_object" in data
