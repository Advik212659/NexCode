import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
import os


client = TestClient(app)


def test_create_notebook():
    """Test creating a new notebook"""
    response = client.post("/api/notebook/create", json={"name": "Test Notebook"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Notebook"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["mode"] == "file"


def test_list_notebooks():
    """Test listing all notebooks"""
    # Create a notebook first
    client.post("/api/notebook/create", json={"name": "List Test"})
    
    response = client.get("/api/notebook/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_notebook():
    """Test getting a specific notebook by ID"""
    # Create a notebook
    create_response = client.post("/api/notebook/create", json={"name": "Get Test"})
    notebook_id = create_response.json()["id"]
    
    # Get the notebook
    response = client.get(f"/api/notebook/{notebook_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == notebook_id
    assert data["name"] == "Get Test"


def test_get_nonexistent_notebook():
    """Test getting a notebook that doesn't exist"""
    response = client.get("/api/notebook/nonexistent-id")
    assert response.status_code == 404


def test_delete_notebook():
    """Test deleting a notebook"""
    # Create a notebook
    create_response = client.post("/api/notebook/create", json={"name": "Delete Test"})
    notebook_id = create_response.json()["id"]
    
    # Delete the notebook
    response = client.delete(f"/api/notebook/{notebook_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify it's deleted
    get_response = client.get(f"/api/notebook/{notebook_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_notebook():
    """Test deleting a notebook that doesn't exist"""
    response = client.delete("/api/notebook/nonexistent-id")
    assert response.status_code == 404


def test_update_notebook():
    """Test updating notebook context"""
    # Create a notebook
    create_response = client.post("/api/notebook/create", json={"name": "Update Test"})
    notebook_id = create_response.json()["id"]
    
    # Update the notebook
    context = {"files": {"test.py": "print('hello')"}, "total_tokens": 100}
    response = client.put(f"/api/notebook/{notebook_id}", json=context)
    assert response.status_code == 200
    data = response.json()
    assert data["context"] == context


def test_update_nonexistent_notebook():
    """Test updating a notebook that doesn't exist"""
    response = client.put("/api/notebook/nonexistent-id", json={})
    assert response.status_code == 404


def test_notebook_persistence():
    """Test that notebooks are persisted to storage"""
    # Create a notebook
    response = client.post("/api/notebook/create", json={"name": "Persistence Test"})
    notebook_id = response.json()["id"]
    
    # Check if file exists
    assert os.path.exists("notebook_history.json")
    
    # Clean up
    client.delete(f"/api/notebook/{notebook_id}")


def test_notebook_chronological_order():
    """Test that notebooks are listed in chronological order"""
    # Create multiple notebooks
    ids = []
    for i in range(3):
        response = client.post("/api/notebook/create", json={"name": f"Notebook {i}"})
        ids.append(response.json()["id"])
    
    # List notebooks
    response = client.get("/api/notebook/")
    notebooks = response.json()
    
    # Verify they're in reverse chronological order (newest first)
    # Get the first notebook's updated_at time and compare
    first_updated = notebooks[0]["updated_at"]
    last_updated = notebooks[-1]["updated_at"]
    
    # First should be more recent than last
    assert first_updated >= last_updated
    
    # Clean up
    for notebook_id in ids:
        client.delete(f"/api/notebook/{notebook_id}")


def test_notebook_initialization():
    """Test that notebooks are initialized with correct defaults"""
    response = client.post("/api/notebook/create", json={"name": "Init Test"})
    data = response.json()
    
    assert data["mode"] == "file"  # Default mode
    assert data["context"] is None or data["context"] == {}
    assert "created_at" in data
    assert "updated_at" in data
    
    # Clean up
    client.delete(f"/api/notebook/{data['id']}")
