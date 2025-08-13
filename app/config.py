from pydantic import BaseSettings

class AppConfig(BaseSettings):
    DEBUG: bool
    MONGODB_URI: str
    MONGODB_DB: str

    class Config:
        env_file = ".env"

app_config = AppConfig()