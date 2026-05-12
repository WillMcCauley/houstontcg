from fastapi import APIRouter

from backend.models.schemas import ProductCatalogResponse
from backend.services.runtime import get_runtime


router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductCatalogResponse)
def list_products() -> ProductCatalogResponse:
    runtime = get_runtime()
    products = runtime.catalog_service.get_products()
    return ProductCatalogResponse(products=products, count=len(products))
