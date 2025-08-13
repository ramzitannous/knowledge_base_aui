from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):

    # MongoDB
    MONGO_INITDB_ROOT_USERNAME: str = "admin"
    MONGO_INITDB_ROOT_PASSWORD: str = "admin"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "knowledge_base"

    # Postgres
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "knowledge_base"

    # AWS
    AWS_ACCESS_KEY_ID: str = "root"
    AWS_SECRET_ACCESS_KEY: str = "root"
    AWS_S3_ENDPOINT_URL: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str = "knowledge-base"

    # general
    DEBUG: bool = True

    @property
    def MONGODB_URI(self):
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

    class Config:
        env_file = ".env"

app_config = AppConfig()