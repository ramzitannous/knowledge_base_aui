from app.models import KnowledgeBase
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate
from beanie import PydanticObjectId
from app.exceptions import ResourceConflict, ResourceNotFound

async def create_knowledge_base(data: KnowledgeBaseCreate) -> KnowledgeBase:
    kb = KnowledgeBase(**data.model_dump())
    try:
        await kb.insert()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise ResourceConflict("KnowledgeBase with this name already exists.")
        raise
    return kb

async def list_knowledge_bases() -> list[KnowledgeBase]:
    return await KnowledgeBase.find_all().to_list()

async def get_knowledge_base(kb_id: PydanticObjectId) -> KnowledgeBase:
    kb = await KnowledgeBase.get(kb_id)
    if not kb:
        raise ResourceNotFound("KnowledgeBase not found")
    return kb

async def update_knowledge_base(kb_id: PydanticObjectId, data: KnowledgeBaseUpdate) -> KnowledgeBase:
    kb = await KnowledgeBase.get(kb_id)
    if not kb:
        raise ResourceNotFound("KnowledgeBase not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kb, key, value)
    try:
        await kb.save()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise ResourceConflict("KnowledgeBase with this name already exists.")
        raise
    return kb

async def delete_knowledge_base(kb_id: PydanticObjectId) -> None:
    kb = await KnowledgeBase.get(kb_id)
    if not kb:
        raise ResourceNotFound("KnowledgeBase not found")
    await kb.delete()
