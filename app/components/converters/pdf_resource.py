import logging
import time
from io import BytesIO
from typing import Any

from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractCliOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker import BaseChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.io import DocumentStream
from docling_haystack.converter import MetaExtractor
from haystack import Document, component
from haystack.dataclasses import ByteStream

from app.config import app_config
from app.schemas.metadata import FileResourceMetadata

"""
    reference: https://docling-project.github.io/docling/examples/rag_haystack/
    reference: https://docling-project.github.io/docling/examples/full_page_ocr/
    chunking strategy: https://docling-project.github.io/docling/examples/hybrid_chunking/
"""

class FileResourceMetaExtractor(MetaExtractor):
    """custom metadata extractor for file resource, that will include filename, version, kb_id, file_resource_id"""

    def extract_chunk_meta(self, chunk: BaseChunk, resources_metadata: FileResourceMetadata) -> dict[str, Any]:
        """Extract chunk meta with extra metadata."""
        return {
                "dl_meta": chunk.export_json_dict(),
                 "knowledge_base_id": resources_metadata.knowledge_base_id,
                 "version": resources_metadata.version,
                 "file_resource_id": resources_metadata.file_resource_id,
                 "filename": resources_metadata.filename
                }

@component
class PDFResourceToDocument:
    """Custom PDF Converter that uses DocumentConverter from docling to extract text from PDFs
        - it will use tesseract as OCR engine to extract text (optional)
        - it will use hybrid chunker
        - it will use MPS accelerator
        - it will support table structure
    """
    def __init__(self):
        self._resources_metadata = []
        self._meta_extractor = FileResourceMetaExtractor()
        self._chunker = HybridChunker(tokenizer=app_config.PIPELINE_CONFIG.EMBEDDING_MODEL)
        self._pipeline_options = PdfPipelineOptions()

        # support table structure
        self._pipeline_options.do_table_structure = True
        self._pipeline_options.table_structure_options.do_cell_matching = True

        # enable MPS accelerator
        self._pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.MPS
        )
        self._doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=self._pipeline_options,
                )
            }
        )

    @component.output_types(documents=list[Document])
    def run(self, streams: list[ByteStream],
            resources_metadata: list[FileResourceMetadata],
            ocr_enabled: bool = False):
        """override DoclingConverter.run to make it work with ByteStream instead of local file path
            and make it work with hybrid chunker only
        """
        self._resources_metadata = resources_metadata
        self._pipeline_options.do_ocr = ocr_enabled
        t1 = time.time()
        # OCR Pipeline options
        if ocr_enabled:
            ocr_options = TesseractCliOcrOptions(force_full_page_ocr=True, lang=["eng"])
            self._pipeline_options.ocr_options = ocr_options

        assert len(streams) == len(self._resources_metadata), "Number of streams and resource metadata must be the same"

        documents: list[Document] = []
        for stream, resources_metadata in zip(streams, self._resources_metadata):
            # convert to docling DocumentStream
            doc_stream = DocumentStream(name=resources_metadata.filename, stream=BytesIO(stream.data))
            dl_doc = self._doc_converter.convert(
                source=doc_stream,
            ).document
            chunk_iter = self._chunker.chunk(dl_doc=dl_doc)
            hs_docs = [
                Document(
                    content=self._chunker.contextualize(chunk=chunk),
                    meta=self._meta_extractor.extract_chunk_meta(chunk=chunk, resources_metadata=resources_metadata),
                )
                for chunk in chunk_iter
            ]
            documents.extend(hs_docs)
        t2 = time.time()
        logging.info(f"total time took to convert PDF file OCR: {ocr_enabled} is: {t2 - t1}")
        return {"documents": documents}
