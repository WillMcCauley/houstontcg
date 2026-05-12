from dataclasses import dataclass
import re


@dataclass
class IntentResult:
    intent: str
    confidence: float
    matched_rules: list[str]


class IntentClassifier:
    def __init__(self) -> None:
        self.product_entities = {
            "mtg",
            "magic",
            "commander",
            "pokemon",
            "pikachu",
            "lego",
            "iphone",
            "phone",
            "bundle",
            "kidkraft",
            "market",
            "stand",
            "collectible",
            "plush",
        }
        self.intent_rules = {
            "greeting": {
                "keywords": ["hi", "hello", "hey", "good morning", "good afternoon"],
                "weight": 1.0,
            },
            "product_search": {
                "keywords": [
                    "show me",
                    "looking for",
                    "find",
                    "search",
                    "what do you have",
                    "what do you sell",
                    "what items",
                    "what listings",
                    "inventory",
                    "item",
                    "listing",
                    "for sale",
                ],
                "weight": 0.95,
            },
            "recommendation": {
                "keywords": [
                    "recommend",
                    "best",
                    "gift",
                    "similar",
                    "suggest",
                    "good for",
                    "what should i get",
                    "collector",
                    "fan",
                    "birthday",
                    "display",
                    "something for",
                ],
                "weight": 0.98,
            },
            "bundle_inquiry": {
                "keywords": ["bundle", "combo", "pair", "together", "multiple items"],
                "weight": 0.96,
            },
            "availability": {
                "keywords": ["available", "still have", "in stock", "gone yet", "still got"],
                "weight": 0.94,
            },
            "shipping_pickup": {
                "keywords": [
                    "shipping",
                    "ship",
                    "pickup",
                    "meet",
                    "local",
                    "deliver",
                    "delivery",
                ],
                "weight": 0.95,
            },
            "payment": {
                "keywords": ["payment", "pay", "cash", "zelle", "cash app", "venmo"],
                "weight": 0.94,
            },
            "purchase_help": {
                "keywords": [
                    "buy",
                    "purchase",
                    "checkout",
                    "check out",
                    "how do i buy",
                    "facebook marketplace",
                    "link",
                    "message seller",
                ],
                "weight": 0.97,
            },
            "general_help": {
                "keywords": [
                    "help",
                    "support",
                    "question",
                    "how does this work",
                    "contact",
                    "message you",
                    "choosing",
                    "shop",
                ],
                "weight": 0.85,
            },
        }

    def classify(self, message: str) -> IntentResult:
        normalized = message.lower().strip()
        raw_tokens = re.findall(r"[a-z0-9]+", normalized)
        tokens = set(raw_tokens)
        singular_tokens = {token[:-1] for token in tokens if token.endswith("s") and len(token) > 3}
        tokens |= singular_tokens
        if not normalized:
            return IntentResult(intent="fallback", confidence=0.15, matched_rules=[])

        if normalized.startswith(("hi", "hello", "hey")):
            return IntentResult(intent="greeting", confidence=0.96, matched_rules=["leading_greeting"])

        scores: dict[str, float] = {}
        matched_rules: dict[str, list[str]] = {}

        for intent, config in self.intent_rules.items():
            for keyword in config["keywords"]:
                if self._matches(keyword, normalized, tokens):
                    scores[intent] = scores.get(intent, 0.0) + config["weight"]
                    matched_rules.setdefault(intent, []).append(keyword)

        if tokens & self.product_entities:
            scores["product_search"] = scores.get("product_search", 0.0) + 0.45
            matched_rules.setdefault("product_search", []).append("product_entity")

        if {"best", "gift", "recommend", "similar"} & tokens:
            scores["recommendation"] = scores.get("recommendation", 0.0) + 0.4
            matched_rules.setdefault("recommendation", []).append("recommendation_bias")

        if {"bundle", "combo", "pair", "together"} & tokens:
            scores["bundle_inquiry"] = scores.get("bundle_inquiry", 0.0) + 0.55
            matched_rules.setdefault("bundle_inquiry", []).append("bundle_bias")

        if {"available", "still", "stock"} & tokens:
            scores["availability"] = scores.get("availability", 0.0) + 0.45
            matched_rules.setdefault("availability", []).append("availability_bias")

        if {"ship", "shipping", "pickup", "deliver", "delivery"} & tokens:
            scores["shipping_pickup"] = scores.get("shipping_pickup", 0.0) + 0.45
            matched_rules.setdefault("shipping_pickup", []).append("shipping_pickup_bias")

        if {"search", "find", "show", "listing", "inventory"} & tokens:
            scores["product_search"] = scores.get("product_search", 0.0) + 0.45
            matched_rules.setdefault("product_search", []).append("product_search_bias")

        if not scores:
            fallback_confidence = 0.45 if len(normalized.split()) >= 3 else 0.25
            return IntentResult(intent="fallback", confidence=fallback_confidence, matched_rules=[])

        best_intent = max(scores, key=scores.get)
        total_score = sum(scores.values()) or 1.0
        confidence = min(0.99, max(0.35, scores[best_intent] / total_score))

        if scores.get("availability", 0.0) >= scores.get("bundle_inquiry", 0.0) and any(
            token in tokens for token in ["available", "still", "stock", "got"]
        ):
            best_intent = "availability"
            confidence = max(confidence, 0.8)

        if scores.get("shipping_pickup", 0.0) and scores.get("general_help", 0.0) and "pickup" in tokens:
            best_intent = "shipping_pickup"
            confidence = max(confidence, 0.8)

        if best_intent == "product_search" and (
            {"best", "recommend", "gift", "similar", "collector", "display"} & tokens
            or "something for" in normalized
            or ("collectible" in tokens and "not" in tokens)
        ):
            best_intent = "recommendation"
            confidence = max(confidence, 0.78)

        return IntentResult(
            intent=best_intent,
            confidence=round(confidence, 3),
            matched_rules=matched_rules.get(best_intent, []),
        )

    def _matches(self, keyword: str, normalized: str, tokens: set[str]) -> bool:
        if " " in keyword:
            return keyword in normalized
        return keyword in tokens
