"""Typed application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    app_env: str = "development"
    secret_key: SecretStr = SecretStr("unsafe-development-secret-change-before-deploy")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, ge=5, le=10080)
    groq_api_key: SecretStr | None = None
    database_url: str = "sqlite:///./study_buddy.db"
    chroma_persist_dir: Path = Path("./chroma_db")
    upload_dir: Path = Path("./uploads")
    max_upload_size_mb: int = Field(default=20, ge=1, le=200)
    frontend_url: str = "http://localhost:5173"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5500"]
    llm_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "all-MiniLM-L6-v2"
    request_timeout_seconds: float = Field(default=30, gt=0, le=180)

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.app_env.lower() == "production":
            secret = self.secret_key.get_secret_value()
            if secret.startswith("unsafe-") or len(secret) < 32:
                raise ValueError("SECRET_KEY must contain at least 32 non-placeholder characters in production")
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY is required in production")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
