from pydantic import BaseModel


class KnowledgeBaseResourceCreate(BaseModel):
    knowledge_base_id: str
    filename: str
    s3_key: str = None
    size: int = None
    version: int = 1

class KnowledgeBaseResourceUpdate(BaseModel):
    filename: str = None
    s3_key: str = None
    size: int = None
    version: int = None