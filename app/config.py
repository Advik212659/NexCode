from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    max_context_tokens: int = 200000
    port: int = 9000
    google_site_verification: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
