import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./mplads_sentinel.db"
    JWT_SECRET: str = "8f93e50c451b69d4d5e7178c772c91bdf1e8a2a46641e4d3f3f2255743b59302"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    LLM_API_KEY: str = "mock_key"
    OCR_CONFIG: str = "tesseract"
    STORAGE_CONFIG: str = "local"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
