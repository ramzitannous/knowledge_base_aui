import asyncio

import nest_asyncio

from app.components.converters.s3pdf import S3PDFToDocument
from app.config import app_config
from app.db import init_db
from app.models import KnowledgeBaseResource
from app.components.pipelines.pdf_indexer import pdf_index_pipeline

async def main():
    await init_db()
    id = "689cf5bd4b7d61f6331816d4"
    kb_resource = await KnowledgeBaseResource.get(id)
    pdf_index_pipeline.run({
        "pdf_converter": {
            "kb_resource": kb_resource,
            "bucket_name": app_config.AWS_BUCKET_NAME
        }
    })

nest_asyncio.apply()
asyncio.run(main())