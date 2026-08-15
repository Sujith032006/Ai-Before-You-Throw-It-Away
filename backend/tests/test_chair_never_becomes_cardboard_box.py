import pytest
from app.utils.object_normalization import normalize_object_name
from app.services.detection_service import check_reuse_database_support

def test_chair_never_becomes_cardboard_box():
    """
    CRITICAL PERMANENT REGRESSION TEST (STEP 14):
    Chair image input MUST remain 'chair' and NEVER become 'cardboard_box', 'container', or 'bottle'.
    """
    raw_name = "chair"
    norm = normalize_object_name(raw_name)

    # 1. Physical Object Identity Assertions
    assert norm["object_name"] == "chair"
    assert norm["object_name"] != "cardboard_box"
    assert norm["object_name"] != "container"
    assert norm["object_name"] != "bottle"

    # 2. Database Support Check Assertions
    db_res = check_reuse_database_support(norm["object_name"], "wood")

    # The database ONLY answers if structured projects exist; it NEVER alters the physical identity!
    assert db_res["base_object"] == "chair"
    assert db_res["name"] == "chair"
    assert db_res["name"] != "cardboard_box"
    assert db_res["name"] != "container"
    assert db_res["supported"] is False  # Outside structured database
