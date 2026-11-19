import httpx
from typing import Dict, List, Optional, Any
from app.config import get_settings
from app.models.schemas import Mode
import json

settings = get_settings()


class LLMProvider:
    """Unified AI Engine supporting Gemini Flash with optional OpenRouter fallback"""
    
    def __init__(self):
        self.openrouter_api_key = settings.openrouter_api_key
        self.groq_api_key = settings.groq_api_key
        self.max_tokens = settings.max_context_tokens
        
    async def generate_response(
        self,
        message: str,
        mode: Mode,
        context: Optional[Dict[str, Any]] = None,
        files: Optional[List[str]] = None,
        model: str = "openrouter"
    ) -> Dict[str, Any]:
        """Generate AI response using selected model"""
        
        # Construct system prompt based on mode
        if mode == Mode.FILE:
            system_prompt = self._get_file_mode_system_prompt()
        else:
            system_prompt = self._get_code_mode_system_prompt()
        
        # Add context to message if available
        full_message = message
        if context and "workspace_summary" in context:
            full_message = f"Workspace Context:\n{context['workspace_summary']}\n\nUser Request:\n{message}"
        
        # Route to appropriate model
        if model == "groq":
            try:
                return await self._call_groq(system_prompt, full_message, mode, files)
            except Exception as e:
                print(f"Groq API error: {e}")
                # Fallback to OpenRouter
                if self.openrouter_api_key:
                    try:
                        return await self._call_openrouter(system_prompt, full_message, mode, files)
                    except Exception as e2:
                        print(f"OpenRouter fallback error: {e2}")
        else:
            # Default to OpenRouter
            try:
                return await self._call_openrouter(system_prompt, full_message, mode, files)
            except Exception as e:
                print(f"OpenRouter API error: {e}")
                # Fallback to Groq if configured
                if self.groq_api_key:
                    try:
                        return await self._call_groq(system_prompt, full_message, mode, files)
                    except Exception as e2:
                        print(f"Groq fallback error: {e2}")
        
        # Return graceful error if all fail
        return {
            "response": "I apologize, but I'm currently unable to connect to the AI service. Please check your API key configuration or try again later.",
            "files_modified": [],
            "steps": ["Connection failed - check API configuration"]
        }
    
    async def _call_groq(
        self,
        system_prompt: str,
        message: str,
        mode: Mode,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Call Groq API"""
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            response_text = data["choices"][0]["message"]["content"]
            
            return {
                "response": response_text,
                "files_modified": files or [],
                "steps": ["Using Groq", "Generating response"]
            }
    
    async def _call_openrouter(
        self,
        system_prompt: str,
        message: str,
        mode: Mode,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Call OpenRouter API"""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            response_text = data["choices"][0]["message"]["content"]
            
            return {
                "response": response_text,
                "files_modified": files or [],
                "steps": ["Using OpenRouter", "Generating response"]
            }
    
    def _get_file_mode_system_prompt(self) -> str:
        """System prompt for File Mode (repo-level multi-file agent)"""
        return """You are NexCode, an autonomous AI coding assistant in File Mode. You have access to a full codebase and can analyze, modify, and generate code across multiple files.

Your capabilities:
- Analyze repository structure and dependencies
- Search and understand code across files
- Generate Git-like diffs for code changes
- Provide step-by-step explanations of your work
- Prioritize core code files when context is limited

When responding:
1. Break down complex tasks into clear steps
2. Show exactly which files you're modifying
3. Provide code changes in a clear, diff-like format
4. Explain your reasoning for each change
5. Highlight any potential issues or trade-offs

Always be precise and helpful. Focus on production-quality code."""
    
    def _get_code_mode_system_prompt(self) -> str:
        """System prompt for Code Mode (single-file snippet assistant)"""
        return """You are NexCode, an AI coding assistant in Code Mode. You help users with single-file code snippets, debugging, and quick prototyping.

Your capabilities:
- Write and debug code snippets
- Explain code functionality
- Suggest optimizations
- Help with API usage and syntax
- Provide safe, executable examples

When responding:
1. Provide clear, executable code examples
2. Include explanations for complex logic
3. Highlight any edge cases or gotchas
4. Suggest best practices
5. Keep code self-contained when possible

Focus on being helpful and educational. Code snippets should be ready to copy and run."""
