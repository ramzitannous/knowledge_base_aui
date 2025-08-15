from haystack import Pipeline, AsyncPipeline
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder
from haystack_integrations.components.retrievers.pgvector.embedding_retriever import PgvectorEmbeddingRetriever

from app.components.document_store import pgvector_document_store
from app.config import app_config

# pgvector retriever, top_k can be customized when running RAG pipeline
vector_retriever = PgvectorEmbeddingRetriever(
    document_store=pgvector_document_store,
    top_k=app_config.PIPELINE_CONFIG.DEFAULT_TOP_K,
)

text_embedder = FastembedTextEmbedder(model=app_config.PIPELINE_CONFIG.EMBEDDING_MODEL,
                                      parallel=0, progress_bar=True)
# create an async pipeline to be used in the api
search_pipeline = AsyncPipeline()
search_pipeline.add_component("text_embedder", text_embedder)
search_pipeline.add_component("vector_retriever", vector_retriever)

search_pipeline.connect("text_embedder.embedding", "vector_retriever.query_embedding")
