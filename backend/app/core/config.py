"""Application configuration settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:ombur@localhost:5432/ai_gym_coach"
    DATABASE_TEST_URL: str = "postgresql://postgres:ombur@localhost:5432/ai_gym_coach_test"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM API
    OPENAI_API_KEY: str = ""
    XAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""  # ← ADDED: Groq API key for free fast AI responses

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ← ADDED: This prevents "extra_forbidden" errors
    )


settings = Settings()
