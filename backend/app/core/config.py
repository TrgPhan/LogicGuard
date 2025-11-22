from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Support multiple origins for flexible deployment
    FRONTEND_URL: str = "http://localhost:3000"
    # Comma-separated list of allowed origins (optional, defaults to FRONTEND_URL + localhost)
    ALLOWED_ORIGINS: str | None = None
    
    # AI/LLM
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"  # có thể đổi sang phiên bản pro nếu cần chất lượng cao hơn
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()