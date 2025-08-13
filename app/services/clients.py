from contextlib import asynccontextmanager

import aioboto3
from app.config import app_config


@asynccontextmanager
async def get_async_s3_client():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=app_config.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=app_config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=app_config.AWS_SECRET_ACCESS_KEY,
        region_name=app_config.AWS_DEFAULT_REGION,
    ) as client:
        yield client