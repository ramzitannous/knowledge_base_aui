from haystack import AsyncPipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder
from haystack_integrations.components.retrievers.pgvector.embedding_retriever import PgvectorEmbeddingRetriever

from app.components.document_store import pgvector_document_store
from app.components.generator import llm_generator
from app.config import app_config

prompt_template = """
    Using the following documents, answer the question below. 
    For each fact or statement in your answer, cite the source in square brackets in a smaller font, e.g., [file_resource_id: {file_resource_id}, page_no:{page_no}]. 
    Base your response only on the information in these documents.
    
    Documents:
    {% for doc in documents %}
    {{ doc.content }}
    {% endfor %}
    
    Sources Metadata:
    {% for doc in documents %}
    - filename: {{ doc.meta.filename }}
      file_resource_id: {{ doc.meta.file_resource_id }}
      page_no: {{ doc.meta.page_no }}
    {% endfor %}
    
    Question: {{ query }}
    Answer (with citations):
"""

prompt_builder = PromptBuilder(template=prompt_template, required_variables=["query", "documents"])
vector_retriever = PgvectorEmbeddingRetriever(
    document_store=pgvector_document_store,
    top_k=app_config.PIPELINE_CONFIG.DEFAULT_TOP_K,
)

text_embedder = FastembedTextEmbedder(model=app_config.PIPELINE_CONFIG.EMBEDDING_MODEL,
                                      parallel=0, progress_bar=True)


# create an async pipeline to be used in the api
rag_pipeline = AsyncPipeline()
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("vector_retriever", vector_retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("generator", llm_generator)

# connect components
rag_pipeline.connect("text_embedder.embedding", "vector_retriever.query_embedding")
rag_pipeline.connect("vector_retriever", "prompt_builder")
rag_pipeline.connect("prompt_builder", "generator")

