from fastapi import APIRouter

from backend.models.schemas import FeedbackRequest, FeedbackResponse
from backend.services.runtime import get_runtime


router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    runtime = get_runtime()
    feedback_id = runtime.analytics_service.log_feedback(
        session_id=request.session_id,
        event_type=request.event_type,
        product_id=request.product_id,
        metadata=request.metadata,
    )
    return FeedbackResponse(status="ok", feedback_id=feedback_id)
