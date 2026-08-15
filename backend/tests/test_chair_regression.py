import pytest
from app.services.object_identification_service import normalize_object_name
from app.services.detection_service import check_reuse_database_support

def test_chair_is_not_cardboard_box():
    """
    Step 13 Critical Bug Regression Test:
    Asserts that a chair image/name MUST NEVER be identified as cardboard_box or container.
    """
    raw_detected_name = "chair"
    norm = normalize_object_name(raw_detected_name)
    
    assert norm["object_name"] == "chair"
    assert norm["object_name"] != "cardboard_box"
    assert norm["object_name"] != "container"
    
    db_res = check_reuse_database_support(norm["object_name"], "plastic")
    
    assert db_res["name"] == "chair"
    assert db_res["name"] != "cardboard_box"
    assert db_res["name"] != "container"
    assert db_res["supported"] is False
    assert db_res["category"] == "Furniture"
