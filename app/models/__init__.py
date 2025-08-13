import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class KnowledgeBase(Document):
    """Knowledge Base model"""
    name: str = Indexed(description="Name of the knowledge base (unique)", unique=True)
    description: str = Field(..., description="Description of the knowledge base")
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    updated_at: Optional[datetime.datetime] = None

    class Settings:
        # mongodb collection name
        name = "knowledge_bases"

class StatusEnum(str, Enum):
    UPLOADING = "uploading"
    INGESTING = "ingesting"
    DONE = "done"
    ERROR = "error"


class KnowledgeBaseResource(Document):
    """Resource file belonging to a Knowledge Base"""
    knowledge_base_id: str = Field(..., description="Reference to KnowledgeBase _id")
    filename: str = Field(..., description="Name of the file")
    s3_key: Optional[str] = Field(None, description="S3 key of the file")
    uploaded_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    version: Optional[int] = Field(1, description="Version of the file")
    status: StatusEnum = Field(StatusEnum.UPLOADING, description="Resource status: active, inactive, or archived")
    error: Optional[str] = Field(None, description="Error message")

    class Settings:
        # mongodb collection name
        name = "knowledge_base_files"
        # todo make unique index
        # indexes = [
        #     # Compound unique index on (knowledge_base_id, filename, version)
        #     [("knowledge_base_id", 1), ("filename", 1),("version", 1), {"unique": True}]
        # ]
