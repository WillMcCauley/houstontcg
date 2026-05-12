import json
from pathlib import Path

from backend.services.runtime import get_runtime


def main() -> None:
    runtime = get_runtime()
    eval_path = Path(__file__).resolve().parent.parent / "data" / "eval_prompts.json"
    prompts = json.loads(eval_path.read_text())

    intent_correct = 0
    retrieval_correct = 0
    fallback_count = 0
    rows = []

    for item in prompts:
        query = item["query"]
        expected_intent = item["expected_intent"]
        expected_product_ids = item["expected_product_ids"]

        intent_result = runtime.intent_classifier.classify(query)
        search_results = runtime.semantic_search.search_products(
            query,
            runtime.catalog_service.get_products(),
            limit=3,
        )
        retrieved_ids = [result["product"].id for result in search_results]

        intent_hit = intent_result.intent == expected_intent
        retrieval_hit = not expected_product_ids or any(
            product_id in retrieved_ids for product_id in expected_product_ids
        )

        intent_correct += int(intent_hit)
        retrieval_correct += int(retrieval_hit)
        fallback_count += int(intent_result.intent == "fallback")

        rows.append(
            {
                "query": query,
                "predicted_intent": intent_result.intent,
                "expected_intent": expected_intent,
                "intent_hit": intent_hit,
                "retrieved_ids": retrieved_ids,
                "expected_product_ids": expected_product_ids,
                "retrieval_hit": retrieval_hit,
            }
        )

    total = len(prompts)
    summary = {
        "total_prompts": total,
        "intent_accuracy": round(intent_correct / total, 3),
        "retrieval_success_at_3": round(retrieval_correct / total, 3),
        "fallback_rate": round(fallback_count / total, 3),
        "results": rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
