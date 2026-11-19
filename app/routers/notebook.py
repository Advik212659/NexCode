from fastapi import APIRouter, HTTPException
from app.models.schemas import Notebook, NotebookCreate, Mode
from typing import List, Dict
from datetime import datetime, timezone
import uuid
import json
import os

router = APIRouter()

# In-memory notebook storage (can be replaced with database)
notebooks: Dict[str, Notebook] = {}
notebook_storage_file = "notebook_history.json"


def load_notebooks():
    """Load notebooks from persistent storage"""
    global notebooks
    if os.path.exists(notebook_storage_file):
        try:
            with open(notebook_storage_file, 'r') as f:
                data = json.load(f)
                for nb_id, nb_data in data.items():
                    # Parse datetimes and ensure they are timezone-aware
                    created_at = datetime.fromisoformat(nb_data['created_at'])
                    updated_at = datetime.fromisoformat(nb_data['updated_at'])
                    
                    # Make timezone-aware if naive
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    if updated_at.tzinfo is None:
                        updated_at = updated_at.replace(tzinfo=timezone.utc)
                    
                    nb_data['created_at'] = created_at
                    nb_data['updated_at'] = updated_at
                    notebooks[nb_id] = Notebook(**nb_data)
        except Exception as e:
            print(f"Error loading notebooks: {e}")


def save_notebooks():
    """Save notebooks to persistent storage"""
    data = {}
    for nb_id, notebook in notebooks.items():
        data[nb_id] = {
            "id": notebook.id,
            "name": notebook.name,
            "mode": notebook.mode.value,
            "created_at": notebook.created_at.isoformat(),
            "updated_at": notebook.updated_at.isoformat(),
            "context": notebook.context
        }
    try:
        with open(notebook_storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving notebooks: {e}")


# Load notebooks on startup
load_notebooks()


@router.post("/create", response_model=Notebook)
async def create_notebook(notebook_data: NotebookCreate):
    """Create a new notebook session"""
    notebook_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    notebook = Notebook(
        id=notebook_id,
        name=notebook_data.name,
        mode=Mode.FILE,
        created_at=now,
        updated_at=now,
        context={}
    )
    
    notebooks[notebook_id] = notebook
    save_notebooks()
    
    return notebook


@router.get("/", response_model=List[Notebook])
async def list_notebooks():
    """List all notebook sessions chronologically"""
    return sorted(
        notebooks.values(),
        key=lambda x: x.updated_at,
        reverse=True
    )


@router.get("/{notebook_id}", response_model=Notebook)
async def get_notebook(notebook_id: str):
    """Get a specific notebook by ID"""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebooks[notebook_id]


@router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str):
    """Delete a notebook session"""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    del notebooks[notebook_id]
    save_notebooks()
    
    return {"message": "Notebook deleted successfully"}


@router.put("/{notebook_id}")
async def update_notebook(notebook_id: str, context: dict):
    """Update notebook context"""
    if notebook_id not in notebooks:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    notebooks[notebook_id].context = context
    notebooks[notebook_id].updated_at = datetime.now(timezone.utc)
    save_notebooks()
    
    return notebooks[notebook_id]
