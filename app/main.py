from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import CurrentUserId, DatabaseSession
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import init_database
from app.core.errors import register_exception_handlers
from app.schemas.common import Envelope, success_envelope
from app.schemas.event import EventIngestRequest, EventIngestResult
from app.services.events import event_to_schema, ingest_event

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if settings.auto_create_tables:
        init_database()
    yield


app = FastAPI(
    title="Fortune Module 4 API",
    version="0.1.0",
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


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/session/event", response_model=Envelope[EventIngestResult], include_in_schema=False)
def compatibility_ingest_event(
    payload: EventIngestRequest,
    db: DatabaseSession,
    user_id: CurrentUserId,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
) -> Envelope[EventIngestResult]:
    record, duplicate, effective_key = ingest_event(
        db=db,
        user_id=user_id,
        payload=payload,
        idempotency_key=idempotency_key,
    )
    return success_envelope(
        EventIngestResult(
            event=event_to_schema(record),
            duplicate=duplicate,
            idempotency_key=effective_key,
        ),
        system=record.system,
        session_id=record.session_id,
        source_refs=record.source_refs,
    )
