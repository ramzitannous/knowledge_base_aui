from pydantic import BaseModel, Field, field_validator

from app.models import StatusEnum, FileResource


# Shared validator for filename
def validate_pdf_filename(v: str) -> str:
    if not v or not v.lower().endswith('.pdf'):
        raise ValueError("filename must have a .pdf extension")
    return v

class FileResourceCreate(BaseModel):
    knowledge_base_id: str
    filename: str
    version: int = 1
    size: int = Field(None, description="Size of the file in bytes")

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        return validate_pdf_filename(v)

class FileResourceCreateResponse(BaseModel):
    s3_presigned_url: str
    resource: FileResource

class FileResourceUpdate(BaseModel):
    filename: str
    status: StatusEnum
    error: str

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        return validate_pdf_filename(v)

class FileResourcePartialUpdate(BaseModel):
    filename: str = None
    status: StatusEnum = None
    error: str = None

    @field_validator('filename')
    def filename_must_be_pdf(cls, v):
        if v is not None:
            return validate_pdf_filename(v)
        return v