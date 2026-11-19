import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import Mode


client = TestClient(app)


def test_get_current_mode():
    """Test getting the current execution mode"""
    response = client.get("/api/mode/current")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "session_id" in data
    assert data["mode"] in ["file", "code"]


def test_switch_mode_to_file():
    """Test switching to FILE mode"""
    response = client.post("/api/mode/switch", json={"mode": "file"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "file"
    assert "session_id" in data
    assert "message" in data


def test_switch_mode_to_code():
    """Test switching to CODE mode"""
    response = client.post("/api/mode/switch", json={"mode": "code"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "code"
    assert "session_id" in data


def test_switch_mode_invalid():
    """Test switching to an invalid mode"""
    response = client.post("/api/mode/switch", json={"mode": "invalid"})
    assert response.status_code == 400


def test_reset_session():
    """Test resetting the session"""
    # First get current session
    initial_response = client.get("/api/mode/current")
    initial_session = initial_response.json()["session_id"]
    
    # Reset session
    reset_response = client.post("/api/mode/reset")
    assert reset_response.status_code == 200
    reset_data = reset_response.json()
    
    # Verify session ID changed
    assert "session_id" in reset_data
    assert reset_data["session_id"] != initial_session


def test_mode_state_persistence():
    """Test that mode state persists across requests"""
    # Switch to file mode
    client.post("/api/mode/switch", json={"mode": "file"})
    
    # Verify mode is file
    response = client.get("/api/mode/current")
    assert response.json()["mode"] == "file"
    
    # Switch to code mode
    client.post("/api/mode/switch", json={"mode": "code"})
    
    # Verify mode is code
    response = client.get("/api/mode/current")
    assert response.json()["mode"] == "code"


def test_session_update_on_mode_switch():
    """Test that session ID updates when mode is switched"""
    # Get initial session
    initial = client.get("/api/mode/current")
    initial_session = initial.json()["session_id"]
    
    # Switch mode
    client.post("/api/mode/switch", json={"mode": "code"})
    
    # Get new session
    new = client.get("/api/mode/current")
    new_session = new.json()["session_id"]
    
    # Session should have changed
    assert new_session != initial_session
