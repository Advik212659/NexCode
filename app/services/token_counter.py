try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from typing import Dict, List
from app.config import get_settings

settings = get_settings()


class TokenCounter:
    """Token counting and context management service"""
    
    def __init__(self):
        self.max_tokens = settings.max_context_tokens
        
        if TIKTOKEN_AVAILABLE:
            # Use cl100k_base encoding (compatible with many models)
            self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None
            print("Warning: tiktoken not available, using fallback token estimation")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        if not text:
            return 0
        
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: estimate tokens (roughly 4 characters per token)
            return len(text) // 4
    
    def count_tokens_dict(self, data: Dict[str, str]) -> int:
        """Count total tokens in a dictionary of strings"""
        total = 0
        for key, value in data.items():
            total += self.count_tokens(key)
            total += self.count_tokens(value)
        return total
    
    def count_file_tokens(self, filename: str, content: str) -> int:
        """Count tokens for a single file"""
        return self.count_tokens(content)
    
    def count_workspace_tokens(self, files: Dict[str, str]) -> int:
        """Count total tokens for a workspace (multiple files)"""
        total = 0
        for filename, content in files.items():
            total += self.count_file_tokens(filename, content)
        return total
    
    def truncate_to_limit(self, text: str, limit: int = None) -> str:
        """Truncate text to fit within token limit"""
        if limit is None:
            limit = self.max_tokens
        
        if self.encoding:
            tokens = self.encoding.encode(text)
            if len(tokens) <= limit:
                return text
            
            truncated_tokens = tokens[:limit]
            return self.encoding.decode(truncated_tokens)
        else:
            # Fallback: truncate by character count
            estimated_chars = limit * 4
            if len(text) <= estimated_chars:
                return text
            return text[:estimated_chars]
    
    def prioritize_files(
        self,
        files: Dict[str, str],
        max_tokens: int = None
    ) -> Dict[str, str]:
        """Prioritize and truncate files to fit within token budget"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        # Calculate token count for each file
        file_tokens = {}
        for filename, content in files.items():
            file_tokens[filename] = self.count_file_tokens(filename, content)
        
        # Sort by importance (prioritize core code files)
        priority_order = self._get_file_priority_order(list(files.keys()))
        
        # Add files in priority order until budget is reached
        result = {}
        current_tokens = 0
        
        for filename in priority_order:
            if filename not in files:
                continue
            
            file_token_count = file_tokens[filename]
            
            if current_tokens + file_token_count <= max_tokens:
                result[filename] = files[filename]
                current_tokens += file_token_count
            else:
                # Try to include a truncated version
                remaining_budget = max_tokens - current_tokens
                if remaining_budget > 100:  # Minimum threshold
                    truncated = self.truncate_to_limit(
                        files[filename],
                        remaining_budget
                    )
                    result[filename] = truncated
                    current_tokens += remaining_budget
                break
        
        return result
    
    def _get_file_priority_order(self, filenames: List[str]) -> List[str]:
        """Determine priority order for files based on importance"""
        # Priority: main entry points > core logic > config > tests > docs
        priority_keywords = [
            ('main', 100),
            ('app', 95),
            ('index', 90),
            ('__init__', 85),
            ('core', 80),
            ('service', 75),
            ('model', 70),
            ('router', 65),
            ('config', 60),
            ('util', 55),
            ('test', 30),
            ('spec', 25),
            ('readme', 20),
            ('changelog', 15),
        ]
        
        scored = []
        for filename in filenames:
            score = 0
            lower_name = filename.lower()
            
            for keyword, points in priority_keywords:
                if keyword in lower_name:
                    score += points
            
            # Bonus for common code extensions
            if filename.endswith(('.py', '.js', '.ts', '.go', '.rs')):
                score += 50
            elif filename.endswith(('.json', '.yaml', '.yml', '.toml')):
                score += 40
            elif filename.endswith(('.md', '.txt')):
                score += 10
            
            scored.append((filename, score))
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in scored]
    
    def get_usage_percentage(self, current_tokens: int) -> float:
        """Get percentage of token budget used"""
        return (current_tokens / self.max_tokens) * 100
    
    def get_status(self, current_tokens: int) -> str:
        """Get status indicator based on token usage"""
        percentage = self.get_usage_percentage(current_tokens)
        
        if percentage < 70:
            return "ok"
        elif percentage < 90:
            return "warning"
        else:
            return "critical"
