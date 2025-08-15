import asyncio

from haystack import component
from haystack.dataclasses import ByteStream

from app.config import app_config
from app.schemas.metadata import FileResourceMetadata
from app.services.clients import get_async_s3_client
from app.services.s3 import s3_file_exists, download_s3_file_as_bytes


@component
class S3FileFetcher:
    """haystack custom component to fetch file from S3"""

    async def fetch_one(self, client,s3_key: str) -> ByteStream | None:
        bucket_name = app_config.AWS_BUCKET_NAME
        file_exists = await s3_file_exists(client, bucket_name, s3_key)
        if not file_exists:
            return None
        file_content = await download_s3_file_as_bytes(client, bucket_name, s3_key)
        return ByteStream(data=file_content)

    async def get_files_async(self, s3_keys: list[str]) -> list[ByteStream | None]:
        async with get_async_s3_client() as client:
            tasks = [self.fetch_one(client, key) for key in s3_keys]
            return await asyncio.gather(*tasks)

    @component.output_types(streams=list[ByteStream], resources_metadata=list[FileResourceMetadata])
    def run(self, resources_metadata: list[FileResourceMetadata]):
        s3_keys = [metadata.s3_key for metadata in resources_metadata]
        streams = asyncio.run(self.get_files_async(s3_keys))
        return {"streams": streams, "resources_metadata": resources_metadata}
