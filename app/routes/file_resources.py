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
        - Create KB resource and return s3_presigned_url to be used to upload the actual file
        - This separation was used to offload the actual file upload from the api
        - Only .pdf file is supported
        1. create s3_presigned_url, if this failed, no resource will be created
        2. create actual resource when s3_presigned_url is ready
    """
    validate_pdf_filename(data.filename)
    s3_presigned_url, s3_key = await service.generate_s3_presigned_url_for_resource(data.filename, data.version, s3_client)
    created_resource = await service.create_resource(data, s3_key)
    return FileResourceCreateResponse(s3_presigned_url=s3_presigned_url,
                                               resource=created_resource)

@router.get("/{knowledge_base_id}/", response_model=List[FileResource],
            status_code=status.HTTP_200_OK)
async def list_resources(knowledge_base_id: str, offset: int = 0, limit: int = 10):
    """
    list resources by knowledge base id
    """
    return await service.list_resources_by_kb(knowledge_base_id=knowledge_base_id, offset=offset, limit=limit)

@router.get("/{file_resource_id}", response_model=FileResource,
            status_code=status.HTTP_200_OK)
@cache(key_builder=build_get_one_cache_key, namespace=FileResource.Settings.name)
async def get_resource(file_resource_id: PydanticObjectId):
    return await service.get_resource(file_resource_id)


@router.put("/{file_resource_id}", response_model=FileResource, status_code=status.HTTP_200_OK)
async def update_resource(file_resource_id: PydanticObjectId, data: FileResourceUpdate):
    """
    - Ingesting file will start once file status is send as `uploaded` or `re_ingest`
    """
    return await service.update_resource(file_resource_id, data)


@router.patch("/{file_resource_id}", response_model=FileResource, status_code=status.HTTP_200_OK)
async def partial_update_resource(file_resource_id: PydanticObjectId, data: FileResourcePartialUpdate):
    """
    - Ingesting file will start once file status is send as `uploaded` or `re_ingest`
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