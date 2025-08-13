from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, status, Response, Query

from app.models import KnowledgeBase
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBasePartialUpdate
from app.services.knowledge_base import (
    create_knowledge_base, list_knowledge_bases, get_knowledge_base,
    update_knowledge_base, delete_knowledge_base
)

router = APIRouter()

@router.post("/", response_model=KnowledgeBase, status_code=status.HTTP_201_CREATED)
async def create_kb_route(data: KnowledgeBaseCreate):
    kb = await create_knowledge_base(data)
    return kb

@router.get("/", response_model=List[KnowledgeBase], status_code=status.HTTP_200_OK)
async def list_kb_route(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    return await list_knowledge_bases(offset=offset, limit=limit)

@router.get("/{kb_id}", response_model=KnowledgeBase, status_code=status.HTTP_200_OK)
async def get_kb_route(kb_id: PydanticObjectId):
    kb = await get_knowledge_base(kb_id)
    return kb

@router.put("/{kb_id}", response_model=KnowledgeBase, status_code=status.HTTP_200_OK)
async def update_kb_route(kb_id: PydanticObjectId, data: KnowledgeBaseUpdate):
    kb = await update_knowledge_base(kb_id, data)
    return kb

@router.patch("/{kb_id}", response_model=KnowledgeBase, status_code=status.HTTP_200_OK)
async def patch_kb_route(kb_id: PydanticObjectId, data: KnowledgeBasePartialUpdate):
    kb = await update_knowledge_base(kb_id, data, partial=True)
    return kb

@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kb_route(kb_id: PydanticObjectId):
    deleted = await delete_knowledge_base(kb_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
