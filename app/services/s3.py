import uuid

from botocore.client import BaseClient
from botocore.exceptions import ClientError


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


async def download_s3_file_as_bytes(s3_client: BaseClient, bucket: str, key: str) -> bytes:
    """
    Download a file from S3 and return its content as bytes.
    """
    response = await s3_client.get_object(Bucket=bucket, Key=key)
    content = b""
    while True:
        chunk = await response['Body'].read(4096)
        if not chunk:
            break
        content += chunk
    return content


async def s3_file_exists(s3_client: BaseClient, bucket: str, key: str) -> bool:
    """
    Check if a file exists in S3.
    Returns True if the file exists, False otherwise.
    """
    try:
        await s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise


def generate_s3_key(filename: str, version: int) -> str:
    """generate unique key for the file"""
    ext = ""
    if "." in filename:
        splits = filename.split(".")
        filename = splits[0]
        ext = f".{splits[-1]}"
    return f"{filename}_{str(uuid.uuid4())}_{version}{ext}"