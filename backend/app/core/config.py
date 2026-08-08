import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobPilot AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jobpilot-super-secret-jwt-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./jobpilot.db")
    
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "SMART_MOCK")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    
    # Resend Email Integration
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "JobPilot AI <onboarding@resend.dev>")
    
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    
    class Config:
        case_sensitive = True

settings = Settings()

os.makedirs(os.path.join(settings.STORAGE_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "screenshots"), exist_ok=True)
