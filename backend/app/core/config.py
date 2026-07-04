"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    """App settings — loaded from env vars with sensible defaults."">

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "AI Phone Intelligence OSINT Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment(os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/phone_osint",
    )
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/phone_osint")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── Auth / API Keys ──────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    API_KEY_LENGTH: int = 32

    # ── External APIs ────────────────────────────────────
    # Phone validation / carrier
    NUMVERIFY_API_KEY: Optional[str] = os.getenv("NUMVERIFY_API_KEY")
    ABSTRACT_API_KEY: Optional[str] = os.getenv("ABSTRACT_API_KEY")
    IPQUALITYSCORE_API_KEY: Optional[str] = os.getenv("IPQUALITYSCORE_API_KEY")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")

    # Geolocation
    OPENCELLID_API_KEY: Optional[str] = os.getenv("OPENCELLID_API_KEY")
    OPENCAGE_API_KEY: Optional[str] = os.getenv("OPENCAGE_API_KEY")

    # AI providers
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

    # ── Storage ──────────────────────────────────────────
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
    EXPORT_DIR: Path = Path(os.getenv("EXPORT_DIR", "./data/exports"))

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ── Cell Tower DB (OpenCellID local) ─────────────────
    CELL_TOWER_DB_PATH: str = os.getenv("CELL_TOWER_DB_PATH", "./data/cell_towers.db")


settings = Settings()
