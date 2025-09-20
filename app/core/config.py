from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend - Optimized"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = "100/minute"
    RATE_LIMIT_PER_HOUR: str = "1000/hour"
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    MAX_CONNECTIONS_PER_USER: int = 10
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Force SQLite for this project
        self.DATABASE_URL = "sqlite:///./sql_app.db"
        self.ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"
    
    # CORS - Allow more origins for production
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5000",
        "https://localhost:3000",
        "https://localhost:8000",
        "https://localhost:5000",
        "*"  # Allow all origins - configure properly in production
    ]
    
    model_config = {"case_sensitive": True}

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()