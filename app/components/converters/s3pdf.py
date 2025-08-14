import asyncio

from haystack import component, Document
from haystack.components.converters.pypdf import PyPDFToDocument
from haystack.dataclasses import ByteStream

from app.models import KnowledgeBaseResource
from app.services.clients import get_async_s3_client
from app.services.s3 import download_s3_file_as_bytes, s3_file_exists


@component
class S3PDFToDocument:
    """
     download file from S3 and convert it to haystackDocument
    """
    def __init__(self):
        self._pdf_converter = PyPDFToDocument()


    async def get_file_async(self, kb_resource: KnowledgeBaseResource, bucket_name: str) -> ByteStream:
        async with get_async_s3_client() as client:
            file_exists = await s3_file_exists(client, bucket_name, kb_resource.s3_key)
            if not file_exists:
                raise ValueError("File does not exist in S3")
            file_content = await download_s3_file_as_bytes(client, bucket_name, kb_resource.s3_key)
            return ByteStream(data=file_content)

    @component.output_types(documents=list[Document])
    def run(self, kb_resource: KnowledgeBaseResource, bucket_name: str):
        file_content = asyncio.run(self.get_file_async(kb_resource, bucket_name))
        metadata = {
                    "filename": kb_resource.filename,
                    "version": kb_resource.version,
                    "kb_id": str(kb_resource.knowledge_base_id),
                    "kb_resource_id": str(kb_resource.id),
                    }
        return self._pdf_converter.run(sources=[file_content], meta=metadata)
