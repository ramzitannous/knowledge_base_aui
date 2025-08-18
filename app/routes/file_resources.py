from typing import List

from app.services.cache import build_get_one_cache_key
from beanie import PydanticObjectId
from botocore.client import BaseClient
from fastapi import APIRouter, status, Depends
from fastapi.params import Query
from fastapi_cache.decorator import cache

from app.config import app_config
from app.deps import s3_dep
from app.models import FileResource
from app.schemas.file_resources import (
    FileResourceCreate,
    FileResourceUpdate,
    FileResourcePartialUpdate,
    FileResourceCreateResponse,
    validate_pdf_filename,
)
from app.services import file_resources as service
from app.services.s3 import delete_s3_file

router = APIRouter(prefix="/file-resources", tags=["File Resources"])

@router.post("/", response_model=FileResourceCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(data: FileResourceCreate, s3_client: BaseClient = Depends(s3_dep)):
    """
    Create a new FileResource and get an S3 presigned URL for upload.

    - **Step 1:** Client sends file metadata (filename, version, knowledge_base_id).
    - **Step 2:** API returns an S3 presigned URL for direct PDF upload and creates the resource.
    - **Step 3:** Client uploads the file to S3 using the URL.
    - **Step 4:** Client must update the resource status to 'uploaded' to trigger ingestion.

    Only PDF files are supported. If presigned URL generation fails, no resource is created.
    """
    validate_pdf_filename(data.filename)
    s3_presigned_url, s3_key = await service.generate_s3_presigned_url_for_resource(data.filename, data.version, s3_client)
    created_resource = await service.create_resource(data, s3_key)
    return FileResourceCreateResponse(s3_presigned_url=s3_presigned_url,
                                               resource=created_resource)

@router.get(
    "/{knowledge_base_id}/",
    response_model=List[FileResource],
    status_code=status.HTTP_200_OK,
)
async def list_resources(
    knowledge_base_id: str,
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return (1-100)"),
):
    """List file resources for a knowledge base with pagination (offset, limit)."""
    return await service.list_resources_by_kb(knowledge_base_id=knowledge_base_id, offset=offset, limit=limit)

@router.get("/{file_resource_id}", response_model=FileResource,
            status_code=status.HTTP_200_OK)
@cache(key_builder=build_get_one_cache_key, namespace=FileResource.Settings.name)
async def get_resource(file_resource_id: PydanticObjectId):
    return await service.get_resource(file_resource_id)


@router.put("/{file_resource_id}", response_model=FileResource, status_code=status.HTTP_200_OK)
async def update_resource(file_resource_id: PydanticObjectId, data: FileResourceUpdate):
    """
    Fully update a FileResource. Use this to:
    - Set status to `uploaded` after S3 upload (triggers ingestion/indexing)
    - Set status to `re_ingest` to re-process an existing file
    """
    return await service.update_resource(file_resource_id, data)


@router.patch("/{file_resource_id}", response_model=FileResource, status_code=status.HTTP_200_OK)
async def partial_update_resource(file_resource_id: PydanticObjectId, data: FileResourcePartialUpdate):
    """
    Update a FileResource partially. Use this to:
    - Set status to `uploaded` after S3 upload (triggers ingestion/indexing)
    - Set status to `re_ingest` to re-process an existing file (no new upload required)

    `re_ingest` can be triggered from any status except when already ingesting.
    """
    return await service.update_resource(file_resource_id, data, True)


@router.delete("/{file_resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(file_resource_id: PydanticObjectId, delete_file=Query(True, description="Control if you want to Delete file from s3"),
                          s3_client: BaseClient = Depends(s3_dep)):
    # ensure resource exists
    resource = await service.get_resource(file_resource_id)
    if delete_file:
        s3_key = resource.s3_key
        # if file does not exists in s3, no exception will happen, this is by design
        # no need to fail the actual api, if file does not exist
        await delete_s3_file(s3_client, app_config.AWS_BUCKET_NAME, s3_key)
    await resource.delete()