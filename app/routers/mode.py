from fastapi import APIRouter, HTTPException
from app.models.schemas import Mode, ChatRequest, ChatResponse
from typing import Dict, Any
import uuid
from pydantic import BaseModel

router = APIRouter()

# In-memory mode state storage
mode_state: Dict[str, Any] = {
    "current_mode": Mode.FILE,
    "session_id": str(uuid.uuid4())
}


class ModeSwitchRequest(BaseModel):
    mode: str


@router.get("/current")
async def get_current_mode():
    """Get the current execution mode (FILE or CODE)"""
    return {
        "mode": mode_state["current_mode"].value,
        "session_id": mode_state["session_id"]
    }


@router.post("/switch")
async def switch_mode(request: ModeSwitchRequest):
    """Switch between FILE and CODE mode"""
    try:
        new_mode = Mode(request.mode.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    mode_state["current_mode"] = new_mode
    mode_state["session_id"] = str(uuid.uuid4())
    
    return {
        "mode": mode_state["current_mode"].value,
        "session_id": mode_state["session_id"],
        "message": f"Switched to {new_mode.value.upper()} mode"
    }


@router.post("/reset")
async def reset_session():
    """Reset the current session context"""
    mode_state["session_id"] = str(uuid.uuid4())
    return {
        "session_id": mode_state["session_id"],
        "message": "Session reset successfully"
    }
