from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    api_title: str = "AI Agent Hub API"
    api_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # Database - uses app user, not admin
    database_url: str = "postgresql://ai_agent_app:ai_agent_app_password@localhost:5435/ai_agent_hub"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
