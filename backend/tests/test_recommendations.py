import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommendations_bottle_gardening():
    # Scenario 1: Bottle + Gardening + Scissors + Soil
    payload = {
        "object_name": "bottle",
        "goal": "gardening",
        "tools": ["scissors"],
        "materials": ["soil"],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["top_recommendation"] is not None
    top = data["top_recommendation"]
    assert top["project_id"] == "plastic-bottle-self-watering-planter"
    assert top["match_score"] >= 85

def test_recommendations_tincan_storage():
    # Scenario 2: Tin Can + Storage + Paint
    payload = {
        "object_name": "tin_can",
        "goal": "storage",
        "tools": ["scissors"],
        "materials": ["paint"],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["recommendations"]) > 0

def test_recommendations_tshirt_useful():
    # Scenario 3: Old T-Shirt + Useful Item + Scissors
    payload = {
        "object_name": "old_tshirt",
        "goal": "useful_item",
        "tools": ["scissors"],
        "materials": [],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["top_recommendation"]["project_id"] in ["tshirt-shopping-bag", "tshirt-cleaning-cloths"]

def test_deterministic_scoring():
    payload = {
        "object_name": "bottle",
        "goal": "gardening",
        "tools": ["scissors"],
        "materials": ["soil"],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    res1 = client.post("/api/recommendations", json=payload).json()
    res2 = client.post("/api/recommendations", json=payload).json()
    assert res1["top_recommendation"]["match_score"] == res2["top_recommendation"]["match_score"]
    assert res1["top_recommendation"]["project_id"] == res2["top_recommendation"]["project_id"]

def test_get_project_details():
    res = client.get("/api/projects/plastic-bottle-self-watering-planter")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Self-Watering Planter"
    assert len(data["steps"]) > 0

def test_get_nonexistent_project():
    res = client.get("/api/projects/non-existent-id")
    assert res.status_code == 404
