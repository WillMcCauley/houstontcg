import math
import re
from collections import Counter

from backend.models.schemas import Product


TOKEN_PATTERN = re.compile(r"[a-z0-9\"]+")


class SemanticSearchService:
    def __init__(self) -> None:
        self.synonyms = {
            "pokemon": ["pikachu", "pokemon", "plush", "collectible"],
            "gift": ["gift", "collectible", "lego", "pokemon"],
            "kid": ["kids", "play", "market", "bundle"],
            "kids": ["kids", "play", "market", "bundle"],
            "collectible": ["collectible", "pokemon", "lego", "mtg"],
            "tcg": ["mtg", "magic", "commander", "cards"],
            "marketplace": ["facebook", "listing", "buy"],
            "phone": ["iphone", "electronics", "apple"],
            "bundle": ["bundle", "combo", "together"],
            "magic": ["mtg", "magic", "commander"],
        }

    def _tokenize(self, text: str) -> list[str]:
        return TOKEN_PATTERN.findall(text.lower())

    def _expand_tokens(self, tokens: list[str]) -> list[str]:
        expanded: list[str] = []
        for token in tokens:
            expanded.append(token)
            expanded.extend(self.synonyms.get(token, []))
        return expanded

    def _product_vector(self, product: Product) -> Counter[str]:
        weighted_text = []
        weighted_text.extend([product.title] * 3)
        weighted_text.extend([product.category] * 2)
        weighted_text.extend(product.tags * 2)
        weighted_text.extend(product.keywords * 2)
        weighted_text.append(product.description)
        weighted_text.append(" ".join(product.bundle_options))
        tokens = self._expand_tokens(self._tokenize(" ".join(weighted_text)))
        return Counter(tokens)

    def _query_vector(self, query: str) -> Counter[str]:
        tokens = self._expand_tokens(self._tokenize(query))
        return Counter(tokens)

    def _cosine_similarity(self, left: Counter[str], right: Counter[str]) -> float:
        if not left or not right:
            return 0.0

        dot = sum(left[token] * right[token] for token in set(left) & set(right))
        left_mag = math.sqrt(sum(value * value for value in left.values()))
        right_mag = math.sqrt(sum(value * value for value in right.values()))
        if not left_mag or not right_mag:
            return 0.0
        return dot / (left_mag * right_mag)

    def search_products(
        self,
        query: str,
        products: list[Product],
        limit: int = 3,
    ) -> list[dict]:
        query_vector = self._query_vector(query)
        query_tokens = set(query_vector)
        results = []

        for product in products:
            product_vector = self._product_vector(product)
            similarity = self._cosine_similarity(query_vector, product_vector)
            matched_terms = sorted(query_tokens & set(product_vector))
            phrase_bonus = 0.08 if product.title.lower() in query.lower() else 0.0
            category_bonus = 0.05 if product.category.lower() in query.lower() else 0.0
            bundle_bonus = 0.07 if "bundle" in query.lower() and product.category == "Bundle" else 0.0
            final_score = similarity + phrase_bonus + category_bonus + bundle_bonus

            if final_score <= 0.01:
                continue

            explanation = (
                "Matched on semantic overlap"
                if matched_terms
                else "Matched on category and description similarity"
            )
            results.append(
                {
                    "product": product,
                    "score": round(final_score, 3),
                    "matched_terms": matched_terms[:6],
                    "explanation": explanation,
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]
