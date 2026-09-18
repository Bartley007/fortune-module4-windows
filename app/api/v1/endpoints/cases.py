from fastapi import APIRouter

from app.api.deps import CurrentUserId, DatabaseSession
from app.schemas.case import SimilarCaseRequest, SimilarCaseResult
from app.schemas.common import Envelope, success_envelope
from app.services.cases import find_similar_cases

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/similar", response_model=Envelope[SimilarCaseResult])
def get_similar_cases(
    payload: SimilarCaseRequest,
    db: DatabaseSession,
    user_id: CurrentUserId,
) -> Envelope[SimilarCaseResult]:
    del user_id
    result = find_similar_cases(
        db,
        payload.features,
        top_k=payload.top_k,
        threshold=payload.threshold,
    )
    return success_envelope(
        result,
        system="bazi" if payload.features.chart_structure else "divination",
        session_id=payload.session_id,
    )
