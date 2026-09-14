form pydantic_settings import BaseSettings
from functools import lru_cache
#pydantic-settings+ pydantic==2.7.1
# ==2.3.0- -----> pydanticsettings is a library Works with pydantic and can read the configuration values from .env files, env variables, default values , other supported configuration sources.
# so instead of using manual Import os and using os.getenv(GROQ_API), os.getenv(DB_URL), BaseSettings handles it.
# form functools import lru_cache    --> (Least Recently used Cache)
# (Built in library in python==functools which contains Lru) |^|---(Allows python to remember the result of a function call so it doesn’t have to execute the function again unnecessarily. )

# creating a python class called as Settings and giving a inheritance of BaseSettings so that using its functionality we can access  BaseSetting functionalities of reading .env variables.
class Settings(BaseSettings):
#    application environment 
#var name(app_env)   Type(str)    = default value("development")
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