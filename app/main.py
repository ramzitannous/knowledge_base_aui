# Entry point for FastAPI app
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import ResourceConflict, ResourceNotFound
from fastapi import FastAPI
from app.routes import router as knowledge_base_router
from app.db import init_db
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
app = FastAPI(lifespan=lifespan)

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
