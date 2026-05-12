import uuid

from fastapi import APIRouter

from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.runtime import get_runtime


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    runtime = get_runtime()
    session_id = request.session_id or str(uuid.uuid4())

    intent_result = runtime.intent_classifier.classify(request.message)
    search_results = runtime.semantic_search.search_products(
        request.message,
        runtime.catalog_service.get_products(),
        limit=request.limit,
    )
    recommendations = runtime.recommender.recommend(
        query=request.message,
        intent=intent_result.intent,
        search_results=search_results,
        products=runtime.catalog_service.get_products(),
        limit=request.limit,
    )
    policy_hits = runtime.knowledge_base.retrieve(
        request.message,
        intent=intent_result.intent,
        limit=2,
    )

    response_payload = runtime.response_builder.build_chat_response(
        query=request.message,
        session_id=session_id,
        intent_result=intent_result,
        search_results=search_results,
        recommendations=recommendations,
        policy_hits=policy_hits,
        store_profile=runtime.knowledge_base.get_store_profile(),
    )

    analytics_id = runtime.analytics_service.log_interaction(
        session_id=session_id,
        raw_query=request.message,
        intent=intent_result.intent,
        confidence=intent_result.confidence,
        response_type=response_payload["response_type"],
        fallback=response_payload["fallback"],
        matched_products=[result["product"].id for result in search_results],
        recommended_products=[item["product"].id for item in recommendations],
        policy_hits=[item["id"] for item in policy_hits],
    )
    response_payload["analytics_id"] = analytics_id

    return ChatResponse(**response_payload)
