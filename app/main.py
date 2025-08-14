# Entry point for FastAPI app
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import Depends

from app.db import init_db
from app.exceptions import ResourceConflict, ResourceNotFound
from app.routes import knowledge_base_router, knowledge_base_resources_router
from app.deps import verify_api_key
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, dependencies=[Depends(verify_api_key)])

# setup rate limiter for 10/minute
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Register exception handlers
@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: ResourceNotFound):
    return JSONResponse(status_code=404, content={"error": str(exc)})

@app.exception_handler(ResourceConflict)
async def resource_conflict_handler(request: Request, exc: ResourceConflict):
    return JSONResponse(status_code=409, content={"error": str(exc)})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

app.include_router(knowledge_base_router, prefix="/knowledge-base", tags=["Knowledge Base"])
app.include_router(knowledge_base_resources_router, prefix="/knowledge-base-resources", tags=["Knowledge Base Resources"])
