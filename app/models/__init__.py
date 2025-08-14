import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field, validator, field_validator


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
    UPLOADED = "uploaded"
    INGESTING = "ingesting"
    DONE = "done"
    ERROR = "error"
    NO_FILE = "no_file"

    def __str__(self):
        return self.value



class KnowledgeBaseResource(Document):
    """Resource file belonging to a Knowledge Base"""
    knowledge_base_id: str = Field(..., description="Reference to KnowledgeBase _id")
    filename: str = Field(..., description="Name of the file")
    s3_key: Optional[str] = Field(None, description="S3 key of the file")
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    version: Optional[int] = Field(1, description="Version of the file")
    status: StatusEnum = Field(StatusEnum.NO_FILE, description="Resource status")
    error: Optional[str] = Field(None, description="Error message")
    job_id: Optional[str] = Field(None, description="Job ID for async processing")
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    updated_at: Optional[datetime.datetime] = None

    class Settings:
        # mongodb collection name
        # todo rename
        name = "knowledge_base_files"
        # todo make unique index
        # indexes = [
        #     # Compound unique index on (knowledge_base_id, filename, version)
        #     [("knowledge_base_id", 1), ("filename", 1),("version", 1), {"unique": True}]
        # ]
