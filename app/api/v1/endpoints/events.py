from typing import Annotated

from fastapi import APIRouter, Header

from app.api.deps import CurrentUserId, DatabaseSession
from app.schemas.common import Envelope, success_envelope
from app.schemas.event import EventIngestRequest, EventIngestResult
from app.services.events import event_to_schema, ingest_event

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest", response_model=Envelope[EventIngestResult])
def ingest_session_event(
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
    event = event_to_schema(record)
    return success_envelope(
        EventIngestResult(event=event, duplicate=duplicate, idempotency_key=effective_key),
        system=record.system,
        session_id=record.session_id,
        source_refs=record.source_refs,
    )
