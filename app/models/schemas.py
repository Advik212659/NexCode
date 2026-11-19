from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Mode(str, Enum):
    FILE = "file"
    CODE = "code"


class NotebookCreate(BaseModel):
    name: str = Field(..., description="Name of the notebook session")


class Notebook(BaseModel):
    id: str
    name: str
    mode: Mode
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    role: str = Field(..., description="User or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    notebook_id: str
    message: str
    mode: Mode
    files: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = "gemini-flash"


class ChatResponse(BaseModel):
    response: str
    token_usage: Dict[str, int]
    files_modified: Optional[List[str]] = None
    steps: List[str]


class TokenUsage(BaseModel):
    current_tokens: int
    max_tokens: int
    percentage: float
    status: str  # "ok", "warning", "critical"


class FileUpload(BaseModel):
    filename: str
    content: str
    size: int
    token_count: int


class WorkspaceInfo(BaseModel):
    name: str
    file_count: int
    total_tokens: int
    status: str
