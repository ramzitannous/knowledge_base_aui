from app.models import KnowledgeBaseResource
from app.schemas.knowledge_base_resources import KnowledgeBaseResourceCreate, KnowledgeBaseResourceUpdate
from beanie import PydanticObjectId
from app.exceptions import ResourceConflict, ResourceNotFound

async def create_resource(data: KnowledgeBaseResourceCreate) -> KnowledgeBaseResource:
    resource = KnowledgeBaseResource(**data.model_dump())
    try:
        await resource.insert()
    except Exception as e:
        if hasattr(e, "details") and "E11000" in str(e):
            raise ResourceConflict("Resource with this filename, version, and knowledge_base_id already exists.")
        raise
    return resource

async def list_resources() -> list[KnowledgeBaseResource]:
    return await KnowledgeBaseResource.find_all().to_list()

async def get_resource(resource_id: PydanticObjectId) -> KnowledgeBaseResource:
    resource = await KnowledgeBaseResource.get(resource_id)
    if not resource:
        raise ResourceNotFound("Resource not found")
    return resource

async def update_resource(resource_id: PydanticObjectId, data: KnowledgeBaseResourceUpdate) -> KnowledgeBaseResource:
    resource = await KnowledgeBaseResource.get(resource_id)
    if not resource:
        raise ResourceNotFound("Resource not found")
    update_data = data.model_dump(exclude_unset=True)
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
