from fastapi import APIRouter
from starlette import status

from app.components.pipelines.vector_search import search_pipeline
from app.schemas.vector_search import VectorSearchResponse, VectorSearchInput

api_router = APIRouter()

@api_router.post("", response_model=list[VectorSearchResponse], status_code=status.HTTP_200_OK)
async def vector_search_post(data: VectorSearchInput):
    top_k = data.top_k
    query = data.query

    # build retriever filters https://haystack.deepset.ai/tutorials/31_metadata_filtering
    conditions = []
    if data.metadata_filters is not None:
        for key, value in data.metadata_filters.model_dump().items():
            field  = f"meta.{key}"
            if value is not None:
                conditions.append({
                    "field": field,
                    "operator": "==",
                    "value": value
                })
    retriever_filters = {
        "operator": "AND",
        "conditions": conditions
    }

    # optional params
    retriever_params = {}
    if top_k is not None:
        retriever_params["top_k"] = top_k
    if any(cond for cond in retriever_filters["conditions"]):
        retriever_params["filters"] = retriever_filters

    pipeline_input = {
        "text_embedder": {
            "text": query
        }
    }
    # include it if available
    if retriever_params:
        pipeline_input["vector_retriever"] = retriever_params

    # run async pipeline, it will benefit from async retriever
    results = await search_pipeline.run_async(pipeline_input)

    # build response object
    response = []
    documents = results["vector_retriever"]["documents"]
    sorted_documents = sorted(documents, key=lambda doc: doc.score, reverse=True)
    for doc in sorted_documents:
        response.append(VectorSearchResponse.construct_from_document(doc))
    return response