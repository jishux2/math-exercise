from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import secrets
import os

# 获取项目根目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Math Exercise API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings - SQLite
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/math_exercise.db"

    # AI Service settings
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()