from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Force SQLite for this project
        self.DATABASE_URL = "sqlite:///./sql_app.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5000"
    ]
    
    model_config = {"case_sensitive": True}

settings = Settings()