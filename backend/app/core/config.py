import os
import secrets
import logging
from typing import List, Any
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("edupath.config")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_FILE = os.path.join(BACKEND_DIR, "edupath.db").replace("\\", "/")
DEFAULT_UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")

DEFAULT_DEV_SECRET = "edupath-super-secret-development-key-30203f-8b5cf6"

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduPath AI – Intelligent Learning & Career Ecosystem"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_FILE}")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # AI Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Security / JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", DEFAULT_DEV_SECRET)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    AUTH_RATE_LIMIT_PER_MINUTE: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", DEFAULT_UPLOAD_DIR)
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB

    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        extra="ignore"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, data: Any) -> Any:
        if isinstance(data, dict):
            raw = data.get("ALLOWED_ORIGINS") or os.getenv("ALLOWED_ORIGINS")
            if raw and isinstance(raw, str):
                data["CORS_ORIGINS"] = [x.strip() for x in raw.split(",") if x.strip()]
        return data

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT in ("production", "prod"):
            if self.JWT_SECRET == DEFAULT_DEV_SECRET or len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: In production, JWT_SECRET must be explicitly "
                    "configured in the environment with a cryptographically secure key of at least 32 characters."
                )
        return self

settings = Settings()
