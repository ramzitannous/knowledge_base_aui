import uuid

import aiofiles
from botocore.client import BaseClient


async def generate_presigned_url(s3_client: BaseClient, bucket: str, key: str, expires_in=3600):
    """
    Generate a presigned URL for an S3 object.
    """
    return await s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expires_in
    )


async def delete_s3_file(s3_client: BaseClient, bucket: str, key: str):
    """
    Delete a file from an S3 bucket.
    """
    await s3_client.delete_object(Bucket=bucket, Key=key)


async def download_s3_file(s3_client: BaseClient, bucket: str, key: str, download_path: str):
    """
    Download a file from S3 to a local path.
    """
    async with s3_client.get_object(Bucket=bucket, Key=key) as response:
        async with aiofiles.open(download_path, 'wb') as f:
            while True:
                chunk = await response['Body'].read(4096)
                if not chunk:
                    break
                await f.write(chunk)

def generate_s3_key(filename: str, version: int) -> str:
    """generate unique key for the file"""
    ext = ""
    if "." in filename:
        splits = filename.split(".")
        filename = splits[0]
        ext = f".{splits[-1]}"
    return f"{filename}_{str(uuid.uuid4())}_{version}{ext}"