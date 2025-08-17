from enum import Enum

import torch
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppEnv(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"

    def __str__(self):
        return self.value

class PipelineConfig:
    EMBEDDING_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
    # dimension taken from model
    EMBEDDING_DIMENSION = 384
    OCR_ENABLED = True
    DEFAULT_TOP_K = 10
    LLM_MODEL = "deepseek/deepseek-chat-v3-0324:free"
    LLM_SYSTEM_PROMPT = """
        You are an AI assistant that retrieves information from a knowledge base consisting of PDF documents.
        Your answers should be based solely on the content provided in these documents.
    """


class AppConfig(BaseSettings):
    # MongoDB
    MONGO_INITDB_ROOT_USERNAME: SecretStr
    MONGO_INITDB_ROOT_PASSWORD: SecretStr
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB: str

    # Postgres
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # AWS
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_S3_ENDPOINT_URL: str
    AWS_DEFAULT_REGION: str
    AWS_BUCKET_NAME: str

    #Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    # general
    APP_ENV: AppEnv
    API_KEY: str
    TOKENIZERS_PARALLELISM: str
    CACHE_PREFIX: str = "fastapi_cache"
    API_RATE_LIMIT: str = "10/minute"

    # 1 hour
    CACHE_TTL: int = 3600

    # pipeline
    PIPELINE_CONFIG: PipelineConfig = PipelineConfig()

    # OpenAI
    OPENAI_API_KEY: SecretStr
    OPENAI_API_BASE_URL: str

    class Config:
        env_file = ".env"

    @property
    def is_local(self):
        return self.APP_ENV == AppEnv.LOCAL

    @property
    def MONGODB_URI(self):
        username = self.MONGO_INITDB_ROOT_USERNAME.get_secret_value()
        password = self.MONGO_INITDB_ROOT_PASSWORD.get_secret_value()
        return f"mongodb://{username}:{password}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

    @property
    def POSTGRES_URI(self):
        username = self.POSTGRES_USER.get_secret_value()
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql://{username}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def REDIS_URI(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def device(self):
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using Apple Silicon GPU via MPS")
        else:
            device = torch.device("cpu")
            print("Using CPU")
        return device

app_config = AppConfig()