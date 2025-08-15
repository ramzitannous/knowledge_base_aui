from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.config import app_config
from app.models import KnowledgeBase, KnowledgeBaseResource


async def init_db():
    client = AsyncMongoClient(app_config.MONGODB_URI)
    await init_beanie(
        database=client[app_config.MONGODB_DB],
        document_models=[KnowledgeBase, KnowledgeBaseResource],
    )