from pydantic import BaseModel


class FileResourceMetadata(BaseModel):
    """File resource metadata to be included in chunk meta"""
    filename: str
    version: int
    knowledge_base_id: str
    file_resource_id: str
    s3_key: str
