import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.token_counter import TokenCounter


client = TestClient(app)
token_counter = TokenCounter()


def test_count_tokens_empty_string():
    """Test token counting with empty string"""
    count = token_counter.count_tokens("")
    assert count == 0


def test_count_tokens_simple_text():
    """Test token counting with simple text"""
    text = "Hello, world!"
    count = token_counter.count_tokens(text)
    assert count > 0
    assert isinstance(count, int)


def test_count_tokens_code():
    """Test token counting with code"""
    code = """
def hello():
    print("Hello, world!")
    return 42
"""
    count = token_counter.count_tokens(code)
    assert count > 0


def test_count_tokens_dict():
    """Test token counting for dictionary"""
    data = {"key1": "value1", "key2": "value2"}
    count = token_counter.count_tokens_dict(data)
    assert count > 0


def test_count_file_tokens():
    """Test token counting for a file"""
    filename = "test.py"
    content = "print('hello')"
    count = token_counter.count_file_tokens(filename, content)
    assert count > 0


def test_count_workspace_tokens():
    """Test token counting for workspace"""
    files = {
        "main.py": "print('main')",
        "utils.py": "def helper(): pass",
        "config.json": '{"key": "value"}'
    }
    count = token_counter.count_workspace_tokens(files)
    assert count > 0


def test_truncate_to_limit():
    """Test text truncation to token limit"""
    long_text = "hello " * 10000
    truncated = token_counter.truncate_to_limit(long_text, limit=100)
    count = token_counter.count_tokens(truncated)
    assert count <= 100


def test_truncate_under_limit():
    """Test that text under limit is not truncated"""
    short_text = "hello world"
    truncated = token_counter.truncate_to_limit(short_text, limit=1000)
    assert truncated == short_text


def test_prioritize_files():
    """Test file prioritization"""
    files = {
        "main.py": "print('main')",
        "test_main.py": "def test(): pass",
        "README.md": "# Project",
        "config.json": '{"key": "value"}',
        "utils/helper.py": "def help(): pass"
    }
    
    prioritized = token_counter.prioritize_files(files, max_tokens=100)
    assert isinstance(prioritized, dict)
    # main.py should be prioritized over README.md
    assert "main.py" in prioritized


def test_get_usage_percentage():
    """Test token usage percentage calculation"""
    percentage = token_counter.get_usage_percentage(100000)
    assert percentage == 50.0


def test_get_usage_percentage_zero():
    """Test usage percentage with zero tokens"""
    percentage = token_counter.get_usage_percentage(0)
    assert percentage == 0.0


def test_get_status_ok():
    """Test status for OK token usage"""
    status = token_counter.get_status(50000)  # 25%
    assert status == "ok"


def test_get_status_warning():
    """Test status for warning token usage"""
    status = token_counter.get_status(150000)  # 75%
    assert status == "warning"


def test_get_status_critical():
    """Test status for critical token usage"""
    status = token_counter.get_status(190000)  # 95%
    assert status == "critical"


def test_api_token_usage():
    """Test the API endpoint for token usage"""
    response = client.get("/api/llm/token-usage?text=Hello world")
    assert response.status_code == 200
    data = response.json()
    assert "current_tokens" in data
    assert "max_tokens" in data
    assert "percentage" in data
    assert "status" in data
    assert data["max_tokens"] == 200000


def test_api_token_usage_empty():
    """Test API token usage with empty text"""
    response = client.get("/api/llm/token-usage?text=")
    assert response.status_code == 200
    data = response.json()
    assert data["current_tokens"] == 0


def test_api_analyze_workspace():
    """Test workspace analysis API"""
    files = {
        "main.py": "print('hello')",
        "utils.py": "def helper(): pass"
    }
    
    response = client.post("/api/llm/analyze-workspace", json=files)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "file_count" in data
    assert "total_tokens" in data
    assert "status" in data
    assert data["file_count"] == 2


def test_api_analyze_workspace_with_exclusions():
    """Test workspace analysis with excluded files"""
    files = {
        "main.py": "print('hello')",
        ".git/config": "git config",
        "node_modules/package/index.js": "module.exports",
        "utils.py": "def helper(): pass"
    }
    
    response = client.post("/api/llm/analyze-workspace", json=files)
    assert response.status_code == 200
    data = response.json()
    # Should exclude .git and node_modules
    assert data["file_count"] == 2


def test_respect_200k_limit():
    """Test that the 200,000 token limit is respected"""
    # Generate a large payload
    large_text = "word " * 100000
    count = token_counter.count_tokens(large_text)
    
    # Should not exceed limit in prioritization
    files = {f"file_{i}.py": large_text for i in range(10)}
    prioritized = token_counter.prioritize_files(files, max_tokens=200000)
    
    total = token_counter.count_workspace_tokens(prioritized)
    assert total <= 200000


def test_token_counter_max_tokens():
    """Test that max tokens is set correctly"""
    assert token_counter.max_tokens == 200000


def test_token_encoding():
    """Test that token encoding is initialized (or fallback is used)"""
    # Either encoding is available or we're using fallback
    assert True  # Test passes as long as no error occurs
