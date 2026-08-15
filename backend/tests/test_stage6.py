import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.seed import init_db, DEMO_USER_ID

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_health_check_stage6():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "healthy"]
    assert "database" in data
    assert "ai" in data

def test_dashboard_endpoint():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_scans"] >= 1
    assert data["total_projects"] >= 1
    assert data["completed_projects"] >= 0
    assert isinstance(data["recent_activity"], list)

def test_history_endpoint():
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["history"], list)
    assert len(data["history"]) >= 1

def test_complete_project_endpoint():
    project_id = "plastic-bottle-self-watering-planter"
    response = client.post(f"/api/projects/{project_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["project_id"] == project_id

def test_end_to_end_flow_stage6():
    # 1. Recommendation
    rec_payload = {
        "object_name": "bottle",
        "goal": "gardening",
        "tools": ["scissors"],
        "materials": ["soil"],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    rec_resp = client.post("/api/recommendations", json=rec_payload)
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["success"] is True
    top_project_id = rec_data["top_recommendation"]["project_id"]

    # 2. Personalized Guide
    guide_payload = {
        "project_id": top_project_id,
        "object_name": "bottle",
        "goal": "gardening",
        "available_tools": ["scissors"],
        "available_materials": ["soil"],
        "budget_min": 0,
        "budget_max": 50,
        "difficulty": "easy",
        "max_time_minutes": 30
    }
    guide_resp = client.post("/api/projects/personalized-guide", json=guide_payload)
    assert guide_resp.status_code == 200
    guide_data = guide_resp.json()
    assert guide_data["success"] is True

    # 3. AI Assistant Chat
    chat_payload = {
        "message": "I don't have cotton.",
        "project_id": top_project_id,
        "object_name": "bottle",
        "user_context": {"goal": "gardening"},
        "conversation": []
    }
    chat_resp = client.post("/api/chat", json=chat_payload)
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["success"] is True

    # 4. Mark Complete
    comp_resp = client.post(f"/api/projects/{top_project_id}/complete")
    assert comp_resp.status_code == 200
    assert comp_resp.json()["success"] is True

    # 5. Check Dashboard reflects activity
    dash_resp = client.get("/api/dashboard")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["completed_projects"] >= 1
