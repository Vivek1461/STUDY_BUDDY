form pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "change-me"
    algorithm : str ="HS256"
    access_token_expire_minutes: int =1440
    groq_api_key: str
    database_url: str
    chroma_persist_dir: str = "./chroma_db"
    upload_dir : str = "./uploads"
    max_upload_size_mb: int = 20
    frontend_url: str ="http://localhost:5173"

    class Config: 
        env_file = ".env"
        case_sensitive = False
#Lru cache is used so the Settings are only Loaded Once, not on every request.
@lru_cache()
def get_settings() -> Settings:
    return Settings()