from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import Secret
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from app.components.converters.pdf_resource import PDFResourceToDocument
from app.components.fetchers.s3 import S3FileFetcher
from app.config import app_config

pg_connection_string = Secret.from_token(app_config.POSTGRES_URI)
pgvector_document_store = PgvectorDocumentStore(
    connection_string=pg_connection_string,
    recreate_table=False,
    embedding_dimension=app_config.PIPELINE_CONFIG.EMBEDDING_DIMENSION,
    search_strategy="hnsw" #(ANN) algorithm, graph-based index faster than exact_nearest_neighbor
)
# use overwriting policy
document_writer = DocumentWriter(document_store=pgvector_document_store,
                                 policy=DuplicatePolicy.OVERWRITE)
s3_fetcher = S3FileFetcher()
# fast embed using CPU on all cores (parallel=0)
pdf_embedder = FastembedDocumentEmbedder(model=app_config.PIPELINE_CONFIG.EMBEDDING_MODEL,
                                                progress_bar=True,
                                         parallel=0)
pdf_embedder.warm_up()

converter = PDFResourceToDocument()

# create a pipeline
pdf_index_pipeline = Pipeline()
pdf_index_pipeline.add_component("s3_fetcher", s3_fetcher)
pdf_index_pipeline.add_component("pdf_converter", converter)
pdf_index_pipeline.add_component("embedder", pdf_embedder)
pdf_index_pipeline.add_component("document_writer", document_writer)

# connect components to pipeline, since all use the same input, output as documents, no need to specify
pdf_index_pipeline.connect("s3_fetcher.streams", "pdf_converter.streams")
pdf_index_pipeline.connect("s3_fetcher.resources_metadata", "pdf_converter.resources_metadata")
pdf_index_pipeline.connect("pdf_converter", "embedder")
pdf_index_pipeline.connect("embedder", "document_writer")
