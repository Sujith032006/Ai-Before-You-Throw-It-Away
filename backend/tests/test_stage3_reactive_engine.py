import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_scenario_1_chair_gardening_scissors_budget50_easy():
    """TEST 1: Chair + Gardening + Scissors + Budget ₹50 + Easy"""
    payload = {
        "object_name": "chair",
        "object": {
            "object_name": "chair",
            "display_name": "Chair",
            "material": "wood",
            "condition": "used"
        },
        "goal": "gardening",
        "tools": ["scissors"],
        "materials": ["soil"],
        "budget_min": 0,
        "budget_max": 50,
        "budget": {"min": 0, "max": 50, "currency": "INR"},
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0
    top = data["recommendations"][0]
    assert top["difficulty"].lower() == "easy"
    assert top["estimated_cost_max"] <= 50

def test_scenario_2_plastic_bottle_storage():
    """TEST 2: Plastic Bottle + Storage + Scissors"""
    payload = {
        "object_name": "plastic_bottle",
        "object": {
            "object_name": "plastic_bottle",
            "display_name": "Plastic Bottle",
            "material": "plastic",
            "condition": "used"
        },
        "goal": "storage",
        "tools": ["scissors"],
        "materials": [],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0

def test_scenario_3_laptop_decoration():
    """TEST 3: Laptop + Decoration"""
    payload = {
        "object_name": "laptop",
        "object": {
            "object_name": "laptop",
            "display_name": "Laptop",
            "material": "metal & plastic",
            "condition": "used"
        },
        "goal": "decoration",
        "tools": [],
        "materials": [],
        "budget_min": 0,
        "budget_max": 100,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0

def test_scenario_4_chair_custom_goal_bedroom():
    """TEST 4: Chair + Custom goal: 'Something for my bedroom'"""
    payload = {
        "object_name": "chair",
        "object": {
            "object_name": "chair",
            "display_name": "Chair",
            "material": "wood",
            "condition": "used"
        },
        "goal": "custom",
        "custom_goal": "Something for my bedroom",
        "tools": ["paint"],
        "materials": ["cloth"],
        "budget_min": 0,
        "budget_max": 100,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0

def test_scenario_5_chair_budget_20():
    """TEST 5: Chair + Budget: ₹20"""
    payload = {
        "object_name": "chair",
        "object": {
            "object_name": "chair",
            "display_name": "Chair",
            "material": "wood",
            "condition": "used"
        },
        "goal": "useful_item",
        "tools": ["scissors"],
        "materials": [],
        "budget_min": 0,
        "budget_max": 20,
        "budget": {"min": 0, "max": 20, "currency": "INR"},
        "difficulty": "easy",
        "max_time_minutes": 15
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0
    top = data["recommendations"][0]
    assert top["estimated_cost_max"] <= 50

def test_scenario_6_chair_only_scissors():
    """TEST 6: Chair + Tools: Only scissors (No drill/hammer)"""
    payload = {
        "object_name": "chair",
        "object": {
            "object_name": "chair",
            "display_name": "Chair",
            "material": "plastic",
            "condition": "used"
        },
        "goal": "gardening",
        "tools": ["scissors"],
        "materials": [],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    resp = client.post("/api/recommendations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    top = data["recommendations"][0]
    # Check that required tools do not insist on drill or heavy power tools
    req_tools = [t.lower() for t in top.get("tools_needed", [])]
    assert "drill" not in req_tools
    assert "hammer" not in req_tools
