from pydantic import BaseModel


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str

class KnowledgeBaseUpdate(BaseModel):
    name: str
    description: str

class KnowledgeBasePartialUpdate(BaseModel):
    name: str = None
    description: str = None
