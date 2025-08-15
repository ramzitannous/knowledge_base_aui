import asyncio

import nest_asyncio

from app.components.pipelines.pdf_indexer import pdf_index_pipeline
from app.db import init_db
from app.models import KnowledgeBaseResource
from app.schemas.metadata import FileResourceMetadata


async def main():
    await init_db()
    id = "689cf5bd4b7d61f6331816d4"
    kb_resource = await KnowledgeBaseResource.get(id)
    metadata = FileResourceMetadata(
        filename=kb_resource.filename,
        version=kb_resource.version,
        knowledge_base_id=str(kb_resource.knowledge_base_id),
        file_resource_id=str(kb_resource.id),
        s3_key=kb_resource.s3_key
    )
    documents = pdf_index_pipeline.run({
        "s3_fetcher": {
            "resources_metadata": [metadata]
        },
        "pdf_converter": {
            "ocr_enabled": False
        }
    })
    pdf_index_pipeline.draw(path="pdf_indexing_pipeline.png")



nest_asyncio.apply()
asyncio.run(main())