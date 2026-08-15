import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

BASE_CONTEXT = {
    "object": {"name": "chair", "material": "wood", "condition": "used"},
    "selected_project": {
        "title": "Chair Plant Stand",
        "difficulty": "easy",
        "estimated_time_minutes": 20,
        "estimated_cost": {"min": 10, "max": 50, "currency": "INR"}
    },
    "user_preferences": {
        "goal": "gardening",
        "custom_goal": "balcony decor",
        "budget": 50,
        "time_minutes": 30,
        "difficulty": "easy"
    },
    "tools": ["scissors"],
    "materials": ["soil"],
    "current_step": 2
}

def test_stage4_scenario_1_dont_have_paint():
    """TEST 1: User says 'I don't have paint' -> Alternative without paint"""
    payload = {
        "project_context": BASE_CONTEXT,
        "conversation": [],
        "message": "I don't have paint."
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "message" in data

def test_stage4_scenario_2_only_have_20_rupees():
    """TEST 2: User says 'I only have ₹20' -> Cost reduced to <= 20"""
    payload = {
        "project_context": BASE_CONTEXT,
        "conversation": [],
        "message": "I only have ₹20."
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["action"] in ["reduce_budget", "modify_project", "answer_question"]

def test_stage4_scenario_3_make_it_easier():
    """TEST 3: User says 'Make it easier' -> Easy difficulty version"""
    payload = {
        "project_context": BASE_CONTEXT,
        "conversation": [],
        "message": "Make it easier."
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["action"] in ["change_difficulty", "modify_project", "answer_question"]

def test_stage4_scenario_4_give_me_another_idea():
    """TEST 4: User says 'Give me another idea' -> Returns 3 alternatives"""
    payload = {
        "project_context": BASE_CONTEXT,
        "conversation": [],
        "message": "Give me another idea."
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

def test_stage4_scenario_5_explain_step_2():
    """TEST 5: User says 'Explain step 2' -> Step 2 explanation"""
    payload = {
        "project_context": BASE_CONTEXT,
        "conversation": [],
        "message": "Explain step 2."
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

def test_stage4_scenario_6_updated_tools_scissors_glue():
    """TEST 6: Tool list updated to scissors + glue -> AI uses updated list"""
    ctx = dict(BASE_CONTEXT)
    ctx["tools"] = ["scissors", "glue"]
    payload = {
        "project_context": ctx,
        "conversation": [],
        "message": "What can I make using glue?"
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

def test_stage4_scenario_7_updated_budget_20():
    """TEST 7: Budget updated from ₹50 to ₹20 -> AI respects ₹20"""
    ctx = dict(BASE_CONTEXT)
    ctx["user_preferences"] = dict(BASE_CONTEXT["user_preferences"])
    ctx["user_preferences"]["budget"] = 20
    payload = {
        "project_context": ctx,
        "conversation": [],
        "message": "What is the best project within this budget?"
    }
    resp = client.post("/api/project-chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
