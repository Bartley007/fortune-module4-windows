from fastapi import APIRouter

from app.api.deps import CurrentUserId, DatabaseSession
from app.schemas.common import Envelope, success_envelope
from app.schemas.event import EventOut
from app.schemas.session import SessionCreateRequest, SessionCreateResult
from app.services.events import event_to_schema, list_session_events
from app.services.sessions import (
    create_or_resume_session,
    get_session_or_404,
    session_to_schema,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=Envelope[SessionCreateResult])
def create_session(
    payload: SessionCreateRequest,
    db: DatabaseSession,
    user_id: CurrentUserId,
) -> Envelope[SessionCreateResult]:
    record, resumed = create_or_resume_session(db, user_id, payload)
    session = session_to_schema(record)
    return success_envelope(
        SessionCreateResult(session=session, resumed=resumed),
        system=record.system,
        session_id=record.id,
    )


@router.get("/{session_id}/events", response_model=Envelope[list[EventOut]])
def get_session_events(
    session_id: str,
    db: DatabaseSession,
    user_id: CurrentUserId,
) -> Envelope[list[EventOut]]:
    session = get_session_or_404(db, user_id, session_id)
    events = [event_to_schema(record) for record in list_session_events(db, session_id)]
    source_refs = sorted({ref for event in events for ref in event.source_refs})
    return success_envelope(
        events,
        system=session.system,
        session_id=session_id,
        source_refs=source_refs,
    )
