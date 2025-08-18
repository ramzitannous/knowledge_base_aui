import asyncio

import nest_asyncio

from app.services.db import init_db
from hayhooks import streaming_generator
from rich.console import Console
from rich.markdown import Markdown

from app.components.pipelines.rag import rag_pipeline
from app.models import FileResource
from app.schemas.metadata import FileResourceMetadata

console = Console()


async def main():
    from app.components.pipelines.pdf_indexer import pdf_index_pipeline
    await init_db()
    id = "68a23cb43891a6b7746c311b"
    kb_resource = await FileResource.get(id)
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
            "ocr_enabled": True
        }
    })
    for doc in documents["pdf_converter"]["documents"]:
        console.print(Markdown(doc.content))
        console.print("-" * 80)

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
        console.print(Markdown(doc.content), Markdown(f"score: {doc.score}"))
        console.print("-" * 80)

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

def run_rag_pipeline():
    text = "what is this task about ?"
    pipeline_data = {
        "text_embedder": {
            "text": text
        },
        "prompt_builder": {
            "query": text
        }
    }
    # make pipeline support streaming
    generator_async = streaming_generator(
            pipeline=rag_pipeline,
            pipeline_run_args=pipeline_data)
    for result in generator_async:
        console.print(result.content, end="")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())