import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.utils.object_normalization import normalize_object_name
from app.services.detection_service import check_reuse_database_support

client = TestClient(app)

def test_chair_detection_normalization_and_database_isolation():
    """
    CRITICAL REGRESSION TEST: Section 21
    Verifies that a Chair image is normalized as 'chair' and NEVER converted
    into cardboard_box, container, or bottle.
    """
    raw_name = "chair"
    norm = normalize_object_name(raw_name)

    # 1. Physical Object Identity Assertion
    assert norm["object_name"] == "chair"
    assert norm["object_name"] != "cardboard_box"
    assert norm["object_name"] != "container"
    assert norm["object_name"] != "bottle"
    assert norm["object_name"] != "plastic_bottle"

    # 2. Reuse Database Lookup Assertion
    db_res = check_reuse_database_support(norm["object_name"], "wood")

    # Physical Object Identity MUST NOT be overwritten by the database
    assert db_res["base_object"] == "chair"
    assert db_res["name"] == "chair"
    assert db_res["name"] != "cardboard_box"
    assert db_res["name"] != "container"
    assert db_res["name"] != "plastic_bottle"
    assert db_res["supported"] is False  # Chair is outside structured database but correctly identified!

def test_unknown_remains_unknown_strict():
    """
    CRITICAL TEST: Section 8
    Unknown objects MUST remain unknown and NEVER convert into cardboard_box or container.
    """
    raw_name = "unknown"
    norm = normalize_object_name(raw_name)

    assert norm["object_name"] == "unknown"
    assert norm["object_name"] != "cardboard_box"
    assert norm["object_name"] != "container"
    assert norm["object_name"] != "bottle"
