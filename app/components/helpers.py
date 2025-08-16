from app.schemas.vector_search import SourceMetadata


def build_pipeline_input(top_k: int, query: str, metadata_filters: SourceMetadata = None):
    """
    Builds the pipeline_input dict and retriever_params based on top_k, query, and metadata_filters.
    :param top_k: int or None
    :param query: str
    :param metadata_filters: object with model_dump() method or None
    :return: dict pipeline_input
    """
    # build retriever filters https://haystack.deepset.ai/tutorials/31_metadata_filtering
    conditions = []
    if metadata_filters is not None:
        for key, value in metadata_filters.model_dump().items():
            field = f"meta.{key}"
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
    return pipeline_input