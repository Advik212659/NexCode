import pytest
import os
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    # Set required environment variables for testing
    os.environ["GEMINI_API_KEY"] = "test_key_for_testing"
    os.environ["MAX_CONTEXT_TOKENS"] = "200000"
    os.environ["PORT"] = "9000"
    
    yield
    
    # Clean up
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("MAX_CONTEXT_TOKENS", None)
    os.environ.pop("PORT", None)
