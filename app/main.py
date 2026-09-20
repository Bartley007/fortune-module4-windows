from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.compat import router as compat_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import init_database
from app.core.errors import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if settings.auto_create_tables:
        init_database()
    yield


app = FastAPI(
    title="Fortune Module 4 API",
    version="0.2.0",
    description=(
        "Personalization, session history, recommendation, similar cases, and personal "
        "knowledge base backend for the fortune-telling project."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(compat_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
