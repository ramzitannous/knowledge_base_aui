from typing import Generator

from fastapi import APIRouter
from hayhooks import streaming_generator
from haystack.dataclasses import StreamingChunk
from starlette import status
from starlette.responses import StreamingResponse

from app.components.helpers import build_pipeline_input
from app.components.pipelines.rag import rag_pipeline
from app.schemas.vector_search import SearchInput

api_router = APIRouter(prefix="/rag", tags=["Rag Streaming"])

@api_router.post("", status_code=status.HTTP_200_OK)
def rag_post(data: SearchInput):
    """return rag with llm response for a query in real time using streaming"""

    top_k = data.top_k
    query = data.query
    pipeline_input = build_pipeline_input(top_k, query, data.metadata_filters)
    pipeline_input["prompt_builder"] = {"query": query}

    # make llm support streaming, so output will be in real time
    _result_generator = streaming_generator(
            pipeline=rag_pipeline,
            pipeline_run_args=pipeline_input)

    def stream_generator(result_generator: Generator[StreamingChunk, None, None]):
        for result in result_generator:
            yield from result.content

    # on swagger it will wait for full response to be available then show full response
    return StreamingResponse(stream_generator(_result_generator), media_type="text/plain;charset=UTF-8")
