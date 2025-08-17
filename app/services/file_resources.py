import asyncio
import datetime
import logging

from app.services.cache import get_one_cache_key
from beanie import PydanticObjectId
from botocore.client import BaseClient
from fastapi_cache import FastAPICache

from app.config import app_config
from app.exceptions import DBDocumentConflict, DBDocumentNotFound
from app.models import FileResource, KnowledgeBase, StatusEnum
from app.schemas.file_resources import FileResourceCreate, FileResourceUpdate, \
    FileResourcePartialUpdate
from app.services.s3 import generate_s3_key, generate_presigned_url
from app.services.tasks import run_pdf_indexing_task, q


async def generate_s3_presigned_url_for_resource(filename: str, version: int, s3_client: BaseClient) -> tuple[str, str]:
    s3_key = generate_s3_key(filename, version)
    s3_presigned_url = await generate_presigned_url(s3_client, app_config.AWS_BUCKET_NAME, s3_key)
    return s3_presigned_url, s3_key

async def create_resource(data: FileResourceCreate, s3_key: str) -> FileResource:
    # Ensure the knowledge base exists
    kb = await KnowledgeBase.get(data.knowledge_base_id)
    if not kb:
        raise DBDocumentNotFound("Knowledge base not found")
    resource = FileResource(**data.model_dump(), s3_key=s3_key)
    try:
        await resource.insert()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise DBDocumentConflict("Resource with this filename, version, and knowledge_base_id already exists.")
        raise
    return resource

async def get_resource(resource_id: PydanticObjectId) -> FileResource:
    resource = await FileResource.get(resource_id)
    if not resource:
        raise DBDocumentNotFound("Resource not found")
    return resource

def enforce_status_transition(current_status: StatusEnum, new_status: StatusEnum):
    """
    Enforce allowed status transitions:
    no_file -> uploading -> uploaded
    uploaded -> ingesting -> done internally changed
    'error', 're_ingest' can be set from any status at any time,
    except 're_ingest' is NOT allowed if already ingesting
    """
    if new_status == StatusEnum.RE_INGEST:
        if current_status == StatusEnum.INGESTING:
            raise DBDocumentConflict("Cannot re-ingest while file is already ingesting.")
        return
    if new_status == StatusEnum.ERROR:
        return
    status_flow = [
        StatusEnum.NO_FILE,
        StatusEnum.UPLOADING,
        StatusEnum.UPLOADED
    ]
    try:
        current_index = status_flow.index(current_status)
        next_allowed = status_flow[current_index + 1] if current_index + 1 < len(status_flow) else None
    except ValueError:
        next_allowed = None
    if new_status != next_allowed:
        raise DBDocumentConflict(f"Invalid status transition: {current_status} -> {new_status}")

async def update_resource(resource_id: PydanticObjectId, data: FileResourceUpdate | FileResourcePartialUpdate, partial = False) -> FileResource:
    resource = await FileResource.get(resource_id)
    logging.info(data)

    if not resource:
        raise DBDocumentNotFound("Resource not found")

    # same status cannot be updated
    if resource.status == data.status:
        raise DBDocumentConflict("Can't update resource with same status")

    enforce_status_transition(resource.status, data.status)

    update_data = data.model_dump(exclude_unset=partial)
    updated_at = datetime.datetime.now(datetime.timezone.utc)
    update_data["updated_at"] = updated_at

    # run pdf indexing after upload done or re-ingest
    if data.status in [StatusEnum.UPLOADED, StatusEnum.RE_INGEST]:
        logging.info("Running pdf indexing pipeline")
        loop = asyncio.get_event_loop()
        enqueue_task = lambda: q.enqueue(run_pdf_indexing_task, resource_id)

        # need to run in separate thread, enqueue_task is blocking call
        job = await loop.run_in_executor(None, enqueue_task)
        update_data["job_id"] = job.id
        update_data["status"] = StatusEnum.INGESTING

    for key, value in update_data.items():
        setattr(resource, key, value)
    try:
        await resource.save()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise DBDocumentConflict("Resource with this filename, version, and knowledge_base_id already exists.")
        raise
    # invalidate cache
    await FastAPICache.clear(key=get_one_cache_key(FileResource.Settings.name,
                                                   resource_id))
    return resource


async def delete_resource(resource_id: PydanticObjectId) -> None:
    resource = await FileResource.get(resource_id)
    if not resource:
        raise DBDocumentNotFound("Resource not found")
    # invalidate cache
    await FastAPICache.clear(key=get_one_cache_key(FileResource.Settings.name,
                                                   resource_id))
    await resource.delete()

async def list_resources_by_kb(knowledge_base_id: str, offset: int = 0, limit: int = 100) -> list[FileResource]:
    kb = await KnowledgeBase.get(knowledge_base_id)
    if not kb:
        raise DBDocumentNotFound("Knowledge base not found")
    return await FileResource.find(FileResource.knowledge_base_id == knowledge_base_id).skip(offset).limit(limit).to_list()
