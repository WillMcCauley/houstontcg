import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


class AnalyticsService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    raw_query TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    response_type TEXT NOT NULL,
                    fallback INTEGER NOT NULL,
                    matched_products TEXT NOT NULL,
                    recommended_products TEXT NOT NULL,
                    policy_hits TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    product_id TEXT,
                    metadata TEXT NOT NULL
                )
                """
            )

    def log_interaction(
        self,
        session_id: str,
        raw_query: str,
        intent: str,
        confidence: float,
        response_type: str,
        fallback: bool,
        matched_products: list[str],
        recommended_products: list[str],
        policy_hits: list[str],
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO interactions (
                    timestamp,
                    session_id,
                    raw_query,
                    intent,
                    confidence,
                    response_type,
                    fallback,
                    matched_products,
                    recommended_products,
                    policy_hits
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    session_id,
                    raw_query,
                    intent,
                    confidence,
                    response_type,
                    int(fallback),
                    json.dumps(matched_products),
                    json.dumps(recommended_products),
                    json.dumps(policy_hits),
                ),
            )
            return int(cursor.lastrowid)

    def log_feedback(
        self,
        session_id: str,
        event_type: str,
        product_id: str | None,
        metadata: dict,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO feedback (
                    timestamp,
                    session_id,
                    event_type,
                    product_id,
                    metadata
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    session_id,
                    event_type,
                    product_id,
                    json.dumps(metadata),
                ),
            )
            return int(cursor.lastrowid)

    def get_summary(self) -> dict:
        with self._connect() as connection:
            interaction_rows = connection.execute(
                """
                SELECT intent, fallback, response_type, matched_products, recommended_products
                FROM interactions
                """
            ).fetchall()
            feedback_rows = connection.execute(
                "SELECT event_type, product_id FROM feedback"
            ).fetchall()

        total_interactions = len(interaction_rows)
        intent_counter = Counter()
        product_counter = Counter()
        category_counter = Counter()
        feedback_counter = Counter()
        fallback_count = 0
        recommendation_count = 0

        for intent, fallback, response_type, matched_json, recommended_json in interaction_rows:
            intent_counter[intent] += 1
            fallback_count += int(fallback)
            if response_type == "recommendation":
                recommendation_count += 1

            matched_products = json.loads(matched_json)
            recommended_products = json.loads(recommended_json)
            for product_id in matched_products + recommended_products:
                product_counter[product_id] += 1
                if product_id.startswith("iphone"):
                    category_counter["Electronics"] += 1
                elif product_id.startswith("lego"):
                    category_counter["Lego"] += 1
                elif product_id.startswith("kidkraft"):
                    category_counter["Kids"] += 1
                elif "pikachu" in product_id:
                    category_counter["Collectibles / Bundle"] += 1
                elif "outlaws" in product_id:
                    category_counter["MTG"] += 1

        for event_type, product_id in feedback_rows:
            feedback_counter[event_type] += 1
            if product_id:
                product_counter[product_id] += 1

        fallback_rate = round((fallback_count / total_interactions) if total_interactions else 0.0, 3)
        recommendation_frequency = round(
            (recommendation_count / total_interactions) if total_interactions else 0.0,
            3,
        )

        def top_items(counter: Counter, limit: int = 5) -> list[dict]:
            return [{"name": name, "count": count} for name, count in counter.most_common(limit)]

        return {
            "total_interactions": total_interactions,
            "top_customer_intents": top_items(intent_counter),
            "most_requested_products": top_items(product_counter),
            "top_categories": top_items(category_counter),
            "fallback_rate": fallback_rate,
            "recommendation_frequency": recommendation_frequency,
            "feedback_events": top_items(feedback_counter),
        }
