from typing import Optional

from docling_core.transforms.chunker import DocChunk
from haystack import Document
from pydantic import BaseModel, Field

from app.schemas.metadata import FileResourceMetadataFilters, FileResourceMetadata


class VectorSearchInput(BaseModel):
    query: str = Field(..., description="Natural language query to search for")
    top_k: Optional[int] = Field(None, description="Number of results to return", gt=3, le=100)
    metadata_filters: Optional[FileResourceMetadataFilters] = None


class SourceMetadata(FileResourceMetadata):
    """Source Metadata links to the original document"""
    page_no: int
    section: str


class VectorSearchResponse(BaseModel):
    content: str
    source_metadata: SourceMetadata
    score: float


    @staticmethod
    def construct_from_document(document: Document) -> "VectorSearchResponse":
        """constructs a VectorSearchResponse from a Haystack Document"""
        doc_chunk = DocChunk.model_validate(document.meta["dl_meta"])
        content = document.content

        if doc_chunk.meta.headings:
            section = f"{' / '.join(doc_chunk.meta.headings)}"
        else:
            section = ""
        source_metadata = SourceMetadata(page_no=document.meta.get("page_no", -1),
                                         section=section,
                                         version=document.meta.get("version", 1),
                                         knowledge_base_id=document.meta.get("knowledge_base_id", ""),
                                         file_resource_id=document.meta.get("file_resource_id", ""),
                                         filename=document.meta.get("filename", ""),
                                         s3_key=document.meta.get("s3_key", ""))

        return VectorSearchResponse(content=content,
                                    source_metadata=source_metadata,
                                    score=document.score)

