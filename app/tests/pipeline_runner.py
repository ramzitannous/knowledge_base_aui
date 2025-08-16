import asyncio

import nest_asyncio

from app.db import init_db
from app.models import KnowledgeBaseResource
from app.schemas.metadata import FileResourceMetadata

async def main():
    from app.components.pipelines.pdf_indexer import pdf_index_pipeline
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


def check_vector_retriever():
    from app.components.pipelines.vector_search import search_pipeline
    filters ={
        "field": "meta.file_resource_id",
        "operator": "==",
        "value": "689cf5bd4b7d61f6331816d4"
    }

    docs = search_pipeline.run({
        "text_embedder": {
            "text": "what is the task about"
        },
        "vector_retriever": {
            "top_k": 5,
            "filters": filters
        }
    })["vector_retriever"]["documents"]
    for doc in docs:
        print(doc.content, doc.score)
        print("-" * 80)

def run_index_pipeline():
    from app.components.pipelines.pdf_indexer import pdf_index_pipeline
    file_resource_id = "689cf5bd4b7d61f6331816d4"
    pdf_index_pipeline.run({
        "s3_fetcher": {
            "resources_metadata": [
                FileResourceMetadata(
                    filename="task.pdf",
                    version=1,
                    knowledge_base_id="689cc5118e25474bca465855",
                    file_resource_id=file_resource_id,
                    s3_key="medical_test_d0ae0eb2-9e76-47ff-9aac-584876868e5b_2.pdf"
                )
            ]
        },
        "pdf_converter": {
            "ocr_enabled": False
        }
    })

if __name__ == "__main__":
    run_index_pipeline()
# nest_asyncio.apply()
# asyncio.run(main())