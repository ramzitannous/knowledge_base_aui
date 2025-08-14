import asyncio
import datetime
import logging

from botocore.client import BaseClient

from app.config import app_config
from app.models import KnowledgeBaseResource, KnowledgeBase, StatusEnum
from app.schemas.knowledge_base_resources import KnowledgeBaseResourceCreate, KnowledgeBaseResourceUpdate, \
    KnowledgeBaseResourcePartialUpdate
from beanie import PydanticObjectId
from app.exceptions import ResourceConflict, ResourceNotFound
from app.services.s3 import generate_s3_key, generate_presigned_url
from app.services.tasks import run_pdf_indexing_task, q


async def generate_s3_presigned_url_for_resource(filename: str, version: int, s3_client: BaseClient) -> tuple[str, str]:
    s3_key = generate_s3_key(filename, version)
    s3_presigned_url = await generate_presigned_url(s3_client, app_config.AWS_BUCKET_NAME, s3_key)
    return s3_presigned_url, s3_key

async def create_resource(data: KnowledgeBaseResourceCreate, s3_key: str) -> KnowledgeBaseResource:
    # Ensure the knowledge base exists
    kb = await KnowledgeBase.get(data.knowledge_base_id)
    if not kb:
        raise ResourceNotFound("Knowledge base not found")
    resource = KnowledgeBaseResource(**data.model_dump(), s3_key=s3_key)
    try:
        await resource.insert()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise ResourceConflict("Resource with this filename, version, and knowledge_base_id already exists.")
        raise
    return resource

async def get_resource(resource_id: PydanticObjectId) -> KnowledgeBaseResource:
    resource = await KnowledgeBaseResource.get(resource_id)
    if not resource:
        raise ResourceNotFound("Resource not found")
    return resource

def validate_status_transition(current_status: str, new_status: str):
    """
    Enforce allowed status transitions:
    no_file -> uploading -> uploaded
    uploaded -> ingesting -> done internally changed
    'error' can be set from any status at any time
    """
    if new_status == StatusEnum.ERROR:
        return
    status_flow = [
        StatusEnum.NO_FILE,
        StatusEnum.UPLOADING,
        StatusEnum.UPLOADED,
    ]
    try:
        current_index = status_flow.index(current_status)
        next_allowed = status_flow[current_index + 1] if current_index + 1 < len(status_flow) else None
    except ValueError:
        next_allowed = None
    if new_status != next_allowed:
        raise ResourceConflict(f"Invalid status transition: {current_status} -> {new_status}")

async def update_resource(resource_id: PydanticObjectId, data: KnowledgeBaseResourceUpdate | KnowledgeBaseResourcePartialUpdate, partial = False) -> KnowledgeBaseResource:
    resource = await KnowledgeBaseResource.get(resource_id)
    logging.info(data)

    if not resource:
        raise ResourceNotFound("Resource not found")

    # same status cannot be updated
    if resource.status == data.status:
        raise ResourceConflict("Can't update resource with same status")

    validate_status_transition(resource.status, data.status)

    update_data = data.model_dump(exclude_unset=partial)
    updated_at = datetime.datetime.now(datetime.timezone.utc)
    update_data["updated_at"] = updated_at

    # run pdf indexing
    if data.status == StatusEnum.UPLOADED:
        logging.info("Running pdf indexing pipeline")
        loop = asyncio.get_event_loop()
        enqueue_task = lambda: q.enqueue(run_pdf_indexing_task, resource_id)

        # need to run in separate thread, enqueue_task is blocking call
        job = await loop.run_in_executor(None, enqueue_task)
        update_data["job_id"] = job.id
        # update_data["status"] = StatusEnum.INGESTING

    # for key, value in update_data.items():
    #     setattr(resource, key, value)
    # try:
    #     await resource.save()
    # except Exception as e:
    #     if hasattr(e, "details") and "E11000" in str(e):
    #         raise ResourceConflict("Resource with this filename, version, and knowledge_base_id already exists.")
    #     raise
    return resource

async def delete_resource(resource_id: PydanticObjectId) -> None:
    resource = await KnowledgeBaseResource.get(resource_id)
    if not resource:
        raise ResourceNotFound("Resource not found")
    await resource.delete()

async def list_resources_by_kb(knowledge_base_id: str, offset: int = 0, limit: int = 100) -> list[KnowledgeBaseResource]:
    kb = await KnowledgeBase.get(knowledge_base_id)
    if not kb:
        raise ResourceNotFound("Knowledge base not found")
    return await KnowledgeBaseResource.find(KnowledgeBaseResource.knowledge_base_id == knowledge_base_id).skip(offset).limit(limit).to_list()
