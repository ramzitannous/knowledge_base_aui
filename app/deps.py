"""
Fastapi dependencies
"""
from app.services.clients import get_async_s3_client


async def s3_dep():
    """
    S3 client dependency
    """
    async with get_async_s3_client() as client:
        yield client