from fastapi import APIRouter, HTTPException, status, Depends
from beanie import PydanticObjectId
from typing import List
from app.schemas.knowledge_base_resources import (
    KnowledgeBaseResourceCreate,
    KnowledgeBaseResourceUpdate,
    KnowledgeBaseResourcePartialUpdate,
)
from app.models import KnowledgeBaseResource
from app.services import knowledge_base_resource as service

router = APIRouter(prefix="/knowledge-base-resources", tags=["Knowledge Base Resources"])

@router.post("/", response_model=KnowledgeBaseResource, status_code=status.HTTP_201_CREATED)
async def create_resource(data: KnowledgeBaseResourceCreate):
    return await service.create_resource(data)

@router.get("/{knowledge_base_id}/", response_model=List[KnowledgeBaseResource])
async def list_resources(knowledge_base_id: str, offset: int = 0, limit: int = 10):
    return await service.list_resources_by_kb(knowledge_base_id=knowledge_base_id, offset=offset, limit=limit)

@router.get("/{resource_id}", response_model=KnowledgeBaseResource)
async def get_resource(resource_id: PydanticObjectId):
    return await service.get_resource(resource_id)


@router.put("/{resource_id}", response_model=KnowledgeBaseResource)
async def update_resource(resource_id: PydanticObjectId, data: KnowledgeBaseResourceUpdate):
    return await service.update_resource(resource_id, data)


@router.patch("/{resource_id}", response_model=KnowledgeBaseResource)
async def partial_update_resource(resource_id: PydanticObjectId, data: KnowledgeBaseResourcePartialUpdate):
    return await service.update_resource(resource_id, data, True)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: PydanticObjectId):
    await service.delete_resource(resource_id)