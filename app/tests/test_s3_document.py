import asyncio

import nest_asyncio

from app.components.converters.s3pdf import S3PDFToDocument
from app.config import app_config
from app.db import init_db
from app.models import KnowledgeBaseResource

async def main():
    await init_db()
    id = "689cf5bd4b7d61f6331816d4"
    kb_resource = await KnowledgeBaseResource.get(id)
    s3_pdf_document  = S3PDFToDocument(kb_resource, app_config.AWS_BUCKET_NAME)
    documents = s3_pdf_document.run()
    for doc in documents["documents"]:
        print(doc)

nest_asyncio.apply()
asyncio.run(main())