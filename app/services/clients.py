from contextlib import asynccontextmanager

import aioboto3
from botocore.config import Config
from redis import Redis

from app.config import app_config

config = Config(
    signature_version='s3v4',
    s3={
        'addressing_style': 'path'
    },
    retries={'max_attempts': 3}
)

@asynccontextmanager
async def get_async_s3_client():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=app_config.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=str(app_config.AWS_ACCESS_KEY_ID.get_secret_value()),
        aws_secret_access_key=str(app_config.AWS_SECRET_ACCESS_KEY.get_secret_value()),
        region_name=app_config.AWS_DEFAULT_REGION,
        config=config
    ) as client:
        yield client

redis_client = Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    db=app_config.REDIS_DB
)

