from dataclasses import dataclass
from pathlib import Path

from backend.services.analytics_service import AnalyticsService
from backend.services.catalog_service import CatalogService
from backend.services.intent_classifier import IntentClassifier
from backend.services.knowledge_base import KnowledgeBaseService
from backend.services.recommender import RecommenderService
from backend.services.response_builder import ResponseBuilder
from backend.services.semantic_search import SemanticSearchService


@dataclass
class ServiceRuntime:
    catalog_service: CatalogService
    intent_classifier: IntentClassifier
    semantic_search: SemanticSearchService
    recommender: RecommenderService
    knowledge_base: KnowledgeBaseService
    response_builder: ResponseBuilder
    analytics_service: AnalyticsService


_runtime: ServiceRuntime | None = None


def get_runtime() -> ServiceRuntime:
    global _runtime
    if _runtime is None:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        _runtime = ServiceRuntime(
            catalog_service=CatalogService(data_dir / "products.json"),
            intent_classifier=IntentClassifier(),
            semantic_search=SemanticSearchService(),
            recommender=RecommenderService(),
            knowledge_base=KnowledgeBaseService(data_dir / "policies.json"),
            response_builder=ResponseBuilder(),
            analytics_service=AnalyticsService(data_dir / "copilot_analytics.db"),
        )
    return _runtime
