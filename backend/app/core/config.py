"""
Core configuration for the Vibe PDF Platform.
"""
import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_NAME: str = "Vibe PDF Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vibepdf"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # Default cache TTL in seconds

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # LLM Providers
    LLM_PROVIDER_PRIORITY: str = "anthropic,openai,google"
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None

    # Storage
    STORAGE_BACKEND: Literal["local", "google_drive"] = "local"
    LOCAL_STORAGE_PATH: str = "/tmp/vibepdf"
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Recommendations
    RECOMMENDATION_SIMILARITY_THRESHOLD: float = 0.3
    RECOMMENDATION_MAX_ITEMS: int = 20

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Testing
    TESTING: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
