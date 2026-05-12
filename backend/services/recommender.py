from backend.models.schemas import Product


class RecommenderService:
    def recommend(
        self,
        query: str,
        intent: str,
        search_results: list[dict],
        products: list[Product],
        limit: int = 3,
    ) -> list[dict]:
        lowered_query = query.lower()
        search_scores = {item["product"].id: item["score"] for item in search_results}
        catalog = search_results if search_results else [{"product": product, "score": 0.0} for product in products]
        recommendations = []

        for item in catalog:
            product = item["product"]
            score = item["score"]
            reasons: list[str] = []

            if "pokemon" in lowered_query and "pokemon" in product.tags:
                score += 0.22
                reasons.append("matches Pokemon interest")
            if "gift" in lowered_query and any(tag in product.tags for tag in ["collectible", "lego", "pokemon"]):
                score += 0.16
                reasons.append("works well as a giftable collectible")
            if any(term in lowered_query for term in ["kid", "kids", "child"]) and any(
                tag in product.tags for tag in ["kids", "play"]
            ):
                score += 0.2
                reasons.append("fits a kids-focused request")
            if "collectible" in lowered_query and "collectible" in product.tags:
                score += 0.17
                reasons.append("lines up with collectible interest")
            if "bundle" in lowered_query and product.category == "Bundle":
                score += 0.24
                reasons.append("directly matches bundle intent")
            if "iphone" in lowered_query and product.category == "Electronics":
                score += 0.22
                reasons.append("matches electronics interest")
            if any(term in lowered_query for term in ["mtg", "magic", "commander", "tcg"]) and (
                "commander" in product.tags or product.category == "MTG"
            ):
                score += 0.24
                reasons.append("fits trading card / MTG interest")
            if intent == "recommendation":
                score += 0.1
                reasons.append("prioritized for recommendation-style question")
            if product.id in search_scores:
                reasons.append("surfaced by semantic search")

            if not reasons and score > 0:
                reasons.append("close match on product description and tags")

            recommendations.append(
                {
                    "product": product,
                    "score": round(score, 3),
                    "reason": ", ".join(dict.fromkeys(reasons)),
                }
            )

        recommendations.sort(key=lambda item: item["score"], reverse=True)
        return recommendations[:limit]
