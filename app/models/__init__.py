import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class KnowledgeBase(Document):
    """Knowledge Base model"""
    name: str = Indexed(..., description="Name of the knowledge base (unique)", unique=True)
    description: str = Field(..., description="Description of the knowledge base")
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    updated_at: Optional[datetime.datetime] = None

    class Settings:
        # mongodb collection name
        name = "knowledge_bases"

class KnowledgeBaseResource(Document):
    """Knowledge Base Resource model"""
    knowledge_base_id: str = Field(..., description="Reference to KnowledgeBase _id")
    filename: str = Field(..., description="Name of the file")
    s3_key: Optional[str] = Field(None, description="S3 key of the file")
    uploaded_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    version: Optional[int] = Field(1, description="Version of the file")

    class Settings:
        # mongodb collection name
        name = "knowledge_base_files"
        indexes = [
            # Compound unique index on (knowledge_base_id, filename, version)
            [("knowledge_base_id", 1), ("filename", 1),("version", 1), {"unique": True}]
        ]

