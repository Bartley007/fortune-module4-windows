from fastapi import APIRouter

from app.api.deps import CurrentUserId, DatabaseSession
from app.schemas.common import Envelope, success_envelope
from app.schemas.recommendation import NextActionRequest, RecommendationResult
from app.services.recommendations import recommend_next_actions
from app.services.sessions import get_session_or_404

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/next", response_model=Envelope[RecommendationResult])
def get_next_recommendations(
    payload: NextActionRequest,
    db: DatabaseSession,
    user_id: CurrentUserId,
) -> Envelope[RecommendationResult]:
    session = get_session_or_404(db, user_id, payload.session_id)
    result, source_refs, warnings, _ = recommend_next_actions(db, user_id, payload)
    return success_envelope(
        result,
        system=session.system,
        session_id=payload.session_id,
        source_refs=source_refs,
        warnings=warnings,
    )
