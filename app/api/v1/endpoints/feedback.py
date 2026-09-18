from fastapi import APIRouter

from app.api.deps import CurrentUserId, DatabaseSession
from app.schemas.common import Envelope, success_envelope
from app.schemas.feedback import FeedbackCreate, FeedbackOut
from app.services.feedback import create_feedback, feedback_to_schema
from app.services.sessions import get_session_or_404

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=Envelope[FeedbackOut])
def submit_feedback(
    payload: FeedbackCreate,
    db: DatabaseSession,
    user_id: CurrentUserId,
) -> Envelope[FeedbackOut]:
    record = create_feedback(db, user_id, payload)
    system = "unknown"
    if record.session_id:
        system = get_session_or_404(db, user_id, record.session_id).system
    return success_envelope(
        feedback_to_schema(record),
        system=system,
        session_id=record.session_id,
        source_refs=record.source_refs,
    )
