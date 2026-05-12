from typing import Any

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    title: str
    category: str
    description: str
    tags: list[str]
    keywords: list[str]
    price: str | None = None
    listing_url: str
    image_url: str
    availability: str
    bundle_options: list[str] = Field(default_factory=list)


class ProductCatalogResponse(BaseModel):
    products: list[Product]
    count: int


class PolicyHit(BaseModel):
    id: str
    title: str
    topic: str
    content: str
    score: float


class SearchResult(BaseModel):
    product: Product
    score: float
    matched_terms: list[str]
    explanation: str


class RecommendedProduct(BaseModel):
    product: Product
    score: float
    reason: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    limit: int = 3


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    confidence: float
    answer: str
    next_action: str
    response_type: str
    products: list[RecommendedProduct | SearchResult]
    policy_hits: list[PolicyHit]
    recommendation_reasons: list[str]
    fallback: bool
    analytics_id: int | None = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 3


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    recommendations: list[RecommendedProduct]


class FeedbackRequest(BaseModel):
    session_id: str
    event_type: str
    product_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: int | None = None


class MetricItem(BaseModel):
    name: str
    count: int


class AnalyticsSummaryResponse(BaseModel):
    total_interactions: int
    top_customer_intents: list[MetricItem]
    most_requested_products: list[MetricItem]
    top_categories: list[MetricItem]
    fallback_rate: float
    recommendation_frequency: float
    feedback_events: list[MetricItem]
