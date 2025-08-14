import asyncio
import logging
import sys

from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from rq import Queue

from app.components.pipelines.pdf_indexer import pdf_index_pipeline
from app.config import app_config
from app.db import init_db
from app.models import KnowledgeBaseResource, StatusEnum
from app.services.clients import redis_client
import nest_asyncio
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
    # set as ingesting
    pipeline_data = {
        "pdf_converter": {
            "kb_resource": kb_resource,
            "bucket_name": app_config.AWS_BUCKET_NAME
        }
    }
    try:
        pdf_index_pipeline.run(pipeline_data)
        # ingestion done
        await update_knowledge_base_resource_status(kb_resource_id, StatusEnum.DONE)
        logger.info("Finished running pdf indexing pipeline")
    except Exception as e:
        # log exception
        exc_type, exc_value, exc_tb = sys.exc_info()
        error = f"{exc_type}: {exc_value}"
        await update_knowledge_base_resource_status(kb_resource_id, StatusEnum.ERROR, error)
        logger.error("Failed to run pdf indexing pipeline")
        logger.exception(e)

def run_pdf_indexing_task(kb_resource_id: PydanticObjectId):
    # patch loop to allow calling from nested asyncio loops
    nest_asyncio.apply()
    asyncio.run(run_pdf_indexing_async(kb_resource_id))


