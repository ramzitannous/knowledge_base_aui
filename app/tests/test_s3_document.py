import sys

from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

from app.components.pipelines.pdf_indexer import pgvector_document_store
from app.db import init_db
from app.models import KnowledgeBaseResource


async def main():
    await init_db()
    id = "689cf5bd4b7d61f6331816d4"
    kb_resource = await KnowledgeBaseResource.get(id)
    embedder = FastembedTextEmbedder()
    embedder.warm_up()
    retriever = PgvectorEmbeddingRetriever(document_store=pgvector_document_store)
    embedding = embedder.run("what tech stack is used in this document")
    result = retriever.run(embedding["embedding"], top_k=1)
    print(result)
# nest_asyncio.apply()
# asyncio.run(main())

try:
    raise ValueError("Something went wrong")
except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()

    print(exc_type, exc_value, exc_tb)