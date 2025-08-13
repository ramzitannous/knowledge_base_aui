from pydantic import BaseModel

from app.models import StatusEnum


class KnowledgeBaseResourceCreate(BaseModel):
    knowledge_base_id: str
    filename: str
    version: int = 1

class KnowledgeBaseResourceUpdate(BaseModel):
    filename: str
    version: int
    status: StatusEnum


class KnowledgeBaseResourcePartialUpdate(BaseModel):
    filename: str = None
    version: int = None
    status: StatusEnum = None