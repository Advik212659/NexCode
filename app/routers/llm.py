from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, TokenUsage, WorkspaceInfo
from app.services.llm import LLMProvider
from app.services.token_counter import TokenCounter
from typing import Optional
import os

router = APIRouter()

llm_provider = LLMProvider()
token_counter = TokenCounter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat request and return AI response"""
    try:
        # Calculate token usage
        prompt_tokens = token_counter.count_tokens(request.message)
        
        # Check if context exceeds limit
        if request.context and "total_tokens" in request.context:
            total_tokens = request.context["total_tokens"] + prompt_tokens
        else:
            total_tokens = prompt_tokens
        
        # Generate response with selected model
        model = request.model or "gemini-flash"
        response_data = await llm_provider.generate_response(
            message=request.message,
            mode=request.mode,
            context=request.context,
            files=request.files,
            model=model
        )
        
        response_tokens = token_counter.count_tokens(response_data["response"])
        
        return ChatResponse(
            response=response_data["response"],
            token_usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": response_tokens,
                "total_tokens": total_tokens + response_tokens
            },
            files_modified=response_data.get("files_modified"),
            steps=response_data.get("steps", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/token-usage", response_model=TokenUsage)
async def get_token_usage(text: str):
    """Get token count for given text"""
    try:
        token_count = token_counter.count_tokens(text)
        max_tokens = 200000
        percentage = (token_count / max_tokens) * 100
        
        if percentage < 70:
            status = "ok"
        elif percentage < 90:
            status = "warning"
        else:
            status = "critical"
        
        return TokenUsage(
            current_tokens=token_count,
            max_tokens=max_tokens,
            percentage=round(percentage, 2),
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-workspace", response_model=WorkspaceInfo)
async def analyze_workspace(files: dict):
    """Analyze uploaded workspace files and return token usage"""
    try:
        total_tokens = 0
        file_count = 0
        
        for filename, content in files.items():
            # Skip binary files and common exclusions
            if any(excl in filename for excl in ['.git', 'node_modules', 'venv', '__pycache__', '.pyc']):
                continue
            
            tokens = token_counter.count_tokens(content)
            total_tokens += tokens
            file_count += 1
        
        if total_tokens > 200000:
            status = "warning - context truncated"
        else:
            status = "ok"
        
        return WorkspaceInfo(
            name="uploaded-workspace",
            file_count=file_count,
            total_tokens=total_tokens,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
