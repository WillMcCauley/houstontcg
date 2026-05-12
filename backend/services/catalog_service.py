import json
from pathlib import Path

from backend.models.schemas import Product


class CatalogService:
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self._products = self._load_products()

    def _load_products(self) -> list[Product]:
        raw_products = json.loads(self.data_path.read_text())
        return [Product(**item) for item in raw_products]

    def reload(self) -> list[Product]:
        self._products = self._load_products()
        return self._products

    def get_products(self) -> list[Product]:
        return self._products

    def get_product(self, product_id: str) -> Product | None:
        return next((product for product in self._products if product.id == product_id), None)
