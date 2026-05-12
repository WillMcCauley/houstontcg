from fastapi import APIRouter

from backend.models.schemas import AnalyticsSummaryResponse, SearchRequest, SearchResponse
from backend.services.runtime import get_runtime


router = APIRouter(prefix="/api", tags=["analytics", "search"])


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary() -> AnalyticsSummaryResponse:
    runtime = get_runtime()
    return AnalyticsSummaryResponse(**runtime.analytics_service.get_summary())


@router.post("/search", response_model=SearchResponse)
def semantic_search(request: SearchRequest) -> SearchResponse:
    runtime = get_runtime()
    search_results = runtime.semantic_search.search_products(
        request.query,
        runtime.catalog_service.get_products(),
        limit=request.limit,
    )
    recommendations = runtime.recommender.recommend(
        query=request.query,
        intent="recommendation",
        search_results=search_results,
        products=runtime.catalog_service.get_products(),
        limit=request.limit,
    )
    return SearchResponse(
        query=request.query,
        results=search_results,
        recommendations=recommendations,
    )
