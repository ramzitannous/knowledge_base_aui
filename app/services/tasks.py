import asyncio
import logging
import sys

import nest_asyncio
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from rq import Queue

from app.components.pipelines.pdf_indexer import pdf_index_pipeline
from app.config import app_config
from app.db import init_db
from app.models import KnowledgeBaseResource, StatusEnum
from app.schemas.metadata import FileResourceMetadata
from app.services.clients import redis_client

logger = logging.getLogger(__name__)

# rq to process pdf indexing offloaded from server
q = Queue(connection=redis_client)

async def update_knowledge_base_resource_status(kb_resource_id: PydanticObjectId, status: StatusEnum, error=None):
    data_to_update = {
        KnowledgeBaseResource.status:status
    }
    if error:
        data_to_update[KnowledgeBaseResource.error] = error
    await (KnowledgeBaseResource.find_one(KnowledgeBaseResource.id == kb_resource_id)
           .update(Set(data_to_update)))

async def run_pdf_indexing_async(kb_resource_id: PydanticObjectId):
    # initialize beanie on worker startup, todo move to worker startup event
    await init_db()
    logger.info("Running pdf indexing pipeline")
    kb_resource = await KnowledgeBaseResource.get(kb_resource_id)
    metadata = FileResourceMetadata(
        filename=kb_resource.filename,
        version=kb_resource.version,
        knowledge_base_id=str(kb_resource.knowledge_base_id),
        file_resource_id=str(kb_resource.id),
        s3_key=kb_resource.s3_key
    )
    # set as ingesting
    pipeline_data = {
        "s3_fetcher": {
            "resources_metadata": [metadata]
        },
        "pdf_converter": {
            "ocr_enabled": False
        }
    }

    try:
        pdf_index_pipeline.run(pipeline_data)
        # ingestion done
        await update_knowledge_base_resource_status(kb_resource_id, StatusEnum.DONE)
        logger.info("Finished running pdf indexing pipeline")
        return True
    except Exception as e:
        # log exception
        exc_type, exc_value, exc_tb = sys.exc_info()
        error = f"{exc_type}: {exc_value}"
        await update_knowledge_base_resource_status(kb_resource_id, StatusEnum.ERROR, error)
        logger.error("Failed to run pdf indexing pipeline")
        logger.exception(e)
        return False


def run_pdf_indexing_task(kb_resource_id: PydanticObjectId):
    # patch loop to allow calling from nested asyncio loops
    nest_asyncio.apply()
    return asyncio.run(run_pdf_indexing_async(kb_resource_id))


