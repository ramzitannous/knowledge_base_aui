from pydantic import BaseModel, Field, field_validator

from app.models import StatusEnum, KnowledgeBaseResource


# Shared validator for filename
def validate_pdf_filename(v: str) -> str:
    if not v or not v.lower().endswith('.pdf'):
        raise ValueError("filename must have a .pdf extension")
    return v

class KnowledgeBaseResourceCreate(BaseModel):
    knowledge_base_id: str
    filename: str
    version: int = 1
    size: int = Field(None, description="Size of the file in bytes")

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        return validate_pdf_filename(v)

class KnowledgeBaseResourceCreateResponse(BaseModel):
    s3_presigned_url: str
    resource: KnowledgeBaseResource

class KnowledgeBaseResourceUpdate(BaseModel):
    filename: str
    status: StatusEnum
    error: str

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        return validate_pdf_filename(v)

class KnowledgeBaseResourcePartialUpdate(BaseModel):
    filename: str = None
    status: StatusEnum = None
    error: str = None

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        if v is not None:
            return validate_pdf_filename(v)
        return v