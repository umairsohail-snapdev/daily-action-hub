from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# backend/app/config.py -> backend/app -> backend
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GROQ_API_KEY: str = ""
    SECRET_KEY: str = "super-secret-fixed-dev-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5137")
    
    # Integrations
    NOTION_API_KEY: str = ""
    NOTION_DATABASE_ID: str = ""
    GRANOLA_API_KEY: str = ""
    NOTION_CLIENT_ID: str = ""
    NOTION_CLIENT_SECRET: str = ""

    class Config:
        env_file = str(BASE_DIR / ".env")
        extra = "ignore" # Ignore extra fields in .env

settings = Settings()