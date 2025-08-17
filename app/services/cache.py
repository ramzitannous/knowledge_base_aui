from typing import Any, Callable, Dict, Optional, Tuple

from beanie import PydanticObjectId
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.key_builder import default_key_builder
from redis import asyncio as aioredis
from starlette.requests import Request
from starlette.responses import Response

from app.config import app_config

GET_ONE_CACHE_KEY = "get_one"

def init_cache():
    redis = aioredis.from_url(app_config.REDIS_URI)
    FastAPICache.init(RedisBackend(redis),
                      prefix="fastapi-cache",
                      expire=app_config.CACHE_TTL)

def get_one_cache_key(
        namespace: str,
        _id: PydanticObjectId
    ):
    if namespace is None:
        namespace = ""
    return f"{namespace}:{GET_ONE_CACHE_KEY}_{str(_id)}"

"""custom cache key builder to control when to invalidate cache"""
def build_get_one_cache_key(
        func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any]) -> str:
    _id = list(kwargs.values())[0] if kwargs.values() else None
    if _id and isinstance(_id, PydanticObjectId):
        return get_one_cache_key(namespace, _id)
    return default_key_builder(func, namespace,
                               request=request,
                               response=response,
                               args=args,
                               kwargs=kwargs)
