"""
Fastapi dependencies
"""
from fastapi import Header, HTTPException, status, Depends, Security
from fastapi.security import APIKeyHeader

from app.config import app_config
from app.services.clients import get_async_s3_client


async def s3_dep():
    """
    S3 client dependency
    """
    async with get_async_s3_client() as client:
        yield client

# API Key dependency
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key_header_value: str = Security(api_key_header)):
    if api_key_header_value == app_config.API_KEY:
        return api_key_header_value
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
