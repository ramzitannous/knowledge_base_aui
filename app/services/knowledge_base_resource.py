from app.models import KnowledgeBaseResource, KnowledgeBase
from app.schemas.knowledge_base_resources import KnowledgeBaseResourceCreate, KnowledgeBaseResourceUpdate, \
    KnowledgeBaseResourcePartialUpdate
from beanie import PydanticObjectId
from app.exceptions import ResourceConflict, ResourceNotFound

async def create_resource(data: KnowledgeBaseResourceCreate) -> KnowledgeBaseResource:
    # Ensure the knowledge base exists
    kb = await KnowledgeBase.get(data.knowledge_base_id)
    if not kb:
        raise ResourceNotFound("Knowledge base not found")
    resource = KnowledgeBaseResource(**data.model_dump())
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

async def update_resource(resource_id: PydanticObjectId, data: KnowledgeBaseResourceUpdate | KnowledgeBaseResourcePartialUpdate, partial = False) -> KnowledgeBaseResource:
    resource = await KnowledgeBaseResource.get(resource_id)
    if not resource:
        raise ResourceNotFound("Resource not found")
    update_data = data.model_dump(exclude_unset=partial)
    for key, value in update_data.items():
        setattr(resource, key, value)
    try:
        await resource.save()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise ResourceConflict("Resource with this filename, version, and knowledge_base_id already exists.")
        raise
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
