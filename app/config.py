from enum import Enum

from pydantic_settings import BaseSettings

class AppEnv(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"

    def __str__(self):
        return self.value

class PipelineConfig:
    EMBEDDING_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
    SPLIT_SIZE = 400
    SPLIT_OVERLAP = 40
    SEPARATORS = ["\n\n", "\n", " "]
    SPLIT_UNIT = "token"
    # dimension taken from model
    EMBEDDING_DIMENSION = 384

class AppConfig(BaseSettings):
    # MongoDB
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB: str

    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
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

    # pipeline
    PIPELINE_CONFIG: PipelineConfig = PipelineConfig()

    class Config:
        env_file = ".env"

    @property
    def is_local(self):
        return self.APP_ENV == AppEnv.LOCAL

    @property
    def MONGODB_URI(self):
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

    @property
    def POSTGRES_URI(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

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
app_config = AppConfig()