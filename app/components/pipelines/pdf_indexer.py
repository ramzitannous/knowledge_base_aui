from haystack import Pipeline
from haystack.components.preprocessors import DocumentCleaner, RecursiveDocumentSplitter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import Secret
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.components.writers import DocumentWriter
from app.components.converters.s3pdf import S3PDFToDocument
from app.config import app_config
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder

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
s3_pdf_converter = S3PDFToDocument()
pdf_cleaner = DocumentCleaner()
# fast embed using CPU on all cores (parallel=0)
pdf_embedder = FastembedDocumentEmbedder(model=app_config.PIPELINE_CONFIG.EMBEDDING_MODEL,
                                                progress_bar=True,
                                         parallel=0)
pdf_embedder.warm_up()

pdf_splitter = RecursiveDocumentSplitter(
    split_length=app_config.PIPELINE_CONFIG.SPLIT_SIZE,
    split_overlap=app_config.PIPELINE_CONFIG.SPLIT_OVERLAP,
    separators=app_config.PIPELINE_CONFIG.SEPARATORS,
    split_unit=app_config.PIPELINE_CONFIG.SPLIT_UNIT
)

# create a pipeline
pdf_index_pipeline = Pipeline()
pdf_index_pipeline.add_component("pdf_converter", s3_pdf_converter)
pdf_index_pipeline.add_component("pdf_cleaner", pdf_cleaner)
pdf_index_pipeline.add_component("pdf_splitter", pdf_splitter)
pdf_index_pipeline.add_component("pdf_embedder", pdf_embedder)
pdf_index_pipeline.add_component("document_writer", document_writer)

# connect components to pipeline, since all use the same input, output as documents, no need to specify
pdf_index_pipeline.connect("pdf_converter", "pdf_cleaner")
pdf_index_pipeline.connect("pdf_cleaner", "pdf_splitter")
pdf_index_pipeline.connect("pdf_splitter", "pdf_embedder")
pdf_index_pipeline.connect("pdf_embedder", "document_writer")
