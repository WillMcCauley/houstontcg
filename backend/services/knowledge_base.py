import json
import re
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class KnowledgeBaseService:
    def __init__(self, data_path: Path) -> None:
        raw = json.loads(data_path.read_text())
        self.store_profile = raw["store_profile"]
        self.prompt_templates = raw["prompt_templates"]
        self.knowledge = raw["knowledge"]

    def get_store_profile(self) -> dict:
        return self.store_profile

    def get_prompt_templates(self) -> dict:
        return self.prompt_templates

    def retrieve(self, query: str, intent: str, limit: int = 2) -> list[dict]:
        query_tokens = set(TOKEN_PATTERN.findall(query.lower()))
        ranked = []

        intent_topic_map = {
            "shipping_pickup": {"pickup", "shipping"},
            "payment": {"payment"},
            "purchase_help": {"marketplace", "purchase"},
            "bundle_inquiry": {"bundle"},
            "general_help": {"support"},
            "availability": {"availability"},
        }
        preferred_topics = intent_topic_map.get(intent, set())

        for item in self.knowledge:
            score = 0.0
            tags = set(item["tags"])
            topic = item["topic"]
            content_tokens = set(TOKEN_PATTERN.findall(item["content"].lower()))
            score += len(query_tokens & tags) * 0.35
            score += len(query_tokens & content_tokens) * 0.08
            if topic in preferred_topics:
                score += 0.35
            if score > 0:
                ranked.append(
                    {
                        "id": item["id"],
                        "title": item["title"],
                        "topic": topic,
                        "content": item["content"],
                        "score": round(score, 3),
                    }
                )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]
