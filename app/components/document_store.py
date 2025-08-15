from haystack.utils import Secret
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from app.config import app_config

pg_connection_string = Secret.from_token(app_config.POSTGRES_URI)
pgvector_document_store = PgvectorDocumentStore(
    connection_string=pg_connection_string,
    recreate_table=False,
    embedding_dimension=app_config.PIPELINE_CONFIG.EMBEDDING_DIMENSION,
    vector_function="cosine_similarity", # function to calculate distance between vectors
    search_strategy="hnsw" #(ANN) algorithm, graph-based index faster than exact_nearest_neighbor
)