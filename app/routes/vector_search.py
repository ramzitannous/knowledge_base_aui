from fastapi import APIRouter
from starlette import status

from app.components.helpers import build_pipeline_input
from app.components.pipelines.vector_search import search_pipeline
from app.schemas.vector_search import VectorSearchResponse, SearchInput

api_router = APIRouter(prefix="/vector-search", tags=["Vector Search"])

@api_router.post("", response_model=list[VectorSearchResponse], status_code=status.HTTP_200_OK)
async def vector_search_post(data: SearchInput):
    """
    Vector Search API
    -----------------
    Perform semantic search over indexed documents using vector embeddings.

    - **Input:** Query string, top_k, optional metadata filters
    - **Output:** List of documents ranked by semantic similarity
    - **Use Case:** Retrieve relevant documents for a query using vector similarity (e.g., for RAG or search UX)
    """
    top_k = data.top_k
    query = data.query
    pipeline_input = build_pipeline_input(top_k, query, data.metadata_filters)

    # run async pipeline, it will benefit from async retriever
    results = await search_pipeline.run_async(pipeline_input)

    # build response object
    response = []
    documents = results["vector_retriever"]["documents"]
    sorted_documents = sorted(documents, key=lambda doc: doc.score, reverse=True)
    for doc in sorted_documents:
        response.append(VectorSearchResponse.construct_from_document(doc))
    return response